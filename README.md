# 🦀 AgentolusLiteCoder

**A local, offline, pure-Python coding agent powered by Ollama**


[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Powered-f97316?style=for-the-badge)](https://ollama.com)
[![Version](https://img.shields.io/badge/v0.1.0-a855f7?style=for-the-badge)](https://github.com/AaLeiRon/agentoluslitecoder)

```
    ╔══════════════════════════════════════════╗
    ║  ◉ ─────────────────────────────────── ◉ ║
    ║        A G E N T O L U S                 ║
    ║      L I T E   C O D E R                 ║
    ║  ◉ ─────────────────────────────────── ◉ ║
    ╚══════════════════════════════════════════╝
           │  ╔═══════════════════╗  │
           │  ║  ▓▓  ·ALC·  ▓▓    ║  │
           ╰──║  ▓▓  ▓▓▓▓▓  ▓▓    ║──╯
              ║  ▓▓  ▓▓▓▓▓  ▓▓    ║
              ╚═══════════════════╝
               ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗
               ║█║ ║█║ ║█║ ║█║ ║█║
               ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝
          ┌────────────────────────────┐
          │  >>> ready to execute <<<  │
          └────────────────────────────┘
```

> No cloud • No API keys • No data leaving your computer
> Just you, your terminal, and a local LLM writing real code 🔒

---

## ✨ What is this?

**AgentolusLiteCoder** is an AI coding agent that lives in your terminal. You talk to it in plain English (or German!), and it writes, executes, and manages Python code inside a safe sandbox. Everything runs locally using [Ollama](https://ollama.com) — zero cloud dependencies.

```
🦀 Aaron [agentolus_sandbox]: create march.py that prints hello march
🤖 Agentolus: Created: march.py

🦀 Aaron [agentolus_sandbox]: execute march.py
🤖 Agentolus: hello march
```

---

## ⚡ Quick Start

```bash
# 1. Clone & install
git clone https://github.com/AaLeiRon/agentoluslitecoder.git
cd agentoluslitecoder
pip install -e .

# 2. Make sure Ollama is running with a model
ollama pull glm-4.7-flash:q8_0

# 3. Launch!
ald
```

**Other modes:**

```bash
alc "create a hello world script"    # single prompt
ald --sandbox /custom/path           # custom sandbox
ald --reset                          # clear memory
```

---

## 🖥️ What It Looks Like

```
╔══════════════════════════════════════════╗
║        A G E N T O L U S                 ║
║      L I T E   C O D E R                 ║
╚══════════════════════════════════════════╝
v0.1.0  |  Hey Aaron 🦀  |  sandbox: ~/agentolus_sandbox

🦀 Aaron [agentolus_sandbox]: create a folder called webapp
🤖 Agentolus: Created: webapp

🦀 Aaron [agentolus_sandbox]: cd webapp
🤖 Agentolus: 📂 webapp

🦀 Aaron [agentolus_sandbox/webapp]: create app.py with a flask hello world
🤖 Agentolus: Created: app.py

🦀 Aaron [agentolus_sandbox/webapp]: execute app.py
🤖 Agentolus: Hello World!

🦀 Aaron [agentolus_sandbox/webapp]: read app.py
🤖 Agentolus: print("Hello World!")
```

---

## 🎯 Features

🧠 **Local & Offline** — Runs on Ollama with GLM, Qwen, GPT-OSS, and more. Zero cloud, zero API keys.

📝 **Natural Language Coding** — "Create a flask app" → creates the file. "Fix the bug" → reads & rewrites.

🏖️ **Sandboxed & Safe** — Everything in `~/agentolus_sandbox`. AST-level path sanitization. Shell blocked.

⚡ **Smart Execution** — LLM generates Python → auto-executed. Bash auto-converted to Python.

💾 **Memory & Backup** — Conversation context preserved. Auto-backup before overwrites. Full audit trail.

🌐 **Integrations** — HTTP API (FastAPI) for Telegram, Discord. Part of the Agentolus multi-agent system.

🎭 **Profiles** — Choose your name and emoji avatar — 🦀 🐱 👽

---

## 🎮 What Can You Say?

### 📁 Files

| Command | Result |
|---|---|
| `create hello.py with hello world` | Creates file |
| `read hello.py` | Shows contents |
| `delete hello.py` | Removes (with backup!) |
| `list files` | Lists directory |

### 📂 Navigation

| Command | Result |
|---|---|
| `cd myproject` | Enter folder |
| `cd ..` | Go up |
| `create folder src` | Make directory |
| `pwd` | Show location |

### ⚡ Execution

| Command | Result |
|---|---|
| `execute hello.py` | Run Python file |
| `create & run fibonacci` | Generate + execute |
| `write a sorting script` | Create script |

### 🧠 Smart Tasks

| Command | Result |
|---|---|
| `build a REST API` | Full project |
| `fix bug in app.py` | Read + rewrite |
| `add error handling` | Modify file |
| `refactor to use classes` | Restructure code |

---

## 🛡️ Security

Your system is always protected. Every operation is sandboxed, sanitized, and logged.

| | Layer | How it works |
|---|---|---|
| 🔒 | **Sandbox** | All operations confined to `~/agentolus_sandbox` |
| 🧹 | **AST Sanitization** | Path injections stripped at syntax tree level |
| 🚫 | **Shell Blocking** | Metacharacters `& \| ; > <` are blocked |
| 💾 | **Auto-Backup** | Files backed up before any overwrite |
| 📝 | **Audit Trail** | Every action logged to `execution.log` |
| 🔑 | **100% Offline** | No network calls, ever |

---

## ⚙️ Configuration

| Variable | Default | What it does |
|---|---|---|
| `AGENTOLUS_MODEL` | `glm-4.7-flash:q8_0` | Which Ollama model to use |
| `AGENTOLUS_API_URL` | `http://127.0.0.1:11434/api/chat` | Ollama endpoint |
| `AGENTOLUS_SANDBOX` | `~/agentolus_sandbox` | Where files live |

### 🏆 Tested Models

| Model | RAM | Speed | Sweet spot |
|---|---|---|---|
| `glm-4.7-flash:q8_0` | ~8GB | 🟢🟢🟢 | Daily coding |
| `qwen3:32b` | ~20GB | 🟢🟢 | Complex projects |
| `qwen3-coder:30b` | ~20GB | 🟢🟢 | Code generation |
| `gpt-oss:120b` | ~65GB | 🟢 | Max intelligence |

---

## 🌐 HTTP API

Connect to **Telegram**, **Discord**, or any HTTP client:

```bash
pip install fastapi uvicorn
python litecoder_api.py
# → http://localhost:8085
```

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a prompt |
| `POST` | `/api/reset` | Clear memory |
| `GET` | `/api/status` | System info |
| `GET` | `/health` | Health check |

**Example:**

```bash
curl -X POST http://localhost:8085/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create a hello world file"}'
```

```json
{
  "reply": "Created: hello.py",
  "code": "with open('hello.py', 'w') as f: ...",
  "cwd": "agentolus_sandbox"
}
```

---

## 🏗️ How It Works

```
You ──→ 🧠 Ollama LLM ──→ 🔧 Processing ──→ 🏖️ Sandbox
              │                    │                │
         generates code      sanitizes &       executes safely
         (Python/Bash)       converts to       in ~/sandbox
                             safe Python
```

**Processing pipeline:**

1. `extract_code()` — pulls code from LLM response
2. `_bash_to_python()` — converts any bash to Python
3. `_sanitize_code()` — AST-level path sanitization
4. `_repair_code()` — auto-fixes common mistakes
5. `exec()` — runs in sandboxed environment

**Sandbox structure:**

```
~/agentolus_sandbox/
├── your-projects/       ← your code lives here
├── _backup/             ← automatic backups
├── memory.json          ← conversation history
├── execution.log        ← audit trail
└── .profile.json        ← name & emoji
```

---

## 🤝 Part of Agentolus

The coding brain of the **Agentolus** multi-agent ecosystem:

```
📱 Telegram / Discord
      │
      ▼
🎯 Major Agent (Router)
      ├── 💬 Comms    →  Email, Calendar, Messaging
      ├── 🌐 Browser  →  Web Browsing & Search
      ├── 🧠 LLM      →  Claude, ChatGPT, Gemini
      ├── 📸 Social   →  Instagram, LinkedIn
      └── 🦀 Coder    →  YOU ARE HERE
```

---

## 📋 CLI Reference

| Command | Description |
|---|---|
| `!reset` | 🧹 Clear memory |
| `!profile` | 🎭 Change name & emoji |
| `!git` |  🚂 git commands |
| `pwd` | 📂 Current directory |
| `!model` | 🤖 switch model |
| `Ctrl+C` | 👋 Exit |

---

## 🗺️ Roadmap

- [x] Sandboxed code execution
- [x] File & directory operations
- [x] Bash → Python conversion
- [x] AST path sanitization
- [x] Conversation memory
- [x] HTTP API
- [ ] Agentic loop (Plan → Code → Test → Fix)
- [ ] Project context scanning
- [ ] Auto-testing with pytest
- [ ] Dependency detection
- [ ] Multi-file project builder

---

https://github.com/user-attachments/assets/beea14dd-ff66-4374-8f87-0d48a813d000



---
## 📄 License

[MIT](LICENSE) — do whatever you want 🎉

---

Built with ❤️ and 🦀 by [AaLeiRon](https://github.com/AaLeiRon)

*No clouds were harmed in the making of this agent* ☁️❌
