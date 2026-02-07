import asyncio
import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import mss
from PIL import Image


# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
EMBED_URL = f"{OLLAMA_BASE_URL}/api/embed"

MODEL_PLANNER = "qwen3:latest"
MODEL_CRITIC = "qwen3:latest"
MODEL_VISION = "granite3.2-vision:latest"
MODEL_EMBED = "mxbai-embed-large:latest"

CAPTURE_DIR = "captures"
FRAME_INTERVAL_SECONDS = 2.0   # delay between frames
MAX_FRAMES = 10                # set None or a big number for continuous


# ---------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------
@dataclass
class Observation:
    frame_id: int
    text: Optional[str] = None          # optional textual info
    image_path: Optional[str] = None    # path to captured screen image


@dataclass
class Action:
    type: str                 # "describe_image" | "embed_text" | "noop"
    args: Dict[str, Any]


@dataclass
class ToolResult:
    tool: str
    ok: bool
    payload: Dict[str, Any]


@dataclass
class Feedback:
    score: float              # 0.0–1.0
    comment: str


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

    # Fallback
    return {"fallback_text": raw}


def encode_image_to_b64(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def capture_screen_to_file(frame_id: int, directory: str = CAPTURE_DIR) -> str:
    """
    Capture the primary monitor to a JPG file and return the file path.
    Uses mss for cross-platform screen capture.
    """
    os.makedirs(directory, exist_ok=True)
    out_path = os.path.join(directory, f"frame_{frame_id}.jpg")

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        sct_img = sct.grab(monitor)

        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(out_path, "JPEG", quality=80)

    return out_path


# ---------------------------------------------------------------------
# OLLAMA CALLS (ASYNC)
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
    payload = {
        "model": model,
        "input": texts,
    }
    async with session.post(EMBED_URL, json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()

    if "embeddings" in data:
        return data["embeddings"]
    if "embedding" in data:   # older single-input format
        return [data["embedding"]]
    raise RuntimeError(f"Unexpected embedding response: {data}")


# ---------------------------------------------------------------------
# TOOLS
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
        # trunc to avoid printing 1000s of floats
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


# ---------------------------------------------------------------------
# PLANNER (MAIN AGENT) USING QWEN3
# ---------------------------------------------------------------------
PLANNER_SYSTEM_TEMPLATE = """
You are the MAIN AGENT.

Your purpose:
{purpose}

You get at each frame:
- An observation (frame_id, optional text, optional image description).
- Optional feedback about your previous action.
You must choose an ACTION using the available tools:

TOOLS:
1) "describe_image"
   - Use when you want a textual description of the current frame's image.
   - args: { }

2) "embed_text"
   - Use when you want a semantic embedding of some text you specify.
   - args: { "text": "<string to embed>" }

3) "noop"
   - Do nothing this frame.
   - args: { }

Respond ONLY in JSON:

{
  "action": "<describe_image | embed_text | noop>",
  "args": { ... },
  "explanation": "<short explanation of why you chose this>"
}
""".strip()


async def plan_action(
    session: aiohttp.ClientSession,
    system_prompt: str,
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

    planner_system = PLANNER_SYSTEM_TEMPLATE.replace("{purpose}", system_prompt)

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


# ---------------------------------------------------------------------
# CRITIC (FEEDBACK) USING QWEN3
# ---------------------------------------------------------------------
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


async def evaluate_action(
    session: aiohttp.ClientSession,
    system_prompt: str,
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
                f"AGENT PURPOSE:\n{system_prompt}\n\n"
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
# MAIN LOOP (SCREEN CAPTURE ENV)
# ---------------------------------------------------------------------
async def run_agent_loop():
    """
    Capture screen frames and run the agent on each one.
    """
    system_purpose = (
        "Observe the user's screen over time, describe visual content when helpful, "
        "and embed important textual information for later retrieval."
    )

    async with aiohttp.ClientSession() as session:
        last_feedback: Optional[Feedback] = None
        frame_id = 0

        try:
            while True:
                if MAX_FRAMES is not None and frame_id >= MAX_FRAMES:
                    print("\nReached MAX_FRAMES. Stopping.")
                    break

                print(f"\n=== FRAME {frame_id} ===")

                # Capture screen
                image_path = capture_screen_to_file(frame_id)
                obs_text = f"Screen capture frame {frame_id}"
                observation = Observation(
                    frame_id=frame_id,
                    text=obs_text,
                    image_path=image_path,
                )

                # 1) Plan
                action = await plan_action(session, system_purpose, observation, last_feedback)
                print(f"Planned action: {action.type}, args={action.args}")

                # 2) Execute tool
                if action.type == "describe_image":
                    tool_result = await tool_describe_image(session, observation)
                elif action.type == "embed_text":
                    text = action.args.get("text") or observation.text or ""
                    tool_result = await tool_embed_text(session, text)
                else:
                    tool_result = await tool_noop(session)

                print(f"Tool result: ok={tool_result.ok}, payload={tool_result.payload}")

                # 3) Critic feedback
                feedback = await evaluate_action(
                    session=session,
                    system_prompt=system_purpose,
                    observation=observation,
                    action=action,
                    tool_result=tool_result,
                )

                print(f"Feedback: score={feedback.score:.2f}, comment={feedback.comment}")
                last_feedback = feedback

                frame_id += 1
                await asyncio.sleep(FRAME_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: stopping agent loop.")


# ---------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    """
    Requirements:
      1) Start Ollama:
            ollama serve

      2) Pull models:
            ollama pull granite3.2-vision:latest
            ollama pull mxbai-embed-large:latest
            ollama pull qwen3:latest

      3) Install Python deps:
            pip install aiohttp mss pillow
    """
    asyncio.run(run_agent_loop())

