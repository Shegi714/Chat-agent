# Stateless Chat Agent — LangGraph

## 📌 Что делает

Простой агент, который:
- Возвращает текущее UTC время при вопросе "What time is it?"
- Во всех остальных случаях отвечает "What is my purpose?" на языке пользователя

## 🚀 Запуск

```bash
git clone <your_repo>
cd <your_repo>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
langgraph dev
