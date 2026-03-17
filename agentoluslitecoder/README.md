<h1 align="center">🦀 AgentolusLiteCoder</h1>

<p align="center">
  <strong>Your local, offline, pure-Python coding agent</strong>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge" alt="MIT License"></a>
  <a href="https://ollama.com"><img src="https://img.shields.io/badge/Powered_by-Ollama-f97316?style=for-the-badge" alt="Ollama"></a>
  <a href="https://github.com/AaLeiRon/agentoluslitecoder"><img src="https://img.shields.io/badge/Version-0.1.0-a855f7?style=for-the-badge" alt="Version"></a>
</p>

<p align="center">
  <em>No cloud. No API keys. No data leaving your computer.<br>Just you, your terminal, and a local LLM writing real code. 🔒</em>
</p>

---

<pre align="center">
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
</pre>

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🧠 | **Local LLM Powered** | Runs on Ollama with any model — GLM, Qwen, GPT-OSS, and more |
| 🏖️ | **Sandboxed Execution** | All code runs safely inside `~/agentolus_sandbox` |
| 📝 | **File Operations** | Create, read, edit, delete files with natural language |
| 📂 | **Directory Navigation** | Navigate folders, create directories, list contents |
| ⚡ | **Auto Code Execution** | LLM generates Python → agent executes → you see results |
| 🔄 | **Bash→Python** | Bash output auto-converted to safe Python |
| 🧹 | **AST Sanitization** | Path injections stripped at the syntax tree level |
| 💾 | **Memory** | Conversation context preserved across commands |
| 🔙 | **Auto-Backup** | Files backed up before overwriting |
| 🎭 | **Profiles** | Choose your name and emoji avatar — 🦀 🐱 👽 |
| 🌐 | **HTTP API** | FastAPI server for Telegram, Discord, and more |

---

## 🚀 Quick Start

**Prerequisites:** Python 3.10+ and [Ollama](https://ollama.com) running locally

```bash
git clone https://github.com/AaLeiRon/agentoluslitecoder.git
cd agentoluslitecoder
pip install -e .
```

Then just type:

```bash
ald
```

That's it! 🎉

> **Other modes:**
> - `alc "create a hello world script"` — single prompt mode
> - `ald --sandbox /custom/path` — custom sandbox location  
> - `ald --reset` — clear conversation memory

---

## 🖥️ CLI in Action

```
  v0.1.0  |  Hey Aaron 🦀  |  sandbox: ~/agentolus_sandbox
  !reset = clear memory  |  !profile = change profile  |  Ctrl+C = exit

  🦀 Aaron [agentolus_sandbox]: create a folder called myproject
  🤖 Agentolus: Created: myproject

  🦀 Aaron [agentolus_sandbox]: cd myproject
  🤖 Agentolus: 📂 myproject

  🦀 Aaron [agentolus_sandbox/myproject]: create march.py that prints hello march
  🤖 Agentolus: Created: march.py

  🦀 Aaron [agentolus_sandbox/myproject]: execute march.py
  🤖 Agentolus: hello march

  🦀 Aaron [agentolus_sandbox/myproject]: read march.py
  🤖 Agentolus: print("hello march")
```

---

## 🎮 What Can You Say?

<table>
<tr><td>

### 📁 Files
```
create a file called hello.py with hello world
read hello.py
delete hello.py
list files
```

</td><td>

### 📂 Navigation
```
cd myproject
cd ..
create a folder called src
pwd
```

</td></tr>
<tr><td>

### ⚡ Execution
```
execute hello.py
create a fibonacci function and run it
write a script that lists all .txt files
```

</td><td>

### 🧠 Smart Tasks
```
build me a flask REST API
fix the bug in app.py
add error handling to main.py
refactor this to use classes
```

</td></tr>
</table>

---

## 🛡️ Security

> **Your system is always protected.** Every operation is sandboxed, sanitized, and logged.

| | Protection | How |
|---|---|---|
| 🔒 | **Sandboxed** | All operations confined to `~/agentolus_sandbox` |
| 🧹 | **AST Sanitized** | Path injection attacks stripped at syntax tree level |
| 🚫 | **No Shell Escape** | Shell metacharacters `& \| ; > <` blocked |
| 💾 | **Auto Backup** | Files backed up before any overwrite |
| 📝 | **Audit Trail** | Every action logged to `execution.log` |
| 🔑 | **100% Offline** | No data ever leaves your machine |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENTOLUS_MODEL` | `glm-4.7-flash:q8_0` | Ollama model to use |
| `AGENTOLUS_API_URL` | `http://127.0.0.1:11434/api/chat` | Ollama API endpoint |
| `AGENTOLUS_SANDBOX` | `~/agentolus_sandbox` | Sandbox directory path |

### 🏆 Recommended Models

| Model | Size | Speed | Best For |
|---|---|---|---|
| `glm-4.7-flash:q8_0` | ~8GB | 🟢🟢🟢 | Daily coding tasks |
| `qwen3:32b` | ~20GB | 🟢🟢 | Complex projects |
| `qwen3-coder:30b` | ~20GB | 🟢🟢 | Pure code generation |
| `gpt-oss:120b` | ~65GB | 🟢 | Maximum intelligence |

---

## 🌐 HTTP API

> Connect AgentolusLiteCoder to **Telegram**, **Discord**, or any HTTP client

```bash
pip install fastapi uvicorn
python litecoder_api.py
# → Server running on http://localhost:8085
```

**Endpoints:**

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a coding prompt |
| `POST` | `/api/reset` | Reset conversation memory |
| `GET` | `/api/status` | Sandbox & model info |
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
  You ───prompt──→ 🧠 LLM (Ollama) ───python code──→ 🔧 Processing Pipeline ───safe code──→ 🏖️ Sandbox
                                                          │
                                                     extract_code()
                                                     _sanitize_code()    ← AST sanitization
                                                     _repair_code()      ← auto-fix mistakes
                                                     _maybe_wrap_expr()  ← REPL-style output
```

All files live in `~/agentolus_sandbox/`:

```
agentolus_sandbox/
├── myproject/           ← your projects
│   ├── app.py
│   └── utils.py
├── _backup/             ← automatic file backups
├── memory.json          ← conversation history
├── execution.log        ← full audit trail
└── .profile.json        ← your name & emoji
```

---

## 🤝 Part of the Agentolus Ecosystem

AgentolusLiteCoder is the **coding brain** of the [Agentolus](https://github.com/AaLeiRon) multi-agent system:

```
  📱 Telegram / Discord
          │
          ▼
  🎯 Major Agent (Orchestrator)
          │
          ├── 💬 Comms Agent     →  Email, Telegram, Calendar
          ├── 🌐 Browser Agent   →  Web Browsing (PinchTab)
          ├── 🧠 LLM Agent       →  Claude, ChatGPT, Gemini
          ├── 📸 Social Agent    →  Instagram, LinkedIn
          └── 🦀 Coder Agent     →  YOU ARE HERE
```

---

## 📋 CLI Commands

| Command | What it does |
|---|---|
| `!reset` | 🧹 Clear conversation memory |
| `!profile` | 🎭 Change your name and emoji |
| `pwd` | 📂 Show current directory |
| `Ctrl+C` | 👋 Exit gracefully |

---

## 🗺️ Roadmap

- [x] Sandboxed code execution
- [x] File and directory operations
- [x] Bash to Python auto-conversion
- [x] AST path sanitization
- [x] Conversation memory
- [x] HTTP API for integrations
- [ ] Agentic loop (Plan → Code → Test → Fix)
- [ ] Project context scanning
- [ ] Auto-testing (pytest)
- [ ] Dependency detection
- [ ] Multi-file project generation

---

## 📄 License

[MIT](LICENSE) — do whatever you want with it! 🎉

---

<p align="center">
  <strong>Built with ❤️ and 🦀 by <a href="https://github.com/AaLeiRon">AaLeiRon</a></strong>
  <br>
  <em>No clouds were harmed in the making of this agent</em> ☁️❌
</p>

<pre align="center">
┌────────────────────────────┐
│   >>> happy coding! <<<    │
└────────────────────────────┘
</pre>
