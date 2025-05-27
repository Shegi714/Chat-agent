import datetime
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langdetect import detect
from deep_translator import GoogleTranslator

# Тип состояния
class ChatState(TypedDict):
    user_input: str
    output: Optional[str]

# Инструмент: получение времени
def get_current_time() -> dict:
    """Возвращает текущее UTC время в ISO‑8601 формате"""
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return {"utc": now.isoformat() + "Z"}

# Роутер: определяет, какой узел вызывать
def router(state: ChatState) -> str:
    text = state["user_input"].lower()
    if "time" in text:
        return "get_time"
    return "fallback"

# Узел: возвращает текущее время
def use_time_tool(state: ChatState) -> ChatState:
    response = get_current_time()
    return {
        "user_input": state["user_input"],
        "output": f"The current UTC time is {response['utc']}"
    }

# Узел: возвращает фразу "What is my purpose?" на языке пользователя
def fallback_response(state: ChatState) -> ChatState:
    prompt = "What is my purpose?"
    try:
        lang = detect(state["user_input"])
        if lang != "en":
            translated = GoogleTranslator(source="en", target=lang).translate(prompt)
            return {"user_input": state["user_input"], "output": translated}
    except Exception:
        pass
    return {"user_input": state["user_input"], "output": prompt}

# Сборка графа
builder = StateGraph(ChatState)
builder.add_node("router", router)
builder.add_node("get_time", use_time_tool)
builder.add_node("fallback", fallback_response)

builder.set_entry_point("router")
builder.add_edge("router", "get_time")
builder.add_edge("router", "fallback")
builder.add_edge("get_time", END)
builder.add_edge("fallback", END)

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
