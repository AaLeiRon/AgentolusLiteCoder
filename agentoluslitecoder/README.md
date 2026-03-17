<div align="center">

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

# 🦀 AgentolusLiteCoder

### *Your local, offline, pure-Python coding agent*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)
[![Version](https://img.shields.io/badge/version-0.1.0-purple)](https://github.com/AaLeiRon/agentoluslitecoder)

---

**AgentolusLiteCoder** is an AI coding agent that runs entirely on your machine. No cloud. No API keys. No data leaving your computer. Just you, your terminal, and a local LLM writing real code in a sandboxed environment. 🔒

</div>

---

## ✨ Features

🧠 **Local LLM Powered** — Runs on Ollama with any compatible model (GLM, Qwen, GPT-OSS, and more)

🏖️ **Sandboxed Execution** — All code runs safely inside `~/agentolus_sandbox` — your system stays protected

📝 **File Operations** — Create, read, edit, and delete files with natural language

📂 **Directory Navigation** — Navigate folders with `cd`, create directories, list contents

⚡ **Auto Code Execution** — LLM generates Python code → agent executes it → you see the results

🔄 **Bash→Python Conversion** — Even if the LLM outputs bash, it gets converted to safe Python automatically

🧹 **AST Sanitization** — Malicious path injections are stripped at the syntax tree level

💾 **Conversation Memory** — Remembers context across commands within a session

🔙 **Auto-Backup** — Files are backed up before overwriting — never lose your work

🎭 **Custom Profiles** — Choose your name and emoji avatar (🦀🐱👽)

🌐 **HTTP API** — Optional FastAPI server for integration with other tools (Telegram, Discord, etc.)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** 🐍
- **Ollama** running locally with a model pulled 🦙

### Installation

```bash
# Clone the repo
git clone https://github.com/AaLeiRon/agentoluslitecoder.git
cd agentoluslitecoder

# Install in development mode
pip install -e .

# That's it! 🎉
```

### Launch

```bash
# Interactive mode (recommended) 💬
ald

# Single prompt mode ⚡
alc "create a hello world script"

# With custom sandbox 📁
ald --sandbox /path/to/my/sandbox

# Reset memory 🧹
ald --reset
```

---

## 🖥️ CLI in Action

```
  ╔══════════════════════════════════════════╗
  ║  ◉ ─────────────────────────────────── ◉ ║
  ║        A G E N T O L U S                 ║
  ║      L I T E   C O D E R                 ║
  ║  ◉ ─────────────────────────────────── ◉ ║
  ╚══════════════════════════════════════════╝
  v0.1.0  |  Hey Aaron 🦀  |  sandbox: ~/agentolus_sandbox
  !reset = clear memory  |  !profile = change profile  |  Ctrl+C = exit

🦀 Aaron [agentolus_sandbox]: create a folder called myproject
🤖 Agentolus: Created: myproject

🦀 Aaron [agentolus_sandbox]: cd myproject
🤖 Agentolus: 📂 myproject

🦀 Aaron [agentolus_sandbox/myproject]: create a file called app.py with a flask hello world
🤖 Agentolus: Created: app.py

🦀 Aaron [agentolus_sandbox/myproject]: execute app.py
🤖 Agentolus: Hello World!

🦀 Aaron [agentolus_sandbox/myproject]: read app.py
🤖 Agentolus: from flask import Flask
               app = Flask(__name__)
               ...
```

---

## 🎮 Commands & Examples

### 📁 File Operations

| Say this... | Agent does... |
|---|---|
| `create a file called hello.py with hello world` | Creates `hello.py` with print statement |
| `read hello.py` | Shows file contents |
| `delete hello.py` | Removes the file (backup created!) |
| `list files` | Shows all files in current directory |

### 📂 Navigation

| Say this... | Agent does... |
|---|---|
| `cd myproject` | Navigates into folder |
| `cd ..` | Goes up one level |
| `create a folder called src` | Creates directory |
| `pwd` | Shows current location |

### ⚡ Code Execution

| Say this... | Agent does... |
|---|---|
| `execute hello.py` | Runs the Python file |
| `create a fibonacci function and run it` | Generates + executes code |
| `write a script that lists all .txt files` | Creates and optionally runs it |

### 🧠 Smart Interactions

| Say this... | Agent does... |
|---|---|
| `build me a flask REST API with 3 endpoints` | Creates complete project |
| `fix the bug in app.py` | Reads, analyzes, rewrites |
| `add error handling to main.py` | Modifies existing file |
| `refactor this code to use classes` | Restructures code |

---

## 🛡️ Security

AgentolusLiteCoder takes security seriously:

| Layer | Protection |
|---|---|
| 🔒 Sandboxed | All operations confined to ~/agentolus_sandbox |
| 🧹 AST Sanitized | Path injection attacks stripped at syntax level |
| 🚫 No Shell Escape | Shell metacharacters (& \| ; > <) blocked |
| 💾 Auto Backup | Files backed up before any overwrite |
| 📝 Execution Log | Every action logged to execution.log |
| 🔑 No Network | Runs 100% offline, no data ever leaves your machine |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENTOLUS_MODEL` | `glm-4.7-flash:q8_0` | Ollama model to use |
| `AGENTOLUS_API_URL` | `http://127.0.0.1:11434/api/chat` | Ollama API endpoint |
| `AGENTOLUS_SANDBOX` | `~/agentolus_sandbox` | Sandbox directory path |

### Recommended Models 🏆

| Model | Size | Speed | Best For |
|---|---|---|---|
| `glm-4.7-flash:q8_0` | ~8GB | ⚡⚡⚡ | Daily coding tasks |
| `qwen3:32b` | ~20GB | ⚡⚡ | Complex projects |
| `qwen3-coder:30b` | ~20GB | ⚡⚡ | Pure code generation |
| `gpt-oss:120b` | ~65GB | ⚡ | Maximum intelligence |

---

## 🌐 HTTP API (Optional)

Connect AgentolusLiteCoder to **Telegram**, **Discord**, or any HTTP client:

```bash
# Install dependencies
pip install fastapi uvicorn

# Start the API server
python litecoder_api.py
```

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a coding prompt |
| `POST` | `/api/reset` | Reset conversation memory |
| `GET` | `/api/status` | Get sandbox & model info |
| `GET` | `/health` | Health check |

### Example

```bash
curl -X POST http://localhost:8085/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create a hello world file"}'
```

Response:

```json
{
  "reply": "Created: hello.py",
  "code": "with open('hello.py', 'w') as f: ...",
  "result": "Created: hello.py",
  "cwd": "agentolus_sandbox"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    YOU (Terminal)                     │
│                   ald / alc / API                     │
└──────────────────────┬──────────────────────────────┘
                       │ prompt
                       ▼
┌─────────────────────────────────────────────────────┐
│              🧠 Local LLM (Ollama)                   │
│         glm-4.7-flash / qwen3 / gpt-oss             │
└──────────────────────┬──────────────────────────────┘
                       │ python code
                       ▼
┌─────────────────────────────────────────────────────┐
│            🔧 Code Processing Pipeline               │
│                                                      │
│   extract_code()     → Bash to Python converter      │
│   _sanitize_code()   → AST path sanitization         │
│   _repair_code()     → Auto-fix common mistakes      │
│   _maybe_wrap_expr() → REPL-style output             │
└──────────────────────┬──────────────────────────────┘
                       │ safe python
                       ▼
┌─────────────────────────────────────────────────────┐
│          🏖️ Sandboxed Execution (exec)               │
│                                                      │
│   ~/agentolus_sandbox/                               │
│   ├── myproject/                                     │
│   │   ├── app.py                                     │
│   │   └── utils.py                                   │
│   ├── _backup/        ← auto backups                 │
│   ├── memory.json     ← conversation history         │
│   └── execution.log   ← audit trail                  │
└─────────────────────────────────────────────────────┘
```

---

## 🤝 Part of the Agentolus Ecosystem

AgentolusLiteCoder is the coding brain of the **Agentolus** multi-agent system:

```
📱 Telegram / Discord
        │
        ▼
🎯 Major Agent (Orchestrator)
        │
        ├── 💬 Comms Agent (Email, Telegram, Calendar)
        ├── 🌐 Browser Agent (PinchTab Web Browsing)
        ├── 🧠 LLM Agent (Claude, ChatGPT, Gemini)
        ├── 📸 Social Agent (Instagram, LinkedIn)
        └── 🦀 Coder Agent ← YOU ARE HERE
```

---

## 📋 CLI Commands

| Command | Description |
|---|---|
| `!reset` | 🧹 Clear conversation memory |
| `!profile` | 🎭 Change your name and emoji |
| `pwd` / `!pwd` | 📂 Show current directory |
| `Ctrl+C` | 👋 Exit the agent |

---

## 🗺️ Roadmap

- [x] 🏖️ Sandboxed code execution
- [x] 📂 File and directory operations
- [x] 🔄 Bash to Python auto-conversion
- [x] 🛡️ AST path sanitization
- [x] 💾 Conversation memory
- [x] 🌐 HTTP API for integrations
- [ ] 🔄 Agentic loop (Plan → Code → Test → Fix)
- [ ] 📊 Project context scanning
- [ ] 🧪 Auto-testing (pytest integration)
- [ ] 📦 Dependency detection
- [ ] 🤖 Multi-file project generation

---

## 📄 License

MIT License — do whatever you want with it! 🎉

---

<div align="center">

**Built with ❤️ and 🦀 by [AaLeiRon](https://github.com/AaLeiRon)**

*No clouds were harmed in the making of this agent* ☁️❌

```
        ┌────────────────────────────┐
        │  >>> happy coding! <<<     │
        └────────────────────────────┘
```

</div>
