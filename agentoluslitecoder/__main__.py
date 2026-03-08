# agentoluslitecoder/__main__.py
import sys
import os
import json
import argparse

from .main import (
    load_system_prompt, extract_code, run_code, write_file, read_file,
    list_files, log
)

try:
    import requests
except ImportError:
    print("❌ Missing dependency: requests\nInstall with: pip install requests")
    sys.exit(1)

API_URL = os.environ.get("AGENTOLUS_API_URL", "http://127.0.0.1:11434/api/chat")
MODEL_NAME = os.environ.get("AGENTOLUS_MODEL", "qwen3-coder-next:latest")
DEFAULT_SANDBOX = os.path.join(os.path.expanduser("~"), "agentolus_sandbox")


def load_memory(memory_file):
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Memory load error: {e}")
            return [load_system_prompt()]
    return [load_system_prompt()]


def save_memory(messages, memory_file):
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)


def call_api(messages):
    try:
        response = requests.post(
            API_URL,
            json={"model": MODEL_NAME, "messages": messages[-6:], "stream": False},
            timeout=60
        )
        return response.json()["message"]["content"]
    except Exception as e:
        log(f"API error: {e}", level="ERROR")
        return f"[API ERROR] {e}"


def process(user, messages, memory_file, verbose=False):
    messages.append({"role": "user", "content": user})
    raw = call_api(messages)

    code = extract_code(raw)
    if code:
        print(f"▶️ Executing code:\n{code}\n")
        result = run_code(code)
        messages.append({"role": "assistant", "content": f"{raw}\n\nResult:\n{result}"})
        save_memory(messages, memory_file)
        print(f"🤖 Agentolus: {result}\n")
    else:
        # No code block — conversational reply, just show the raw text
        messages.append({"role": "assistant", "content": raw})
        save_memory(messages, memory_file)
        print(f"🤖 Agentolus: {raw}\n")


def setup(sandbox_path):
    """Initialize sandbox and return patched _main module."""
    import agentoluslitecoder.main as _main
    _main.SANDBOX_PATH = sandbox_path
    _main.MEMORY_FILE = os.path.join(sandbox_path, "memory.json")
    _main.LOG_FILE = os.path.join(sandbox_path, "execution.log")
    _main.BACKUP_DIR = os.path.join(sandbox_path, "_backup")
    try:
        os.makedirs(_main.SANDBOX_PATH, exist_ok=True)
        os.makedirs(_main.BACKUP_DIR, exist_ok=True)
    except Exception as e:
        print(f"❌ Cannot create sandbox at '{sandbox_path}': {e}")
        print(f"💡 Try: alc --sandbox C:\\Users\\YourName\\agentolus_sandbox \"your command\"")
        sys.exit(1)
    return _main


def main():
    """alc — single command mode: alc "your prompt" """
    import agentoluslitecoder.main as _main

    parser = argparse.ArgumentParser(
        prog="alc",
        description="🚀 AgentolusLiteCoder — lightweight local Python coding agent.",
        epilog="📌 Example: alc --verbose 'list files'  |  Use 'ald' for interactive mode"
    )
    parser.add_argument("prompt", nargs="?", help="Your command (if omitted, enters interactive mode)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show raw API response")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--sandbox", type=str, default=DEFAULT_SANDBOX,
                        help=f"Sandbox directory (default: {DEFAULT_SANDBOX})")
    parser.add_argument("--reset", action="store_true", help="Clear memory and start fresh")
    args = parser.parse_args()

    _main = setup(args.sandbox)
    memory_file = _main.MEMORY_FILE

    if args.reset:
        if os.path.exists(memory_file):
            os.remove(memory_file)
        print("✅ Memory cleared.")
        return

    messages = load_memory(memory_file)

    if args.prompt:
        print(f"🧠 User (CLI): {args.prompt}")
        process(args.prompt, messages, memory_file, verbose=args.verbose)
    else:
        # Fall through to interactive if no prompt given
        _interactive(messages, memory_file, args.verbose)


def main_interactive():
    """ald — interactive loop mode"""
    import agentoluslitecoder.main as _main

    parser = argparse.ArgumentParser(
        prog="ald",
        description="🚀 AgentolusLiteCoder — interactive mode (type commands, Ctrl+C to exit).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show raw API response")
    parser.add_argument("--sandbox", type=str, default=DEFAULT_SANDBOX,
                        help=f"Sandbox directory (default: {DEFAULT_SANDBOX})")
    parser.add_argument("--reset", action="store_true", help="Clear memory and start fresh")
    args = parser.parse_args()

    _main = setup(args.sandbox)
    memory_file = _main.MEMORY_FILE

    if args.reset:
        if os.path.exists(memory_file):
            os.remove(memory_file)
        print("✅ Memory cleared.")
        return

    messages = load_memory(memory_file)
    _interactive(messages, memory_file, args.verbose)


def _interactive(messages, memory_file, verbose=False):
    print("✨ AgentolusLiteCoder v0.1.0 — Interactive Mode")
    print(f"📝 Sandbox: {messages and os.path.dirname(memory_file)}")
    print("💡 Commands: !reset = clear memory | Ctrl+C = exit\n")
    while True:
        try:
            user = input("🤖 You: ").strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        if not user:
            continue
        if user == "!reset":
            if os.path.exists(memory_file):
                os.remove(memory_file)
            messages = [load_system_prompt()]
            print("✅ Memory cleared.\n")
            continue
        process(user, messages, memory_file, verbose=verbose)


if __name__ == "__main__":
    main()
