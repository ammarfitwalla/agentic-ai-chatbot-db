# 🤖 Agentic AI Customer Database Chatbot

An intelligent agent that allows you to query your customer database using natural language. Built with **LangGraph**, **LangChain**, and **Ollama**.

## 🌟 Features

- **Natural Language to SQL**: Ask questions like *"How many customers are in the UK?"* or *"Show me the latest subscribers"* and get instant answers.
- **Conversation Memory**: Remembers previous questions for follow-up queries (e.g., *"Filter those by city"*).
- **Streaming Interface**: Real-time response generation in the terminal for a smoother experience.
- **Safety First**: Uses read-only database connections and is restricted to `SELECT` queries only.
- **Local & Private**: Powered by **Ollama**, ensuring your data stays on your machine.

## 🛠️ Technology Stack

- **Core Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) & [LangChain](https://github.com/langchain-ai/langchain)
- **AI Model**: Qwen 2.5 / Llama 3.1 (via Ollama)
- **Database**: SQLite
- **Language**: Python 3.10+

## 🚀 Getting Started

### 1. Prerequisites

- **Python**: Version 3.10 or higher.
- **Ollama**: Install from [ollama.com](https://ollama.com) and pull the required model:
  ```bash
  ollama pull qwen3:8b  # or the model specified in ai_config.py
  ```

### 2. Installation

Clone the repository and install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Running the Chatbot

Start the interactive terminal session:

```bash
python main.py
```

## 📂 Project Structure

- `main.py`: Entry point for the terminal chat loop.
- `query_engine.py`: Core logic for the LangGraph agent and SQL tool integration.
- `ai_config.py`: Centralized configuration for AI providers and model settings.
- `customer_db.db`: SQLite database containing customer records.

## 💡 Example Queries

- *"How many total customers do we have?"*
- *"Show me the top 5 companies by customer count."*
- *"Who are the latest 10 subscribers?"*
- *"Find all customers living in London."*
- *"What is the email of John Doe?"*

## ⚙️ Configuration

You can easily switch models or adjust agent behavior in `ai_config.py`:

```python
class AIConfig:
    PROVIDER = 'ollama'
    OLLAMA_MODEL = 'qwen2.5:7b'
    MAX_RESULTS = 50
    MEMORY_WINDOW = 3
```

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
