# agentoluslitecoder/__main__.py
import sys
import os
import json
import argparse

from .main import (
    load_system_prompt, extract_code, run_code, write_file, read_file,
    list_files, log, cwd_display
)

try:
    import requests
except ImportError:
    print("Missing dependency: requests\nInstall with: pip install requests")
    sys.exit(1)

API_URL = os.environ.get("AGENTOLUS_API_URL", "http://127.0.0.1:11434/api/chat")
MODEL_NAME = os.environ.get("AGENTOLUS_MODEL", "qwen3-coder-next:latest")
DEFAULT_SANDBOX = os.path.join(os.path.expanduser("~"), "agentolus_sandbox")

CYAN  = "\033[36m"
GRAY  = "\033[90m"
RESET = "\033[0m"

BANNER = (
    f"{CYAN}\n"
    "  ╔══════════════════════════════════════════╗\n"
    "  ║  ◉ ─────────────────────────────────── ◉ ║\n"
    "  ║        A G E N T O L U S                 ║\n"
    "  ║      L I T E   C O D E R                 ║\n"
    "  ║  ◉ ─────────────────────────────────── ◉ ║\n"
    "  ╚══════════════════════════════════════════╝\n"
    "         │  ╔═══════════════════╗  │\n"
    "         │  ║  ▓▓  ·ALC·  ▓▓    ║  │\n"
    "         ╰──║  ▓▓  ▓▓▓▓▓  ▓▓    ║──╯\n"
    "            ║  ▓▓  ▓▓▓▓▓  ▓▓    ║\n"
    "            ╚═══════════════════╝\n"
    "             ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗\n"
    "             ║█║ ║█║ ║█║ ║█║ ║█║\n"
    "             ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝\n"
    "        ┌────────────────────────────┐\n"
    "        │  >>> ready to execute <<<  │\n"
    "        └────────────────────────────┘\n"
    f"{RESET}"
)

EMOJI_CHOICES = {
    "1": ("🦀", "Crab"),
    "2": ("🐱", "Cat"),
    "3": ("👽", "Alien"),
}


def load_profile(sandbox_path):
    path = os.path.join(sandbox_path, ".profile.json")
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            pass
    return None


def save_profile(sandbox_path, name, emoji):
    path = os.path.join(sandbox_path, ".profile.json")
    json.dump({"name": name, "emoji": emoji}, open(path, "w", encoding="utf-8"))


def first_time_setup(sandbox_path):
    print(f"{CYAN}  Lets set up your profile.{RESET}\n")
    try:
        name = input("  Whats your name? ").strip() or "User"
    except KeyboardInterrupt:
        name = "User"
    print()
    print("  Choose your emoji:")
    for key, (emoji, label) in EMOJI_CHOICES.items():
        print(f"    [{key}] {emoji}  {label}")
    print()
    try:
        choice = input("  Your choice (1/2/3): ").strip()
        emoji = EMOJI_CHOICES.get(choice, ("🦀", "Crab"))[0]
    except KeyboardInterrupt:
        emoji = "🦀"
    save_profile(sandbox_path, name, emoji)
    print(f"\n{CYAN}  Nice to meet you, {name} {emoji}!{RESET}\n")
    return {"name": name, "emoji": emoji}


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
            timeout=180
        )
        return response.json()["message"]["content"]
    except Exception as e:
        log(f"API error: {e}", level="ERROR")
        return f"[API ERROR] {e}"


def process(user, messages, memory_file, verbose=False):
    messages.append({"role": "user", "content": user})
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, load_system_prompt())
    else:
        messages[0] = load_system_prompt()
    raw = call_api(messages)

    code = extract_code(raw)
    if code:
        print(f"Executing code:\n{code}\n")
        result = run_code(code)
        messages.append({"role": "assistant", "content": f"{raw}\n\nResult:\n{result}"})
        save_memory(messages, memory_file)
        print(f"🤖 Agentolus: {result}\n")
    else:
        messages.append({"role": "assistant", "content": raw})
        save_memory(messages, memory_file)
        print(f"🤖 Agentolus: {raw}\n")


def setup(sandbox_path):
    import agentoluslitecoder.main as _main
    _main.SANDBOX_PATH = sandbox_path
    _main.MEMORY_FILE = os.path.join(sandbox_path, "memory.json")
    _main.LOG_FILE = os.path.join(sandbox_path, "execution.log")
    _main.BACKUP_DIR = os.path.join(sandbox_path, "_backup")
    _main.CWD_FILE = os.path.join(sandbox_path, ".cwd")
    try:
        os.makedirs(_main.SANDBOX_PATH, exist_ok=True)
        os.makedirs(_main.BACKUP_DIR, exist_ok=True)
    except Exception as e:
        print(f"Cannot create sandbox at '{sandbox_path}': {e}")
        sys.exit(1)
    return _main


def main():
    import agentoluslitecoder.main as _main
    parser = argparse.ArgumentParser(prog="alc")
    parser.add_argument("prompt", nargs="?")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--sandbox", type=str, default=DEFAULT_SANDBOX)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    _main = setup(args.sandbox)
    memory_file = _main.MEMORY_FILE

    if args.reset:
        if os.path.exists(memory_file):
            os.remove(memory_file)
        print("Memory cleared.")
        return

    messages = load_memory(memory_file)

    if args.prompt:
        print(f"User: {args.prompt}")
        process(args.prompt, messages, memory_file, verbose=args.verbose)
    else:
        _interactive(messages, memory_file, args.verbose)


def main_interactive():
    import agentoluslitecoder.main as _main
    parser = argparse.ArgumentParser(prog="ald")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--sandbox", type=str, default=DEFAULT_SANDBOX)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    _main = setup(args.sandbox)
    memory_file = _main.MEMORY_FILE

    if args.reset:
        if os.path.exists(memory_file):
            os.remove(memory_file)
        print("Memory cleared.")
        return

    messages = load_memory(memory_file)
    _interactive(messages, memory_file, args.verbose)


def _interactive(messages, memory_file, verbose=False):
    sandbox_path = os.path.dirname(memory_file)
    profile = load_profile(sandbox_path)
    print(BANNER)
    if profile is None:
        profile = first_time_setup(sandbox_path)
    name = profile.get("name", "User")
    emoji = profile.get("emoji", "🦀")
    print(f"{CYAN}  v0.1.0  |  Hey {name} {emoji}  |  sandbox: {sandbox_path}{RESET}")
    print(f"{GRAY}  !reset = clear memory  |  !profile = change profile  |  Ctrl+C = exit{RESET}\n")
    while True:
        try:
            user = input(f"{emoji} {name} [{cwd_display()}]: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        if not user:
            continue
        if user == "!reset":
            if os.path.exists(memory_file):
                os.remove(memory_file)
            messages = [load_system_prompt()]
            print("Memory cleared.\n")
            continue
        if user.strip().lower() in ("pwd", "!pwd"):
            print(f"📂 {cwd_display()}\n")
            continue
        if user.strip().lower() in ("!profile",):
            user = "!profile"
        if user == "!profile":
            profile = first_time_setup(sandbox_path)
            name = profile.get("name", "User")
            emoji = profile.get("emoji", "🦀")
            continue
        process(user, messages, memory_file, verbose=verbose)


if __name__ == "__main__":
    main()
