# 🧠 RAG Document Query System (LangGraph Mirror)

This is a LangGraph-based mirror of the text-oriented Retrieval-Augmented Generation (RAG) web app.

- Flask for the web interface
- LangGraph + LangChain + ChromaDB for retrieval orchestration
- OpenAI GPT-4o for answer generation and structured citation extraction
- Markdown rendering for rich answers

## 🚀 Features
- Upload PDFs to a new or existing collection
- Ask questions against your document collections
- Retrieve relevant chunks and generate answers with quoted citations
- Identical UI to the original project

## 🛠️ Setup
1. Create a virtual environment and install requirements:
```bash
pip install -r requirements.txt
```
2. Set environment variables in a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```
3. Run the app:
```bash
python app.py
```

The app runs at `http://127.0.0.1:5000/` by default.