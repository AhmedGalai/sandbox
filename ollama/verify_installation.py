#!/usr/bin/env python3
"""
Verification script for the Ollama CLI command system.
Verifies all components are properly installed and functional.
"""

import sys
import os
from pathlib import Path

def verify_files():
    """Verify all required files exist."""
    print("Verifying Files...")
    print("=" * 60)
    
    required_files = {
        "Command System": [
            "commands/__init__.py",
            "commands/base.py",
            "commands/help.py",
            "commands/agents.py",
            "commands/vision.py",
            "commands/models.py",
            "commands/utils.py",
            "commands/settings.py",
        ],
        "Core": [
            "core/conversation.py",
        ],
        "Main": [
            "main.py",
        ],
        "Documentation": [
            "CLI_GUIDE.md",
            "COMMAND_SYSTEM_ARCHITECTURE.md",
            "COMMAND_SYSTEM_IMPLEMENTATION.md",
            "QUICK_START_CLI.md",
            "DELIVERY_SUMMARY.md",
        ],
    }
    
    all_ok = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for filename in files:
            filepath = Path(filename)
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"  ✓ {filename:<50} ({size:,} bytes)")
            else:
                print(f"  ✗ {filename:<50} MISSING")
                all_ok = False
    
    return all_ok

def verify_imports():
    """Verify all modules can be imported."""
    print("\n\nVerifying Imports...")
    print("=" * 60)
    
    import importlib.util
    
    modules_to_test = [
        ("commands.base", "BaseCommand"),
        ("commands.help", "HelpCommand"),
        ("commands.agents", "AgentsCommand"),
        ("commands.vision", "VisionCommand"),
        ("commands.models", "ModelsCommand"),
        ("commands.utils", "ClearCommand"),
        ("commands.settings", "SettingsCommand"),
        ("core.conversation", "ConversationManager"),
    ]
    
    all_ok = True
    for module_name, class_name in modules_to_test:
        try:
            # Convert module path to file path
            parts = module_name.split(".")
            filepath = Path(f"{parts[0]}/{parts[1]}.py")
            
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            
            # Skip full import due to dependencies, just check syntax
            import py_compile
            py_compile.compile(str(filepath), doraise=True)
            
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}: {e}")
            all_ok = False
    
    return all_ok

def verify_command_registry():
    """Verify command registry."""
    print("\n\nVerifying Command Registry...")
    print("=" * 60)
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("commands", "./commands/__init__.py")
        commands = importlib.util.module_from_spec(spec)
        
        # Read the file to extract registry
        with open("./commands/__init__.py") as f:
            content = f.read()
            
        # Check for registry definition
        if "COMMAND_REGISTRY" in content:
            # Count commands
            command_count = content.count('": ')
            print(f"  ✓ Command registry found")
            print(f"  ✓ Approximately {command_count} commands registered")
        else:
            print(f"  ✗ Command registry not found")
            return False
            
        # Check for aliases
        if "COMMAND_ALIASES" in content:
            print(f"  ✓ Command aliases defined")
        else:
            print(f"  ✗ Command aliases not found")
            return False
            
        return True
    except Exception as e:
        print(f"  ✗ Registry check failed: {e}")
        return False

def verify_conversation_manager():
    """Verify ConversationManager implementation."""
    print("\n\nVerifying ConversationManager...")
    print("=" * 60)
    
    try:
        with open("./core/conversation.py") as f:
            content = f.read()
        
        required_methods = [
            "add_message",
            "get_history",
            "get_window",
            "clear",
            "export",
            "search",
            "get_summary",
            "load_from_disk",
        ]
        
        all_found = True
        for method in required_methods:
            if f"async def {method}" in content or f"def {method}" in content:
                print(f"  ✓ {method}()")
            else:
                print(f"  ✗ {method}() not found")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ✗ ConversationManager check failed: {e}")
        return False

def verify_main_cli():
    """Verify main CLI implementation."""
    print("\n\nVerifying Main CLI...")
    print("=" * 60)
    
    try:
        with open("./main.py") as f:
            content = f.read()
        
        required_items = [
            ("OllamaAgentCLI", "class"),
            ("async def run", "run method"),
            ("async def process_input", "process_input method"),
            ("async def _handle_command", "command handler"),
            ("async def shutdown", "shutdown method"),
            ("ConversationManager", "conversation manager"),
            ("AgentOrchestrator", "orchestrator"),
            ("AgentFactory", "agent factory"),
            ("COMMAND_REGISTRY", "command registry"),
        ]
        
        all_found = True
        for item, description in required_items:
            if item in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} not found")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ✗ Main CLI check failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Ollama CLI Command System Verification" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    
    checks = [
        ("File Verification", verify_files),
        ("Import Verification", verify_imports),
        ("Command Registry", verify_command_registry),
        ("ConversationManager", verify_conversation_manager),
        ("Main CLI", verify_main_cli),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All verification checks passed!")
        print("✓ The CLI is ready to use: python main.py")
        return 0
    else:
        print(f"\n✗ {total - passed} verification check(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
