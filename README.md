# Stateless Chat Agent

## What this does

A stateless chat agent built with [LangGraph](https://github.com/langchain-ai/langgraph). It does the following:

- Replies to every message
- If the user asks for the current time (e.g., "What time is it?"), it calls a `get_current_time` tool that returns UTC time in ISO‑8601 format
- Otherwise, it replies `"What is my purpose?"` **in the user's language**, using language detection and translation.

---

## How to run

```bash
git clone <your-repo-url>
cd your-repo
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
langgraph dev
