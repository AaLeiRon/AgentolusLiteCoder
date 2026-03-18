# agentoluslitecoder/__main__.py
import sys
import os
import json
import argparse

from .main import (
    load_system_prompt, extract_code, run_code, write_file, read_file,
    list_files, log, cwd_display,
    run_git, is_git_repo, load_git_config, save_git_config,
    ensure_gitignore, SANDBOX_PATH,
)

try:
    import requests
except ImportError:
    print("Missing dependency: requests\nInstall with: pip install requests")
    sys.exit(1)

API_URL = os.environ.get("AGENTOLUS_API_URL", "http://127.0.0.1:11434/api/chat")
MODEL_NAME = os.environ.get("AGENTOLUS_MODEL", "glm-4.7-flash:q8_0")
DEFAULT_SANDBOX = os.path.join(os.path.expanduser("~"), "agentolus_sandbox")

# Models available for selection at startup
AVAILABLE_MODELS = [
    ("glm-4.7-flash:q8_0", "~8GB", "⚡⚡⚡ Fast daily coding"),
    ("qwen3:32b", "~20GB", "⚡⚡  Complex projects"),
    ("qwen3-coder:30b", "~20GB", "⚡⚡  Code specialist"),
    ("qwen3.5:122b", "~75GB", "⚡    Large reasoning model"),
    ("gpt-oss:120b", "~65GB", "⚡    Maximum intelligence"),
]

CYAN  = "\033[36m"
GRAY  = "\033[90m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
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


def choose_model():
    """Let the user pick a model at startup."""
    global MODEL_NAME

    print(f"{CYAN}  Select your model:{RESET}\n")
    for i, (name, size, desc) in enumerate(AVAILABLE_MODELS, 1):
        default_marker = f" {GREEN}← default{RESET}" if name == MODEL_NAME else ""
        print(f"    [{i}] {name}  ({size})  {desc}{default_marker}")
    print()

    try:
        choice = input(f"  Your choice (1-{len(AVAILABLE_MODELS)}) or Enter for default: ").strip()
    except KeyboardInterrupt:
        print()
        return MODEL_NAME

    if choice and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(AVAILABLE_MODELS):
            MODEL_NAME = AVAILABLE_MODELS[idx][0]
            print(f"\n{GREEN}  Selected: {MODEL_NAME}{RESET}\n")
            return MODEL_NAME

    print(f"\n{GREEN}  Using default: {MODEL_NAME}{RESET}\n")
    return MODEL_NAME


def choose_git_repo():
    """Git repository setup at startup."""
    config = load_git_config()
    sandbox = SANDBOX_PATH

    # Check if already a git repo
    if is_git_repo():
        # Get current remote
        try:
            result = __import__("subprocess").run(
                ["git", "remote", "-v"],
                capture_output=True, text=True, cwd=sandbox, timeout=5,
            )
            remote_info = result.stdout.strip()
        except Exception:
            remote_info = ""

        if remote_info:
            # Extract first remote URL
            first_line = remote_info.split("\n")[0]
            remote_url = first_line.split("\t")[1].split(" ")[0] if "\t" in first_line else "unknown"
            print(f"{GREEN}  🔗 Git: connected to {remote_url}{RESET}")
        else:
            print(f"{GREEN}  🔗 Git: local repo (no remote){RESET}")

        print(f"{GRAY}  Use !git status, !git push, etc. in chat{RESET}\n")
        return True

    # Not a git repo — ask user
    print(f"{CYAN}  🔗 Git Repository:{RESET}\n")
    print(f"    [1] Clone a remote repository")
    print(f"    [2] Init new local repo")
    print(f"    [3] Skip (no git)")
    print()

    try:
        choice = input("  Your choice (1-3) or Enter to skip: ").strip()
    except KeyboardInterrupt:
        print()
        return False

    if choice == "1":
        try:
            url = input(f"  Repository URL: ").strip()
        except KeyboardInterrupt:
            print()
            return False

        if not url:
            print(f"{YELLOW}  ⚠️  No URL provided, skipping git{RESET}\n")
            return False

        print(f"{CYAN}  ⏳ Cloning {url}...{RESET}")
        try:
            # Clone into a temp dir, then move contents to sandbox
            import tempfile
            temp_dir = tempfile.mkdtemp()
            result = __import__("subprocess").run(
                ["git", "clone", url, temp_dir],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                print(f"{YELLOW}  ⚠️  Clone failed: {result.stderr.strip()}{RESET}\n")
                return False

            # Move .git and files to sandbox
            import shutil
            git_dir = os.path.join(temp_dir, ".git")
            target_git = os.path.join(sandbox, ".git")
            if os.path.exists(target_git):
                shutil.rmtree(target_git)
            shutil.move(git_dir, target_git)

            # Copy files (don't overwrite existing sandbox files)
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(sandbox, item)
                if not os.path.exists(dst):
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)

            shutil.rmtree(temp_dir, ignore_errors=True)
            ensure_gitignore()
            save_git_config({"remote_url": url, "connected": True})
            print(f"{GREEN}  ✅ Cloned and connected to {url}{RESET}\n")
            return True

        except Exception as e:
            print(f"{YELLOW}  ⚠️  Clone failed: {e}{RESET}\n")
            return False

    elif choice == "2":
        try:
            result = __import__("subprocess").run(
                ["git", "init"],
                capture_output=True, text=True, cwd=sandbox, timeout=10,
            )
            if result.returncode == 0:
                ensure_gitignore()
                save_git_config({"connected": True, "local_only": True})
                print(f"{GREEN}  ✅ Initialized git repo in sandbox{RESET}\n")

                # Ask for remote
                try:
                    url = input(f"  Add remote URL? (Enter to skip): ").strip()
                except KeyboardInterrupt:
                    url = ""

                if url:
                    __import__("subprocess").run(
                        ["git", "remote", "add", "origin", url],
                        capture_output=True, text=True, cwd=sandbox, timeout=10,
                    )
                    save_git_config({"remote_url": url, "connected": True})
                    print(f"{GREEN}  ✅ Remote added: {url}{RESET}\n")

                return True
            else:
                print(f"{YELLOW}  ⚠️  Git init failed: {result.stderr.strip()}{RESET}\n")
                return False
        except FileNotFoundError:
            print(f"{YELLOW}  ⚠️  Git not installed! Get it from https://git-scm.com/{RESET}\n")
            return False

    print(f"{GRAY}  Skipping git setup{RESET}\n")
    return False


def ensure_model_loaded():
    """Pre-load the model in Ollama if not already running."""
    ollama_base = API_URL.replace("/api/chat", "")

    # Check if Ollama is reachable
    try:
        resp = requests.get(f"{ollama_base}/api/tags", timeout=5)
        if resp.status_code != 200:
            print(f"{YELLOW}  ⚠️  Ollama not reachable at {ollama_base}{RESET}")
            return False
    except Exception:
        print(f"{YELLOW}  ⚠️  Ollama not running. Start it first!{RESET}")
        return False

    # Check if model is already loaded
    try:
        resp = requests.get(f"{ollama_base}/api/ps", timeout=5)
        if resp.status_code == 200:
            running = resp.json().get("models", [])
            for m in running:
                if m.get("name", "").startswith(MODEL_NAME.split(":")[0]):
                    print(f"{GREEN}  ✅ Model {MODEL_NAME} ready{RESET}")
                    return True
    except Exception:
        pass

    # Pre-warm: send a tiny request to load the model
    print(f"{CYAN}  ⏳ Loading model {MODEL_NAME}...{RESET}")
    try:
        resp = requests.post(
            API_URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": "hi"}],
                "stream": False,
                "think": False,
            },
            timeout=120,
        )
        if resp.status_code == 200:
            print(f"{GREEN}  ✅ Model {MODEL_NAME} loaded!{RESET}")
            return True
        else:
            print(f"{YELLOW}  ⚠️  Failed to load model: {resp.status_code}{RESET}")
            return False
    except Exception as e:
        print(f"{YELLOW}  ⚠️  Failed to load model: {e}{RESET}")
        return False


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
            json={
                "model": MODEL_NAME,
                "messages": messages[-6:],
                "stream": False,
                "think": False,
            },
            timeout=300,
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

    ensure_model_loaded()
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
    choose_model()
    ensure_model_loaded()
    choose_git_repo()
    print()
    if profile is None:
        profile = first_time_setup(sandbox_path)
    name = profile.get("name", "User")
    emoji = profile.get("emoji", "🦀")
    print(f"{CYAN}  v0.1.0  |  Hey {name} {emoji}  |  sandbox: {sandbox_path}")
    print(f"  model: {MODEL_NAME}{RESET}")
    print(f"{GRAY}  !reset = clear memory  |  !profile = change profile  |  !model = switch model  |  !git = git commands  |  Ctrl+C = exit{RESET}\n")
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
        if user == "!model":
            choose_model()
            ensure_model_loaded()
            continue
        if user.startswith("!git"):
            git_cmd = user[4:].strip()
            if not git_cmd:
                print(f"{CYAN}  Git commands: !git status, !git add ., !git commit \"msg\", !git push, !git pull, !git log, !git diff, !git branch{RESET}\n")
                continue
            result = run_git(git_cmd)
            print(f"🔗 {result}\n")
            continue
        process(user, messages, memory_file, verbose=verbose)


if __name__ == "__main__":
    main()
