# 🧠 RAG Document Query System (Text-Based)

This is a **text-based Retrieval-Augmented Generation (RAG)** web application built with:

- **Flask** for the web interface
- **LangChain + ChromaDB** for vector storage and retrieval
- **OpenAI GPT-4o** for generating contextually grounded answers
- **Markdown** for rich answer formatting

Users can upload PDF documents, generate embeddings, and ask natural language questions. The system retrieves relevant textual chunks and generates accurate, cited responses grounded in your uploaded documents.

---

## 🚀 Features

- 📄 Upload one or more PDF documents to a **new or existing collection**
- 🧠 Ask **text-based** natural language questions
- 🔍 Retrieve and display relevant passages with **highlighted citations**
- ✨ View answers formatted in **Markdown**
- 🗃️ Works with **plain text extracted from PDFs**

> ⚠️ This system is **text-based** — it processes the textual content of PDFs (no image/OCR support).

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/rag-flask-app.git
cd rag-flask-app
```
### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Set environment variables
Create a .env file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```