"""HTTP API wrapper for AgentolusLiteCoder.

Bridges Telegram / Agentolus Major Agent to the LiteCoder coding agent.
Runs alongside the CLI tool as a standalone FastAPI server.

Usage:
    python litecoder_api.py
    
    Or with uvicorn:
    uvicorn litecoder_api:app --host 0.0.0.0 --port 8085
"""

import os
import sys
import logging

# Ensure the package is importable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from pydantic import BaseModel

from agentoluslitecoder.main import (
    load_system_prompt, extract_code, run_code, log as alc_log,
    cwd_display, get_cwd, list_files,
)
from agentoluslitecoder.__main__ import (
    call_api, load_memory, save_memory, setup,
    MODEL_NAME, API_URL,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("litecoder_api")

# ── Setup ──────────────────────────────────────────────
SANDBOX = os.environ.get("AGENTOLUS_SANDBOX", os.path.join(os.path.expanduser("~"), "agentolus_sandbox"))
PORT = int(os.environ.get("LITECODER_PORT", "8085"))

# Initialize sandbox and paths
import agentoluslitecoder.main as _main
_main = setup(SANDBOX)
memory_file = _main.MEMORY_FILE

# Load conversation memory
messages = load_memory(memory_file)

logger.info(f"LiteCoder API initialized")
logger.info(f"  Sandbox: {SANDBOX}")
logger.info(f"  Model: {MODEL_NAME}")
logger.info(f"  Ollama: {API_URL}")

# ── FastAPI App ────────────────────────────────────────
app = FastAPI(title="AgentolusLiteCoder API", version="0.2.0")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    code: str = ""
    result: str = ""
    cwd: str = ""


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Process a coding prompt and return the result."""
    global messages

    user_input = req.message.strip()
    if not user_input:
        return ChatResponse(reply="Empty message.", cwd=cwd_display())

    logger.info(f"Prompt: {user_input[:100]}...")

    # ── Special commands ───────────────────────────────
    if user_input == "!reset":
        if os.path.exists(memory_file):
            os.remove(memory_file)
        messages = [load_system_prompt()]
        return ChatResponse(reply="🔄 Memory cleared.", cwd=cwd_display())

    if user_input.lower() in ("pwd", "!pwd"):
        return ChatResponse(reply=f"📂 {cwd_display()}", cwd=cwd_display())

    if user_input.lower() in ("ls", "!ls", "list", "list files"):
        files = list_files(".")
        return ChatResponse(reply=f"📁 {cwd_display()}:\n{files}", cwd=cwd_display())

    # ── Process through LLM ────────────────────────────
    messages.append({"role": "user", "content": user_input})

    # Refresh system prompt (updates CWD info)
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, load_system_prompt())
    else:
        messages[0] = load_system_prompt()

    # Call the coding LLM
    raw = call_api(messages)

    # Extract and execute code
    code = extract_code(raw)
    if code:
        logger.info(f"Executing code:\n{code[:200]}...")

        result = run_code(code)

        messages.append({"role": "assistant", "content": f"{raw}\n\nResult:\n{result}"})
        save_memory(messages, memory_file)

        alc_log(f"API executed code, result: {result[:200]}")
        logger.info(f"Result: {result[:200]}")

        return ChatResponse(
            reply=result,
            code=code,
            result=result,
            cwd=cwd_display(),
        )
    else:
        # No code extracted — return raw LLM response
        messages.append({"role": "assistant", "content": raw})
        save_memory(messages, memory_file)

        logger.info(f"No code extracted, raw response: {raw[:200]}")

        return ChatResponse(
            reply=raw,
            cwd=cwd_display(),
        )


@app.post("/api/reset")
async def reset():
    """Reset conversation memory."""
    global messages
    if os.path.exists(memory_file):
        os.remove(memory_file)
    messages = [load_system_prompt()]
    logger.info("Memory reset via API")
    return {"status": "ok", "cwd": cwd_display()}


@app.get("/api/status")
async def status():
    """Get current LiteCoder status."""
    return {
        "status": "ok",
        "sandbox": SANDBOX,
        "cwd": cwd_display(),
        "cwd_full": get_cwd(),
        "memory_messages": len(messages),
        "model": MODEL_NAME,
        "ollama_url": API_URL,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "litecoder", "model": MODEL_NAME}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting LiteCoder API on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
