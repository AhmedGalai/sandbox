import asyncio
import base64
import json
import os
import threading
import queue
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

import aiohttp
import mss
from PIL import Image

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser


# ---------------------------------------------------------------------
# OLLAMA CONFIG
# ---------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
EMBED_URL = f"{OLLAMA_BASE_URL}/api/embed"

MODEL_PLANNER = "qwen3:latest"
MODEL_CRITIC = "qwen3:latest"
MODEL_VISION = "granite3.2-vision:latest"
MODEL_EMBED = "mxbai-embed-large:latest"

CAPTURE_DIR = "captures"


# ---------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------
@dataclass
class Observation:
    frame_id: int
    text: Optional[str] = None
    image_path: Optional[str] = None


@dataclass
class Action:
    type: str
    args: Dict[str, Any]


@dataclass
class ToolResult:
    tool: str
    ok: bool
    payload: Dict[str, Any]


@dataclass
class Feedback:
    score: float
    comment: str


@dataclass
class AgentConfig:
    system_purpose: str
    region_x: int
    region_y: int
    region_w: int
    region_h: int
    frame_interval: float = 3.0
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    confirm_enabled: bool = True
    overlay_color: str = "#ff0000"  # default red


# ---------------------------------------------------------------------
# UTILS
# ---------------------------------------------------------------------
def parse_json_loose(raw: str) -> Dict[str, Any]:
    """Try to parse JSON from model output, tolerate fences / extra text."""
    text = raw.strip()

    # Strip ``` fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Try direct JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try substring between first '{' and last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    # Fallback: bundle as text
    return {"fallback_text": raw}


def encode_image_to_b64(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def capture_region_to_file(
    frame_id: int, x: int, y: int, w: int, h: int, directory: str = CAPTURE_DIR
) -> str:
    os.makedirs(directory, exist_ok=True)
    out_path = os.path.join(directory, f"frame_{frame_id}.jpg")

    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": w, "height": h}
        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(out_path, "JPEG", quality=80)

    return out_path


# ---------------------------------------------------------------------
# OLLAMA CALLS
# ---------------------------------------------------------------------
async def ollama_chat(
    session: aiohttp.ClientSession,
    model: str,
    messages: List[Dict[str, Any]],
    stream: bool = False,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    async with session.post(CHAT_URL, json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()
    return data["message"]["content"]


async def ollama_embed(
    session: aiohttp.ClientSession,
    model: str,
    texts: List[str],
) -> List[List[float]]:
    payload = {"model": model, "input": texts}
    async with session.post(EMBED_URL, json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()

    if "embeddings" in data:
        return data["embeddings"]
    if "embedding" in data:  # older single-input format
        return [data["embedding"]]
    raise RuntimeError(f"Unexpected embedding response: {data}")


# ---------------------------------------------------------------------
# TOOLS IMPLEMENTATIONS
# ---------------------------------------------------------------------
async def tool_describe_image(
    session: aiohttp.ClientSession, observation: Observation
) -> ToolResult:
    if not observation.image_path:
        return ToolResult(
            tool="describe_image",
            ok=False,
            payload={"error": "No image_path in observation"},
        )

    try:
        img_b64 = encode_image_to_b64(observation.image_path)
    except Exception as e:
        return ToolResult(
            tool="describe_image",
            ok=False,
            payload={"error": f"Failed to read image: {e}"},
        )

    messages = [
        {
            "role": "user",
            "content": "Describe this screen capture briefly and clearly.",
            "images": [img_b64],
        }
    ]
    try:
        content = await ollama_chat(session, MODEL_VISION, messages)
        return ToolResult(
            tool="describe_image",
            ok=True,
            payload={"description": content},
        )
    except Exception as e:
        return ToolResult(
            tool="describe_image",
            ok=False,
            payload={"error": str(e)},
        )


async def tool_embed_text(
    session: aiohttp.ClientSession, text: str
) -> ToolResult:
    if not text:
        return ToolResult(
            tool="embed_text",
            ok=False,
            payload={"error": "Empty text"},
        )

    try:
        vecs = await ollama_embed(session, MODEL_EMBED, [text])
        emb = vecs[0]
        return ToolResult(
            tool="embed_text",
            ok=True,
            payload={
                "vector_dim": len(emb),
                "first_5_dims": emb[:5],
            },
        )
    except Exception as e:
        return ToolResult(
            tool="embed_text",
            ok=False,
            payload={"error": str(e)},
        )


async def tool_noop(session: aiohttp.ClientSession) -> ToolResult:
    return ToolResult(
        tool="noop",
        ok=True,
        payload={"message": "No action taken"},
    )


async def tool_unknown(name: str, args: Dict[str, Any]) -> ToolResult:
    return ToolResult(
        tool=name,
        ok=False,
        payload={"error": f"Unknown tool '{name}' – treated as noop."},
    )


async def tool_depth_anything(
    session: aiohttp.ClientSession, observation: Observation
) -> ToolResult:
    """
    Call external depth script:
      ..\\ollama_vision\\depth_anything_2.py input.jpg output.jpg

    Assumes the script exists and works like:
      python depth_anything_2.py input.jpg output.jpg
    """
    if not observation.image_path:
        return ToolResult(
            tool="depth_anything",
            ok=False,
            payload={"error": "No image_path in observation"},
        )

    script_path = (
        Path(__file__).parent / ".." / "ollama_vision" / "depth_anything_2.py"
    ).resolve()

    if not script_path.is_file():
        return ToolResult(
            tool="depth_anything",
            ok=False,
            payload={"error": f"Script not found: {script_path}"},
        )

    depth_out = (Path(CAPTURE_DIR) / f"depth_{observation.frame_id}.jpg").resolve()

    # Run in thread so we don't block event loop
    def run_proc():
        return subprocess.run(
            [
                "python",
                str(script_path),
                observation.image_path,
                str(depth_out),
            ],
            capture_output=True,
            text=True,
        )

    try:
        proc = await asyncio.to_thread(run_proc)
        ok = proc.returncode == 0 and depth_out.is_file()
        return ToolResult(
            tool="depth_anything",
            ok=ok,
            payload={
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "depth_image": str(depth_out) if depth_out.is_file() else None,
            },
        )
    except Exception as e:
        return ToolResult(
            tool="depth_anything",
            ok=False,
            payload={"error": str(e)},
        )


async def tool_shell_command(
    session: aiohttp.ClientSession, command: str
) -> ToolResult:
    """
    Run arbitrary shell command, e.g. 'start calc'.
    WARNING: obviously dangerous. Only allow if you trust the model / prompt.
    """
    if not command:
        return ToolResult(
            tool="shell_command",
            ok=False,
            payload={"error": "Empty command"},
        )

    def run_cmd():
        return subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )

    try:
        proc = await asyncio.to_thread(run_cmd)
        return ToolResult(
            tool="shell_command",
            ok=(proc.returncode == 0),
            payload={
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            },
        )
    except Exception as e:
        return ToolResult(
            tool="shell_command",
            ok=False,
            payload={"error": str(e)},
        )


BUILTIN_TOOL_IMPLS = {
    "describe_image": tool_describe_image,
    "embed_text": tool_embed_text,
    "noop": tool_noop,
    "depth_anything": tool_depth_anything,
    "shell_command": tool_shell_command,
}


# ---------------------------------------------------------------------
# PLANNER / CRITIC PROMPTS
# ---------------------------------------------------------------------
def build_planner_system_prompt(
    purpose: str, tools_cfg: Dict[str, Dict[str, Any]]
) -> str:
    lines = []
    lines.append("You are the MAIN AGENT.\n")
    lines.append("Your purpose:")
    lines.append(purpose)
    lines.append("")
    lines.append("At each frame you get:")
    lines.append("- An observation (frame_id, optional text, screen image).")
    lines.append("- Optional feedback about your previous action.")
    lines.append("You must choose ONE tool to call each frame.")
    lines.append("")
    lines.append("AVAILABLE TOOLS:")
    index = 1
    for name, cfg in tools_cfg.items():
        if not cfg.get("enabled", True):
            continue
        desc = cfg.get("description", "").strip()
        arg_spec = cfg.get("arg_spec", "{}")
        lines.append(f'{index}) "{name}"')
        if desc:
            lines.append(f"   - {desc}")
        lines.append(f"   - args: {arg_spec}")
        if cfg.get("confirm", False):
            lines.append("   - NOTE: This tool may require user confirmation.")
        index += 1

    lines.append("")
    lines.append("Respond ONLY in JSON:")
    lines.append("{")
    lines.append('  "action": "<tool_name>",')
    lines.append('  "args": { ... },')
    lines.append('  "explanation": "<short explanation of why you chose this>"')
    lines.append("}")

    return "\n".join(lines)


CRITIC_SYSTEM = """
You are a CRITIC.

Given:
- The main agent's purpose.
- The current observation.
- The action the agent chose.
- The tool result.

You must evaluate the action and return a feedback signal:
- score: float in [0, 1] (1 = excellent, 0 = terrible)
- comment: short explanation

Respond ONLY in JSON:
{
  "score": <float between 0 and 1>,
  "comment": "<short explanation>"
}
""".strip()


# ---------------------------------------------------------------------
# PLANNER / CRITIC LOGIC
# ---------------------------------------------------------------------
async def plan_action(
    session: aiohttp.ClientSession,
    planner_system: str,
    observation: Observation,
    last_feedback: Optional[Feedback],
) -> Action:
    obs_text_parts = [f"frame_id={observation.frame_id}"]
    if observation.text:
        obs_text_parts.append(f"text={observation.text!r}")
    if observation.image_path:
        obs_text_parts.append(f"image_path={observation.image_path!r}")
    obs_summary = "; ".join(obs_text_parts)

    feedback_str = (
        f"score={last_feedback.score}, comment={last_feedback.comment!r}"
        if last_feedback
        else "None"
    )

    messages = [
        {
            "role": "system",
            "content": planner_system,
        },
        {
            "role": "user",
            "content": (
                "Current observation:\n"
                f"{obs_summary}\n\n"
                "Last feedback (if any):\n"
                f"{feedback_str}\n\n"
                "Decide the best action now."
            ),
        },
    ]

    raw_content = await ollama_chat(session, MODEL_PLANNER, messages)
    parsed = parse_json_loose(raw_content)

    action_name = parsed.get("action", "noop")
    args = parsed.get("args", {}) or {}

    return Action(type=action_name, args=args)


async def evaluate_action(
    session: aiohttp.ClientSession,
    system_purpose: str,
    observation: Observation,
    action: Action,
    tool_result: ToolResult,
) -> Feedback:
    obs_parts = [f"frame_id={observation.frame_id}"]
    if observation.text:
        obs_parts.append(f"text={observation.text!r}")
    if observation.image_path:
        obs_parts.append(f"image_path={observation.image_path!r}")
    obs_summary = "; ".join(obs_parts)

    messages = [
        {"role": "system", "content": CRITIC_SYSTEM},
        {
            "role": "user",
            "content": (
                f"AGENT PURPOSE:\n{system_purpose}\n\n"
                f"OBSERVATION:\n{obs_summary}\n\n"
                f"ACTION:\n{json.dumps({'type': action.type, 'args': action.args}, indent=2)}\n\n"
                f"TOOL RESULT:\n{json.dumps(tool_result.payload, indent=2)}\n\n"
                "Evaluate the action."
            ),
        },
    ]

    raw = await ollama_chat(session, MODEL_CRITIC, messages)
    parsed = parse_json_loose(raw)

    try:
        score = float(parsed.get("score", 0.0))
    except Exception:
        score = 0.0
    comment = str(parsed.get("comment", ""))
    score = max(0.0, min(1.0, score))

    return Feedback(score=score, comment=comment)


# ---------------------------------------------------------------------
# AGENT RUNNER (ASYNC IN BACKGROUND THREAD)
# ---------------------------------------------------------------------
class AgentRunner:
    def __init__(self, config: AgentConfig, log_cb: Callable[[str], None]):
        self.config = config
        self.log_cb = log_cb
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    def log(self, msg: str) -> None:
        if self.log_cb:
            self.log_cb(msg)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.is_running():
            self.log("Agent is already running.")
            return
        self._stop_event.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        self._thread.start()
        self.log("Agent thread started.")

    def pause(self):
        if not self.is_running():
            self.log("Agent is not running.")
            return
        self._pause_event.set()
        self.log("Agent paused.")

    def resume(self):
        if not self.is_running():
            self.log("Agent is not running.")
            return
        if self._pause_event.is_set():
            self._pause_event.clear()
            self.log("Agent resumed.")

    def stop(self):
        if not self.is_running():
            self.log("Agent is not running.")
            return
        self._stop_event.set()
        self._pause_event.clear()
        self.log("Stopping agent...")
        if self._thread:
            self._thread.join(timeout=5.0)
        self.log("Agent stopped.")

    def _thread_main(self):
        asyncio.run(self._async_main())

    async def _async_main(self):
        async with aiohttp.ClientSession() as session:
            last_feedback: Optional[Feedback] = None
            frame_id = 0
            self.log("Agent main loop started.")

            try:
                while not self._stop_event.is_set():
                    # Handle pause
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        await asyncio.sleep(0.2)
                    if self._stop_event.is_set():
                        break

                    # Capture screen region
                    x = self.config.region_x
                    y = self.config.region_y
                    w = self.config.region_w
                    h = self.config.region_h
                    image_path = capture_region_to_file(frame_id, x, y, w, h)
                    obs_text = f"Screen capture frame {frame_id}"
                    obs = Observation(frame_id=frame_id, text=obs_text, image_path=image_path)

                    self.log(f"\n=== FRAME {frame_id} ===")
                    self.log(f"Captured region x={x}, y={y}, w={w}, h={h} -> {image_path}")

                    # Build planner system prompt from current tools
                    planner_system = build_planner_system_prompt(
                        self.config.system_purpose, self.config.tools
                    )

                    # Plan
                    action = await plan_action(session, planner_system, obs, last_feedback)
                    self.log(f"Planned action: {action.type}, args={action.args}")

                    # Execute action (with optional confirmation)
                    tools_cfg = self.config.tools
                    tool_cfg = tools_cfg.get(action.type)
                    if not tool_cfg or not tool_cfg.get("enabled", True):
                        tool_result = await tool_unknown(action.type, action.args)
                    else:
                        # Confirmation handling
                        if self.config.confirm_enabled and tool_cfg.get("confirm", False):
                            # Note: calling messagebox from a non-main thread
                            # is not ideal but generally works on Windows.
                            answer = messagebox.askyesno(
                                "Confirm tool",
                                f"Tool: {action.type}\nArgs: {action.args}\n\nRun this tool?",
                            )
                            if not answer:
                                self.log(f"Tool '{action.type}' cancelled by user.")
                                tool_result = await tool_noop(session)
                                # Still send this to critic
                            else:
                                tool_result = await self._run_tool_impl(
                                    session, action, obs
                                )
                        else:
                            tool_result = await self._run_tool_impl(session, action, obs)

                    self.log(f"Tool result: ok={tool_result.ok}, payload={tool_result.payload}")

                    # Critic feedback
                    feedback = await evaluate_action(
                        session=session,
                        system_purpose=self.config.system_purpose,
                        observation=obs,
                        action=action,
                        tool_result=tool_result,
                    )
                    last_feedback = feedback
                    self.log(f"Feedback: score={feedback.score:.2f}, comment={feedback.comment}")

                    frame_id += 1
                    await asyncio.sleep(self.config.frame_interval)

            except Exception as e:
                self.log(f"Agent loop error: {e!r}")
            finally:
                self.log("Agent main loop finished.")

    async def _run_tool_impl(
        self,
        session: aiohttp.ClientSession,
        action: Action,
        obs: Observation,
    ) -> ToolResult:
        impl = BUILTIN_TOOL_IMPLS.get(action.type)
        if impl is tool_describe_image:
            return await tool_describe_image(session, obs)
        elif impl is tool_embed_text:
            text = action.args.get("text") or obs.text or ""
            return await tool_embed_text(session, text)
        elif impl is tool_noop:
            return await tool_noop(session)
        elif impl is tool_depth_anything:
            return await tool_depth_anything(session, obs)
        elif impl is tool_shell_command:
            cmd = action.args.get("command", "")
            return await tool_shell_command(session, cmd)
        else:
            return await tool_unknown(action.type, action.args)


# ---------------------------------------------------------------------
# TKINTER GUI
# ---------------------------------------------------------------------
class AgentGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ollama Screen Agent Controller")

        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        # Default tools (now include depth_anything + shell_command)
        default_tools = {
            "describe_image": {
                "description": "Use vision model to describe the screen region.",
                "arg_spec": "{}",
                "enabled": True,
                "confirm": False,
            },
            "embed_text": {
                "description": "Embed a piece of text for semantic retrieval.",
                "arg_spec": '{"text": "<string to embed>"}',
                "enabled": True,
                "confirm": False,
            },
            "noop": {
                "description": "Do nothing for this frame.",
                "arg_spec": "{}",
                "enabled": True,
                "confirm": False,
            },
            "depth_anything": {
                "description": "Estimate depth map of the current capture via depth_anything_2.py.",
                "arg_spec": "{}",
                "enabled": True,
                "confirm": True,
            },
            "shell_command": {
                "description": "Run a shell command on the host (e.g. 'start calc').",
                "arg_spec": '{"command": "<shell command string>"}',
                "enabled": True,
                "confirm": True,
            },
        }

        self.config = AgentConfig(
            system_purpose=(
                "Observe the user's screen, describe visual content when helpful, "
                "embed important textual information for later retrieval, "
                "optionally estimate depth, and optionally run shell commands if appropriate."
            ),
            region_x=0,
            region_y=0,
            region_w=self.screen_w // 2,
            region_h=self.screen_h // 2,
            frame_interval=3.0,
            tools=default_tools,
            confirm_enabled=True,
            overlay_color="#ff0000",
        )

        self.runner: Optional[AgentRunner] = None

        # For thread-safe logging
        self.log_queue: "queue.Queue[str]" = queue.Queue()

        # Overlay
        self.overlay_var = tk.BooleanVar(value=False)
        self.overlay_window: Optional[tk.Toplevel] = None

        # Global confirm toggle
        self.confirm_var = tk.BooleanVar(value=self.config.confirm_enabled)

        self._build_ui()
        self._populate_tools_table()
        self._update_region_sliders_from_config()
        self._update_system_prompt_from_config()

        # Periodic log processing
        self.root.after(100, self._process_log_queue)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------- UI BUILDING ----------------------
    def _build_ui(self):
        # System prompt frame
        prompt_frame = ttk.LabelFrame(self.root, text="System Prompt")
        prompt_frame.pack(fill="x", padx=5, pady=5)

        self.prompt_text = tk.Text(prompt_frame, height=4, wrap="word")
        self.prompt_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Region sliders frame
        region_frame = ttk.LabelFrame(self.root, text="Screen Capture Region")
        region_frame.pack(fill="x", padx=5, pady=5)

        self.x_var = tk.IntVar(value=self.config.region_x)
        self.y_var = tk.IntVar(value=self.config.region_y)
        self.w_var = tk.IntVar(value=self.config.region_w)
        self.h_var = tk.IntVar(value=self.config.region_h)

        # Sliders
        ttk.Label(region_frame, text="X (left)").grid(row=0, column=0, sticky="w")
        x_scale = tk.Scale(
            region_frame,
            from_=0,
            to=self.screen_w,
            orient="horizontal",
            variable=self.x_var,
            command=lambda v: self.on_region_change(),
        )
        x_scale.grid(row=0, column=1, sticky="ew")

        ttk.Label(region_frame, text="Y (top)").grid(row=1, column=0, sticky="w")
        y_scale = tk.Scale(
            region_frame,
            from_=0,
            to=self.screen_h,
            orient="horizontal",
            variable=self.y_var,
            command=lambda v: self.on_region_change(),
        )
        y_scale.grid(row=1, column=1, sticky="ew")

        ttk.Label(region_frame, text="Width").grid(row=2, column=0, sticky="w")
        w_scale = tk.Scale(
            region_frame,
            from_=50,
            to=self.screen_w,
            orient="horizontal",
            variable=self.w_var,
            command=lambda v: self.on_region_change(),
        )
        w_scale.grid(row=2, column=1, sticky="ew")

        ttk.Label(region_frame, text="Height").grid(row=3, column=0, sticky="w")
        h_scale = tk.Scale(
            region_frame,
            from_=50,
            to=self.screen_h,
            orient="horizontal",
            variable=self.h_var,
            command=lambda v: self.on_region_change(),
        )
        h_scale.grid(row=3, column=1, sticky="ew")

        region_frame.columnconfigure(1, weight=1)

        # Overlay checkbox + color
        overlay_row = 4
        overlay_check = ttk.Checkbutton(
            region_frame,
            text="Show capture overlay",
            variable=self.overlay_var,
            command=self.on_overlay_toggle,
        )
        overlay_check.grid(row=overlay_row, column=0, columnspan=1, sticky="w", pady=(5, 0))

        color_btn = ttk.Button(
            region_frame,
            text="Overlay color...",
            command=self.on_choose_overlay_color,
        )
        color_btn.grid(row=overlay_row, column=1, sticky="e", pady=(5, 0), padx=5)

        # Tools frame
        tools_frame = ttk.LabelFrame(self.root, text="Tools")
        tools_frame.pack(fill="both", padx=5, pady=5, expand=True)

        self.tools_tree = ttk.Treeview(
            tools_frame,
            columns=("description", "enabled", "confirm"),
            show="headings",
            selectmode="browse",
            height=5,
        )
        self.tools_tree.heading("description", text="Description")
        self.tools_tree.heading("enabled", text="Enabled")
        self.tools_tree.heading("confirm", text="Confirm?")
        self.tools_tree.column("description", width=300, anchor="w")
        self.tools_tree.column("enabled", width=80, anchor="center")
        self.tools_tree.column("confirm", width=80, anchor="center")
        self.tools_tree.pack(side="top", fill="x", padx=5, pady=5)

        # Add/remove/toggle tool controls
        tool_ctrl_frame = ttk.Frame(tools_frame)
        tool_ctrl_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(tool_ctrl_frame, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Label(tool_ctrl_frame, text="Description").grid(row=0, column=1, sticky="w")

        self.new_tool_name = tk.Entry(tool_ctrl_frame, width=15)
        self.new_tool_name.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.new_tool_desc = tk.Entry(tool_ctrl_frame, width=40)
        self.new_tool_desc.grid(row=1, column=1, sticky="ew", padx=(0, 5))

        add_btn = ttk.Button(tool_ctrl_frame, text="Add Tool", command=self.on_add_tool)
        add_btn.grid(row=1, column=2, padx=5)

        rem_btn = ttk.Button(tool_ctrl_frame, text="Remove Selected", command=self.on_remove_tool)
        rem_btn.grid(row=1, column=3, padx=5)

        toggle_btn = ttk.Button(
            tool_ctrl_frame, text="Toggle Enabled", command=self.on_toggle_tool
        )
        toggle_btn.grid(row=1, column=4, padx=5)

        toggle_confirm_btn = ttk.Button(
            tool_ctrl_frame, text="Toggle Confirm", command=self.on_toggle_confirm
        )
        toggle_confirm_btn.grid(row=1, column=5, padx=5)

        tool_ctrl_frame.columnconfigure(1, weight=1)

        # Control buttons frame
        control_frame = ttk.LabelFrame(self.root, text="Controls")
        control_frame.pack(fill="x", padx=5, pady=5)

        start_btn = ttk.Button(control_frame, text="Start", command=self.on_start)
        start_btn.grid(row=0, column=0, padx=5, pady=5)

        pause_btn = ttk.Button(control_frame, text="Pause", command=self.on_pause)
        pause_btn.grid(row=0, column=1, padx=5, pady=5)

        resume_btn = ttk.Button(control_frame, text="Resume", command=self.on_resume)
        resume_btn.grid(row=0, column=2, padx=5, pady=5)

        stop_btn = ttk.Button(control_frame, text="Stop", command=self.on_stop)
        stop_btn.grid(row=0, column=3, padx=5, pady=5)

        clear_btn = ttk.Button(control_frame, text="Clear Logs", command=self.on_clear_logs)
        clear_btn.grid(row=0, column=4, padx=5, pady=5)

        confirm_check = ttk.Checkbutton(
            control_frame,
            text="Enable confirmations",
            variable=self.confirm_var,
            command=self.on_confirm_toggle,
        )
        confirm_check.grid(row=0, column=5, padx=5, pady=5)

        # Logs frame
        log_frame = ttk.LabelFrame(self.root, text="Logs")
        log_frame.pack(fill="both", padx=5, pady=5, expand=True)

        self.log_text = tk.Text(log_frame, height=15, wrap="word")
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log_text.yview
        )
        log_scroll.pack(side="right", fill="y")
        self.log_text["yscrollcommand"] = log_scroll.set

    # ---------------------- UI HELPERS ----------------------
    def _update_region_sliders_from_config(self):
        self.x_var.set(self.config.region_x)
        self.y_var.set(self.config.region_y)
        self.w_var.set(self.config.region_w)
        self.h_var.set(self.config.region_h)
        self.update_overlay_geometry()

    def _update_system_prompt_from_config(self):
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", self.config.system_purpose)

    def _populate_tools_table(self):
        for row in self.tools_tree.get_children():
            self.tools_tree.delete(row)
        for name, cfg in self.config.tools.items():
            enabled = "yes" if cfg.get("enabled", True) else "no"
            confirm = "yes" if cfg.get("confirm", False) else "no"
            desc = cfg.get("description", "")
            self.tools_tree.insert("", "end", iid=name, values=(desc, enabled, confirm))

    def _process_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.insert("end", msg + "\n")
                self.log_text.see("end")
        except queue.Empty:
            pass
        self.root.after(100, self._process_log_queue)

    def enqueue_log(self, msg: str):
        self.log_queue.put(msg)

    def append_log_from_gui(self, msg: str):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    # ---------------------- REGION / OVERLAY ----------------------
    def on_region_change(self):
        self.config.region_x = int(self.x_var.get())
        self.config.region_y = int(self.y_var.get())
        self.config.region_w = int(self.w_var.get())
        self.config.region_h = int(self.h_var.get())
        self.update_overlay_geometry()

    def on_overlay_toggle(self):
        if self.overlay_var.get():
            self.create_overlay_window()
        else:
            self.destroy_overlay_window()

    def on_choose_overlay_color(self):
        color_tuple = colorchooser.askcolor(color=self.config.overlay_color, title="Choose overlay color")
        if color_tuple and color_tuple[1]:
            self.config.overlay_color = color_tuple[1]
            self.update_overlay_geometry(force_color=True)

    def create_overlay_window(self):
        if self.overlay_window is not None:
            return
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes("-topmost", True)
        self.overlay_window.attributes("-alpha", 0.3)
        self.overlay_window.config(bg=self.config.overlay_color)
        self.update_overlay_geometry()

    def destroy_overlay_window(self):
        if self.overlay_window is not None:
            self.overlay_window.destroy()
            self.overlay_window = None

    def update_overlay_geometry(self, force_color: bool = False):
        if not self.overlay_var.get() or self.overlay_window is None:
            return
        x = self.config.region_x
        y = self.config.region_y
        w = self.config.region_w
        h = self.config.region_h
        self.overlay_window.geometry(f"{w}x{h}+{x}+{y}")
        if force_color:
            self.overlay_window.config(bg=self.config.overlay_color)

    # ---------------------- TOOLS HANDLERS ----------------------
    def on_add_tool(self):
        name = self.new_tool_name.get().strip()
        desc = self.new_tool_desc.get().strip()
        if not name:
            messagebox.showerror("Error", "Tool name cannot be empty.")
            return
        if name in self.config.tools:
            messagebox.showerror("Error", f"Tool '{name}' already exists.")
            return
        self.config.tools[name] = {
            "description": desc,
            "arg_spec": "{}",
            "enabled": True,
            "confirm": False,
        }
        self._populate_tools_table()
        self.new_tool_name.delete(0, "end")
        self.new_tool_desc.delete(0, "end")

    def on_remove_tool(self):
        sel = self.tools_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "No tool selected.")
            return
        name = sel[0]
        if name in self.config.tools:
            del self.config.tools[name]
        self._populate_tools_table()

    def on_toggle_tool(self):
        sel = self.tools_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "No tool selected.")
            return
        name = sel[0]
        cfg = self.config.tools.get(name)
        if not cfg:
            return
        cfg["enabled"] = not cfg.get("enabled", True)
        self._populate_tools_table()

    def on_toggle_confirm(self):
        sel = self.tools_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "No tool selected.")
            return
        name = sel[0]
        cfg = self.config.tools.get(name)
        if not cfg:
            return
        cfg["confirm"] = not cfg.get("confirm", False)
        self._populate_tools_table()

    # ---------------------- CONTROL HANDLERS ----------------------
    def _update_config_from_gui(self):
        self.config.system_purpose = self.prompt_text.get("1.0", "end").strip()
        self.config.region_x = int(self.x_var.get())
        self.config.region_y = int(self.y_var.get())
        self.config.region_w = int(self.w_var.get())
        self.config.region_h = int(self.h_var.get())
        self.config.confirm_enabled = bool(self.confirm_var.get())

    def on_start(self):
        self._update_config_from_gui()
        if self.runner is None or not self.runner.is_running():
            self.runner = AgentRunner(self.config, self.enqueue_log)
            self.runner.start()
        else:
            messagebox.showinfo("Info", "Agent already running.")

    def on_pause(self):
        if self.runner:
            self.runner.pause()

    def on_resume(self):
        if self.runner:
            self.runner.resume()

    def on_stop(self):
        if self.runner:
            self.runner.stop()

    def on_clear_logs(self):
        self.log_text.delete("1.0", "end")

    def on_confirm_toggle(self):
        self.config.confirm_enabled = bool(self.confirm_var.get())

    def on_close(self):
        if self.runner and self.runner.is_running():
            if messagebox.askyesno(
                "Quit", "Agent is running. Stop it and quit?"
            ):
                self.runner.stop()
            else:
                return
        self.destroy_overlay_window()
        self.root.destroy()


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
if __name__ == "__main__":
    """
    Requirements:

      1) Start Ollama:
            ollama serve

      2) Pull models:
            ollama pull qwen3:latest
            ollama pull granite3.2-vision:latest
            ollama pull mxbai-embed-large:latest

      3) Python deps:
            pip install aiohttp mss pillow

      4) External depth script:
            ..\\ollama_vision\\depth_anything_2.py
         Should accept:
            python depth_anything_2.py input.jpg output.jpg
    """
    root = tk.Tk()
    app = AgentGUI(root)
    root.mainloop()

