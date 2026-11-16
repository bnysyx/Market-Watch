
# 📈 Financial AI Agent

An autonomous financial assistant built with Streamlit and LangChain. This agent leverages open-source LLMs (via Groq) to autonomously fetch, analyze, and visualize stock market data without hallucinating financial figures.

## 🚀 Features

- **Autonomous Tool Chaining:** Uses strictly defined "Agentic Docstrings" to ensure the AI correctly chains metadata and time-series data.
- **Anti-Hallucination Engine:** A strict system prompt forces the model to rely solely on local tabular data, preventing it from estimating or inventing financial metrics.
- **Dual-Memory State Management:** Translates Streamlit/LangChain by connecting two separate memory states: one for UI rendering (dictionaries) and one for the AI's internal context (tuples).
- **Local Data Pipeline:** Downloads stock data via `yfinance`, processes technical indicators using Pandas, and generates dynamic `matplotlib` charts saved locally to a `data/` directory.
- **Dynamic Markdown UI:** Renders inline tables, key highlights, and local `.png` charts directly in a conversational chat interface.

## 🧠 Tech Stack

- **Frontend:** Streamlit
- **LLM Orchestration:** LangChain (Agents & Tools)
- **Model Provider:** Groq
- **Data & APIs:** `yfinance`, Yahoo Finance News Tool
- **Data Processing & Vis:** Pandas, Matplotlib

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/financial-ai-agent.git](https://github.com/yourusername/financial-ai-agent.git)
   cd financial-ai-agent
   ```
