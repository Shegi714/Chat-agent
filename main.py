import datetime
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langdetect import detect
from deep_translator import GoogleTranslator
from langchain.llms import Ollama

# Тип состояния
class ChatState(TypedDict):
    user_input: str
    output: Optional[str]

# Инструмент: текущее UTC время
def get_current_time() -> dict:
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return {"utc": now.isoformat() + "Z"}

# Роутинг по сообщению
def router(state: ChatState) -> str:
    if "time" in state["user_input"].lower():
        return "get_time"
    return "llm_fallback"

# Узел: ответ через get_current_time
def use_time_tool(state: ChatState) -> ChatState:
    time = get_current_time()
    return {
        "user_input": state["user_input"],
        "output": f"The current UTC time is {time['utc']}"
    }

# Узел: ответ через локальную модель Ollama + перевод
def llm_fallback(state: ChatState) -> ChatState:
    base_prompt = "What is my purpose?"
    user_text = state["user_input"]
    try:
        lang = detect(user_text)
        if lang != "en":
            prompt = f"Translate the following to {lang}: '{base_prompt}'"
        else:
            prompt = base_prompt
    except Exception:
        prompt = base_prompt

    # Вызов локальной модели через Ollama
    llm = Ollama(model="llama3")  # по умолчанию порт 11434
    result = llm(prompt)

    return {"user_input": user_text, "output": result.strip()}

# Построение LangGraph
builder = StateGraph(ChatState)
builder.add_node("router", router)
builder.add_node("get_time", use_time_tool)
builder.add_node("llm_fallback", llm_fallback)

builder.set_entry_point("router")
builder.add_edge("router", "get_time")
builder.add_edge("router", "llm_fallback")
builder.add_edge("get_time", END)
builder.add_edge("llm_fallback", END)

graph = builder.compile()

# Имитация langgraph dev
if __name__ == "__main__":
    print("Starting dev mode...")
    print("Waiting for input... (type 'exit' to quit)\n")
    while True:
        msg = input("You: ")
        if msg.strip().lower() in {"exit", "quit"}:
            break
        result = graph.invoke({"user_input": msg})
        print("Bot:", result["output"])
