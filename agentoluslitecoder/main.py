# agentoluslitecoder/main.py
import os, sys, json, shutil, time, io, contextlib, importlib, re, glob, ast

SANDBOX_PATH = os.environ.get("AGENTOLUS_SANDBOX", os.path.join(os.path.expanduser("~"), "agentolus_sandbox"))
MEMORY_FILE = os.path.join(SANDBOX_PATH, "memory.json")
BACKUP_DIR = os.path.join(SANDBOX_PATH, "_backup")
LOG_FILE = os.path.join(SANDBOX_PATH, "execution.log")

os.makedirs(SANDBOX_PATH, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _maybe_wrap_last_expr(code):
    """REPL-style: if last statement is a bare expression, wrap it in print().
    Skips if it is already a print() call to avoid print(print(...)) -> None."""
    try:
        tree = ast.parse(code)
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = tree.body[-1]
            # Skip if already a print() call
            if (isinstance(last.value, ast.Call) and
                    isinstance(last.value.func, ast.Name) and
                    last.value.func.id == "print"):
                return code
            last_src = ast.get_source_segment(code, last)
            if last_src:
                prefix = code[:code.rfind(last_src)]
                return (prefix + f"\nprint({last_src})").strip()
    except Exception:
        pass
    return code


def run_code(code):
    code = code.strip()
    if not code:
        return "[NO CODE]"

    mod_map = {}
    for name in ("os", "sys", "json", "io", "contextlib", "glob", "re", "pathlib", "shutil", "time"):
        mod_map[name] = importlib.import_module(name)

    def safe_import(name, *args, **kwargs):
        return mod_map.get(name, importlib.import_module(name))

    builtins = {
        "print": print,
        "len": len, "open": open, "str": str, "int": int, "float": float,
        "bool": bool, "list": list, "dict": dict, "set": set, "tuple": tuple,
        "range": range, "sum": sum, "min": min, "max": max, "any": any, "all": all,
        "enumerate": enumerate, "zip": zip, "sorted": sorted, "reversed": reversed,
        "isinstance": isinstance, "type": type,
        "importlib": importlib,
        "os": mod_map["os"], "sys": mod_map["sys"], "json": mod_map["json"],
        "io": mod_map["io"], "contextlib": contextlib, "glob": mod_map["glob"],
        "re": mod_map["re"], "pathlib": mod_map["pathlib"],
        "shutil": mod_map["shutil"], "time": mod_map["time"],
        "__import__": safe_import,
    }

    code = _maybe_wrap_last_expr(code)
    sandbox_globals = {"__builtins__": builtins, "SANDBOX": SANDBOX_PATH}

    prev_cwd = os.getcwd()
    try:
        os.chdir(SANDBOX_PATH)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, sandbox_globals)
        res = output.getvalue().strip()
        return res or "[OK]"
    except Exception as e:
        return f"[EXEC ERROR] {e}"
    finally:
        os.chdir(prev_cwd)


def extract_code(text):
    """Extract Python code block. Rejects bash/shell blocks and asks model to retry."""
    text = text.strip()

    # Check for bash/shell blocks explicitly — reject them
    bash_pattern = r'```(?:bash|shell|sh|cmd|powershell)\s*(.*?)```'
    if re.search(bash_pattern, text, re.DOTALL | re.IGNORECASE):
        return None  # Caller will report NO ACTIONABLE CODE

    patterns = [r'```python\s*(.*?)```', r'```\s*(.*?)```']
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            lines = [line for line in candidate.splitlines() if line.strip() and not line.strip().startswith('#')]
            if lines:
                return "\n".join(lines).strip()
    return None


def load_system_prompt():
    content = f"""You are AgentolusLiteCoder — a pure Python execution agent.
Sandbox directory: {SANDBOX_PATH}
Working directory during execution: {SANDBOX_PATH}

Output ONLY a Python code block. No explanations. No prose.

STRICT RULES:
- ONLY output ```python ... ``` blocks — NEVER use ```bash, ```shell, ```cmd or any other language
- There is no shell, no terminal, no bash — only Python
- Always use print() to show any result — never leave expressions bare
- Always use os.makedirs(path, exist_ok=True) before writing files in subdirectories
- Use relative paths (they resolve inside the sandbox automatically)
- For ANY file/folder task: use os, pathlib, shutil — not shell commands

EXAMPLES:

List files:
```python
import os
print('\\n'.join(os.listdir('.')))
```

Create folder:
```python
import os
os.makedirs('test', exist_ok=True)
print('Created: test')
```

Create file in subfolder:
```python
import os
os.makedirs('test', exist_ok=True)
with open('test/test.txt', 'w') as f:
    f.write('hello')
print('Created: test/test.txt')
```

Move/rename:
```python
import shutil
shutil.move('old.txt', 'new.txt')
print('Moved: old.txt -> new.txt')
```

Delete file:
```python
import os
os.remove('file.txt')
print('Deleted: file.txt')
```

Delete folder (with contents):
```python
import shutil
shutil.rmtree('foldername')
print('Deleted: foldername')
```

Read file:
```python
with open('file.txt', 'r') as f:
    print(f.read())
```
"""
    return {"role": "system", "content": content}


def write_file(path, content, backup=True):
    full = os.path.join(SANDBOX_PATH, path)
    parent_dir = os.path.dirname(full)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    if backup and os.path.exists(full):
        ts = time.strftime("%Y%m%d_%H%M%S")
        bak_path = os.path.join(BACKUP_DIR, f"{os.path.basename(full)}.{ts}.bak")
        shutil.copy2(full, bak_path)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"[OK] Written to: {full}"


def read_file(path):
    full = os.path.join(SANDBOX_PATH, path)
    try:
        with open(full, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[ERROR] File not found: {full}"
    except Exception as e:
        return f"[ERROR] read_file: {e}"


def list_files(path="."):
    full = os.path.join(SANDBOX_PATH, path)
    try:
        if not os.path.isdir(full):
            return f"[ERROR] Not a directory: {full}"
        files = os.listdir(full)
        return "\n".join(files) if files else "[EMPTY]"
    except Exception as e:
        return f"[ERROR] list_files: {e}"
