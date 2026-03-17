# agentoluslitecoder/main.py
import os, sys, json, shutil, time, io, contextlib, importlib, re, glob, ast

SANDBOX_PATH = os.environ.get("AGENTOLUS_SANDBOX", os.path.join(os.path.expanduser("~"), "agentolus_sandbox"))
MEMORY_FILE = os.path.join(SANDBOX_PATH, "memory.json")
BACKUP_DIR = os.path.join(SANDBOX_PATH, "_backup")
LOG_FILE = os.path.join(SANDBOX_PATH, "execution.log")
CWD_FILE = os.path.join(SANDBOX_PATH, ".cwd")  # persists current dir across commands

os.makedirs(SANDBOX_PATH, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_cwd():
    """Return the current sandbox-relative working directory."""
    if os.path.exists(CWD_FILE):
        try:
            rel = open(CWD_FILE).read().strip()
            full = os.path.normpath(os.path.join(SANDBOX_PATH, rel))
            # Safety: must stay inside sandbox
            if full.startswith(os.path.normpath(SANDBOX_PATH)) and os.path.isdir(full):
                return full
        except Exception:
            pass
    return SANDBOX_PATH


def set_cwd(full_path):
    """Persist a new CWD (must be inside sandbox)."""
    full_path = os.path.normpath(full_path)
    sandbox = os.path.normpath(SANDBOX_PATH)
    if not full_path.startswith(sandbox):
        raise ValueError(f"Path escapes sandbox: {full_path}")
    rel = os.path.relpath(full_path, sandbox)
    with open(CWD_FILE, "w") as f:
        f.write(rel)


def cwd_display():
    """Return a short display string like ~/agentolus_sandbox/agentOne"""
    full = get_cwd()
    sandbox = os.path.normpath(SANDBOX_PATH)
    rel = os.path.relpath(full, sandbox)
    if rel == ".":
        return os.path.basename(sandbox)
    return os.path.basename(sandbox) + "/" + rel.replace("\\", "/")


def _sanitize_path(name):
    """Strip shell metacharacters from a path string."""
    name = str(name).split('&')[0].split('|')[0].split(';')[0].split('>')[0].split('<')[0]
    name = re.sub(r'[^\w /.\\ -]', '', name).strip().strip('/')
    return name or "unnamed"

_sanitize_name = _sanitize_path  # alias used in builtins


class _SanitizePaths(ast.NodeTransformer):
    """AST pass: sanitize string args to all filesystem-touching calls."""
    _PATH_FUNCS = {
        (None, '__cd__'), (None, 'open'),
        ('os', 'makedirs'), ('os', 'remove'), ('os', 'rmdir'), ('os', 'rename'),
        ('os', 'listdir'), ('os.path', 'join'), ('os.path', 'exists'),
        ('shutil', 'rmtree'), ('shutil', 'move'), ('shutil', 'copy2'),
        ('pathlib', 'Path'),
    }

    def _is_path_call(self, node):
        if isinstance(node.func, ast.Name):
            return (None, node.func.id) in self._PATH_FUNCS
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return (node.func.value.id, node.func.attr) in self._PATH_FUNCS
        return False

    def visit_Call(self, node):
        self.generic_visit(node)
        if self._is_path_call(node) and node.args:
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                cleaned = _sanitize_path(first.value)
                if cleaned != first.value:
                    node.args[0] = ast.Constant(value=cleaned)
        return node


def _sanitize_code(code):
    """Run AST sanitization pass over generated code before exec."""
    try:
        tree = ast.parse(code)
        tree = _SanitizePaths().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except Exception:
        return code


def _repair_code(code):
    """Auto-fix common model mistakes before execution."""
    lines = code.split('\n')
    new_lines = []
    makedirs_done = set()
    for line in lines:
        m = re.match(r'.*open\s*\(\s*["\']([^"\']+/[^"\']+)["\']\s*,\s*["\'][wa]["\']', line)
        if m:
            folder = os.path.dirname(m.group(1))
            if folder and folder not in makedirs_done:
                new_lines.append(f"import os; os.makedirs({repr(folder)}, exist_ok=True)  # auto-inserted")
                makedirs_done.add(folder)
        new_lines.append(line)
    return '\n'.join(new_lines)


def _maybe_wrap_last_expr(code):
    """REPL-style: wrap bare last expression in print(), skip if already print()/exec()/eval()."""
    try:
        tree = ast.parse(code)
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = tree.body[-1]
            # Skip if already print(), exec(), eval(), or other void calls
            if isinstance(last.value, ast.Call) and isinstance(last.value.func, ast.Name):
                skip_funcs = {"print", "exec", "eval", "__cd__", "write"}
                if last.value.func.id in skip_funcs:
                    return code
            # Skip if it's a method call like f.write(), os.remove(), etc.
            if isinstance(last.value, ast.Call) and isinstance(last.value.func, ast.Attribute):
                skip_methods = {"write", "close", "remove", "rmtree", "makedirs", "mkdir"}
                if last.value.func.attr in skip_methods:
                    return code
            last_src = ast.get_source_segment(code, last)
            if last_src:
                prefix = code[:code.rfind(last_src)]
                return (prefix + f"\nprint({last_src})").strip()
    except Exception:
        pass
    return code


def _bash_to_python(bash_code):
    """Convert simple bash/shell commands to Python equivalents."""
    python_lines = ["import os, shutil"]
    for line in bash_code.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # cd
        m = re.match(r'cd\s+(.+)', line)
        if m:
            target = m.group(1).strip().strip('"\'')
            python_lines.append(f"__cd__({repr(target)})")
            continue
        # touch
        m = re.match(r'touch\s+(.+)', line)
        if m:
            f = m.group(1).strip()
            python_lines.append(f"open({repr(f)}, 'a').close()")
            python_lines.append(f"print('Created: {f}')")
            continue
        # mkdir
        m = re.match(r'mkdir(?:\s+-p)?\s+(.+)', line)
        if m:
            d = m.group(1).strip()
            python_lines.append(f"os.makedirs({repr(d)}, exist_ok=True)")
            python_lines.append(f"print('Created: {d}')")
            continue
        # echo "text" > file
        m = re.match(r'echo\s+"([^"]+)"\s*>\s*(.+)', line)
        if m:
            content, f = m.group(1), m.group(2).strip()
            python_lines.append(f"open({repr(f)}, 'w').write({repr(content)})")
            python_lines.append(f"print('Created: {f}')")
            continue
        # echo text > file
        m = re.match(r'echo\s+(.+?)\s*>\s*(.+)', line)
        if m:
            content, f = m.group(1).strip(), m.group(2).strip()
            python_lines.append(f"open({repr(f)}, 'w').write({repr(content)})")
            python_lines.append(f"print('Created: {f}')")
            continue
        # rm
        m = re.match(r'rm\s+(?:-rf?\s+)?(.+)', line)
        if m:
            target = m.group(1).strip()
            python_lines.append(f"shutil.rmtree({repr(target)}) if os.path.isdir({repr(target)}) else os.remove({repr(target)})")
            python_lines.append(f"print('Deleted: {target}')")
            continue
        # ls / dir
        if re.match(r'^ls$|^dir$|^ls\s|^dir\s', line):
            python_lines.append("print('\\n'.join(os.listdir('.')))")
            continue
        # pwd
        if re.match(r'^pwd$', line):
            python_lines.append('print(os.getcwd())')
            continue
        # python file.py execution
        m = re.match(r'(?:python3?|py)\s+(\S+\.py)(?:\s+(.*))?', line)
        if m:
            f = m.group(1).strip()
            python_lines.append(f"exec(open({repr(f)}).read())")
            continue
        # node file.js execution
        m = re.match(r'node\s+(\S+\.js)', line)
        if m:
            f = m.group(1).strip()
            python_lines.append(f"print('[INFO] Cannot execute JS natively: {f}')")
            continue
        # pip install
        m = re.match(r'pip\s+install\s+(.*)', line)
        if m:
            pkg = m.group(1).strip()
            python_lines.append(f"import subprocess; subprocess.check_call(['pip', 'install', {repr(pkg)}])")
            python_lines.append(f"print('Installed: {pkg}')")
            continue
        # mv
        m = re.match(r'mv\s+(\S+)\s+(\S+)', line)
        if m:
            src, dst = m.group(1), m.group(2)
            python_lines.append(f"shutil.move({repr(src)}, {repr(dst)})")
            python_lines.append(f"print('Moved: {src} -> {dst}')")
            continue
        # cp
        m = re.match(r'cp\s+(?:-r\s+)?(\S+)\s+(\S+)', line)
        if m:
            src, dst = m.group(1), m.group(2)
            python_lines.append(f"shutil.copy2({repr(src)}, {repr(dst)})")
            python_lines.append(f"print('Copied: {src} -> {dst}')")
            continue
        # cat
        m = re.match(r'cat\s+(.+)', line)
        if m:
            f = m.group(1).strip()
            python_lines.append(f"print(open({repr(f)}).read())")
            continue
        python_lines.append(f"print('[WARN] Could not convert: {line}')")
    return '\n'.join(python_lines)


def run_code(code):
    code = code.strip()
    if not code:
        return "[NO CODE]"

    mod_map = {}
    for name in ("os", "sys", "json", "io", "contextlib", "glob", "re", "pathlib", "shutil", "time"):
        mod_map[name] = importlib.import_module(name)

    def safe_import(name, *args, **kwargs):
        return mod_map.get(name, importlib.import_module(name))

    # __cd__ handler — changes persistent CWD within sandbox
    def __cd__(target):
        # Sanitize: strip anything after whitespace or shell metacharacters
        target = _sanitize_name(str(target))
        current = get_cwd()
        if target in ("~", "/", ""):
            new = SANDBOX_PATH
        elif target == "..":
            new = os.path.dirname(current)
            if not os.path.normpath(new).startswith(os.path.normpath(SANDBOX_PATH)):
                new = SANDBOX_PATH  # don't escape sandbox
        else:
            new = os.path.normpath(os.path.join(current, target))
        if not os.path.isdir(new):
            print(f"cd: {repr(target)}: No such directory")
            return
        set_cwd(new)
        os.chdir(new)
        rel = os.path.relpath(new, SANDBOX_PATH).replace("\\", "/")
        print(f"📂 {rel if rel != '.' else '(sandbox root)'}") 

    builtins = {
        "print": print,
        "len": len, "open": open, "str": str, "int": int, "float": float,
        "bool": bool, "list": list, "dict": dict, "set": set, "tuple": tuple,
        "range": range, "sum": sum, "min": min, "max": max, "any": any, "all": all,
        "enumerate": enumerate, "zip": zip, "sorted": sorted, "reversed": reversed,
        "isinstance": isinstance, "type": type, "exec": exec, "eval": eval,
        "compile": compile, "map": map, "filter": filter,
        "hasattr": hasattr, "getattr": getattr, "setattr": setattr,
        "importlib": importlib,
        "os": mod_map["os"], "sys": mod_map["sys"], "json": mod_map["json"],
        "io": mod_map["io"], "contextlib": contextlib, "glob": mod_map["glob"],
        "re": mod_map["re"], "pathlib": mod_map["pathlib"],
        "shutil": mod_map["shutil"], "time": mod_map["time"],
        "__import__": safe_import,
        "__cd__": __cd__,
        "_sanitize": _sanitize_name,
    }

    code = _sanitize_code(code)  # AST pass: strip injection from path args
    code = _repair_code(code)
    code = _maybe_wrap_last_expr(code)
    sandbox_globals = {"__builtins__": builtins, "SANDBOX": SANDBOX_PATH}

    prev_cwd = os.getcwd()
    try:
        os.chdir(get_cwd())  # use persistent CWD, not always sandbox root
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, sandbox_globals)
        res = output.getvalue().strip()
        # Filter out stray "None" lines from void function returns
        lines = [l for l in res.splitlines() if l.strip() != "None"]
        res = "\n".join(lines).strip()
        return res or "[OK]"
    except Exception as e:
        return f"[EXEC ERROR] {e}"
    finally:
        os.chdir(prev_cwd)


def extract_code(text):
    """Extract Python code. Auto-converts bash/powershell blocks to Python."""
    text = text.strip()

    bash_match = re.search(r'```(?:bash|shell|sh|cmd|powershell)\s*(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if bash_match:
        raw_block = bash_match.group(1)
        # PowerShell here-string
        ps_here = re.search(r'@"\s*\n(.*?)\n"@\s*\|\s*Set-Content\s+-Path\s+"([^"]+)"', raw_block, re.DOTALL)
        if ps_here:
            file_content = ps_here.group(1)
            filename = ps_here.group(2)
            folder = os.path.dirname(filename)
            lines = []
            if folder:
                lines.append(f"import os; os.makedirs({repr(folder)}, exist_ok=True)")
            lines.append(f"with open({repr(filename)}, 'w', encoding='utf-8') as f:")
            lines.append(f"    f.write({repr(file_content)})")
            lines.append(f"print('Created: {filename}')")
            return "\n".join(lines)
        converted = _bash_to_python(raw_block)
        return converted if converted.strip() else None

    for pattern in [r'```python\s*(.*?)```', r'```\s*(.*?)```']:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            lines = [l for l in candidate.splitlines() if l.strip() and not l.strip().startswith('#')]
            if lines:
                return "\n".join(lines).strip()
    return None


def load_system_prompt():
    cwd = get_cwd()
    rel = os.path.relpath(cwd, SANDBOX_PATH).replace("\\", "/")
    cwd_display_str = f"{os.path.basename(SANDBOX_PATH)}/{rel}" if rel != "." else os.path.basename(SANDBOX_PATH)

    content = f"""You are a silent Python code execution machine. You have ONE job.

SANDBOX: {SANDBOX_PATH}
CURRENT DIR: {cwd} (display: {cwd_display_str})

═══════════════════════════════════════════════
OUTPUT FORMAT — ABSOLUTE RULE, NO EXCEPTIONS:
═══════════════════════════════════════════════
Respond with ONLY a ```python ... ``` block. Nothing else.

═══════════════════════════════════════════
CODE RULES:
═══════════════════════════════════════════
- Use __cd__("folder") to change directory — it persists across commands
- __cd__("..") goes up, __cd__("~") returns to sandbox root
- ALWAYS use print() to show results
- ALWAYS use os.makedirs(parent, exist_ok=True) before writing into subfolders
- Relative paths resolve from CURRENT DIR (not sandbox root)
- NEVER use bash, shell, touch, echo — only Python
- NEVER put shell operators (&& | ; > <) inside filenames or __cd__ arguments
- Folder/file names must be simple: letters, digits, dots, dashes, underscores only
- __cd__ takes ONE simple folder name only: __cd__("myfolder") not __cd__("folder && cmd")

═══════════════════════════════════════════
EXAMPLES:
═══════════════════════════════════════════

Navigate into folder:
```python
__cd__("agentOne")
```

Go up:
```python
__cd__("..")
```

Create file in current dir:
```python
with open('hello.txt', 'w') as f:
    f.write('Hello!')
print('Created: hello.txt')
```

Create folder and enter it:
```python
import os
os.makedirs('newFolder', exist_ok=True)
__cd__("newFolder")
```

List files:
```python
import os
print('\\n'.join(os.listdir('.')))
```

Delete file:
```python
import os
os.remove('hello.txt')
print('Deleted: hello.txt')
```

Delete folder:
```python
import shutil
shutil.rmtree('myfolder')
print('Deleted: myfolder')
```

Execute/run a Python file:
```python
exec(open('myfile.py').read())
```

Read a file and show contents:
```python
print(open('myfile.py').read())
```

Write multi-line content to a file:
```python
content = '''
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
with open('app.py', 'w') as f:
    f.write(content.strip())
print('Created: app.py')
```

═══════════════════════════════════════════
CRITICAL REMINDERS — READ CAREFULLY:
═══════════════════════════════════════════
- NEVER use bash/shell commands like "python file.py" — use exec(open('file.py').read()) instead
- NEVER respond with ```bash or ```shell blocks — ONLY ```python blocks
- NEVER use shell operators (>, |, &, ;) — ONLY Python code
- NEVER use touch, echo, cat as commands — use Python open(), print() instead
- For file execution: exec(open('filename.py').read())
- For file reading: print(open('filename.py').read())
- For file writing: open('filename.py', 'w').write(content)
- You are a PYTHON-ONLY machine. No exceptions.
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
