import datetime
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langdetect import detect
from deep_translator import GoogleTranslator
from langchain_community.llms import Ollama  # фикс по импорту

# Состояние чата
class ChatState(TypedDict):
    user_input: str
    output: Optional[str]

# Инструмент: получение времени
def get_current_time() -> dict:
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return {"utc": now.isoformat() + "Z"}

# Узел маршрутизации: возвращает имя следующего узла
def router(state: ChatState) -> str:
    if "time" in state["user_input"].lower():
        return "get_time"
    return "llm_fallback"

# Узел: возврат времени
def use_time_tool(state: ChatState) -> ChatState:
    result = get_current_time()
    return {"user_input": state["user_input"], "output": f"The current UTC time is {result['utc']}"}

# Узел: перевод "What is my purpose?" на язык пользователя через LLM
def llm_response(state: ChatState) -> ChatState:
    user_input = state["user_input"]
    lang = "en"
    try:
        lang = detect(user_input)
    except Exception:
        pass

    prompt = f"Translate 'What is my purpose?' into {lang}."
    output = llm.invoke(prompt)
    return {"user_input": user_input, "output": output}

# Подключаем Ollama
llm = Ollama(model="llama3")  # убедись что модель загружена: ollama pull llama3

# Сборка графа
builder = StateGraph(ChatState)
builder.add_node("router", router)
builder.add_node("get_time", use_time_tool)
builder.add_node("llm_fallback", llm_response)

builder.set_entry_point("router")
builder.add_edge("router", "get_time")
builder.add_edge("router", "llm_fallback")
builder.add_edge("get_time", END)
builder.add_edge("llm_fallback", END)

graph = builder.compile()

# Запуск имитации langgraph dev
if __name__ == "__main__":
    print("Starting dev mode...")
    print("Waiting for input... (type 'exit' to quit)\n")
    while True:
        msg = input("You: ")
        if msg.strip().lower() in {"exit", "quit"}:
            break
        result = graph.invoke({"user_input": msg})
        print("Bot:", result["output"])
