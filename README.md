<div align="center">

# سُمود | Sumud AI

### *Be Sumud in your life.*

**Sumud (صمود) means steadfastness in Arabic.**  
Keep going even when it's hard. Keep applying even when it's slow.

[![MIT License](https://img.shields.io/badge/License-MIT-C8102E?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?style=for-the-badge)](https://trychroma.com)

🇵🇸 Built with Palestinian pride — watermelon colors intentional 🍉

</div>

---

## What is Sumud AI?

Sumud AI is a personal AI-powered job seeker assistant that knows your **whole profile**.

Most AI tools know a fragment of who you are — what you type in that session. Sumud AI knows your entire story because you feed it your career documents upfront. The more you feed it, the more accurate and personalized every output becomes.

**You feed it your files → it learns your story → it helps you apply smarter.**

---

## The Problem It Solves

I was living alone in Germany, handling rent and daily life while trying to apply for jobs in my field at the same time. I didn't have enough hours in the day to write a tailored cover letter for every application.

So I built something to do it for me.

---

## Features

| Feature | Description |
|---|---|
| 🎯 **Job Fit Scorer** | Paste any job description — get a fit score (0–100), matching points, skill gaps, fit category, and reasoning |
| ✉️ **Cover Letter Generator** | Tailored cover letter per job, generated from your actual profile data, editable before use |
| 💬 **Chat Assistant** | RAG-powered Q&A grounded in your stored documents with persistent conversation history |
| 📄 **Document Ingestion** | Upload PDF, DOCX, TXT, or MD files directly from the browser with drag and drop |
| 👁️ **CV Preview** | Upload your CV once, view it as a PDF preview inside the app |
| ⚙️ **Preferences** | Store your job preferences once — used automatically in every scoring request |

---

## How It Works

```
You upload your documents (CV, cover letters, projects, certifications)
                    ↓
Sumud AI chunks, embeds, and stores them in a vector database
                    ↓
You paste a job description
                    ↓
The system finds the most relevant parts of YOUR story
                    ↓
Scores your fit + generates a tailored cover letter
```

This is a **RAG (Retrieval Augmented Generation)** system — built from scratch without LangChain or LlamaIndex.

---

## Tech Stack

### Backend
- **Python 3.13** — core language
- **FastAPI** — REST API framework
- **ChromaDB Cloud** — vector database for semantic search
- **Nomic** — embedding model (nomic-embed-text-v1.5)
- **OpenAI-compatible API** — LLM integration (Groq / Gemini)
- **pypdf + python-docx** — document parsing

### Frontend
- **React** — UI framework
- **Tailwind CSS** — styling
- **Vite** — build tool
- **Axios** — API communication

### Architecture
```
Frontend (React + Tailwind)
        ↓
FastAPI Backend (/api/v1)
  ├── /scorer              → job fit scoring
  ├── /cover-letter        → cover letter generation
  ├── /chat                → conversational assistant
  ├── /ingest-document     → document ingestion pipeline
  ├── /upload-cv           → CV storage and preview
  ├── /get-cv              → retrieve stored CV
  ├── /get-documents       → list stored documents
  ├── /get-records-count   → knowledge base stats
  └── /preferences         → user job preferences
        ↓
ChromaDB Cloud (vector storage)
        ↓
LLM API (generation)
```

---

## Project Structure

```
sumud-ai/
├── main.py                      ← FastAPI entry point
├── requirements.txt
├── LICENSE
├── README.md
│
├── routers/                     ← API endpoint definitions
│   ├── scorer.py
│   ├── cover_letter.py
│   ├── chat.py
│   ├── documents.py             ← ingest_document, upload_cv, get_cv, get_documents, get_records_count
│   ├── preferences.py
│   └── initialize_router.py
│
├── business_logic/              ← core AI logic
│   ├── scorer_logic.py
│   ├── cover_letter_logic.py
│   ├── chat_logic.py
│   ├── preferences_logic.py
│   └── llm.py                  ← all LLM calls (scorer, cover letter, chat)
│
├── data_access/                 ← database and document layer
│   ├── db.py                   ← ChromaDB client and collections
│   ├── embeddings.py           ← get_embedding, store, search
│   └── document_reader.py      ← read_document, chunk_text
│
├── config/                      ← configuration
│   ├── client.py               ← API client initialization
│   └── prompts.py              ← all prompt templates
│
└── frontend/                    ← React application
    └── src/
        ├── pages/
        │   ├── Dashboard.jsx
        │   ├── JobScorer.jsx
        │   ├── Chat.jsx
        │   ├── Spinner.jsx
        │   └── Settings.jsx
        ├── components/
        │   ├── layout/
        │   │   ├── Layout.jsx
        │   │   └── Sidebar.jsx
        └── services/
            └── api.js
```

---

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- [ChromaDB Cloud](https://trychroma.com) account (free)
- [Groq API key](https://console.groq.com) (free)
- [Nomic API key](https://nomic.ai) (free)

### 1. Clone the repository

```bash
git clone https://github.com/Ahmad812002/sumud-ai.git
cd sumud-ai
```

### 2. Backend setup

```bash
# Create virtual environment
python -m venv ENV_DIR
ENV_DIR\Scripts\activate     # Windows
source ENV_DIR/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Fill in your API keys
```

### 3. Environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
NOMIC_API_KEY=your_nomic_api_key
CHROMA_API_KEY=your_chromadb_api_key
CHROMA_TENANT=your_chromadb_tenant_id
CHROMA_DATABASE=your_database_name
```

### 4. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_BASE_URL=http://localhost:8000
```

### 5. Run the application

```bash
# Terminal 1 — Backend
uvicorn main:app --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Usage Guide

**Step 1 — Add your documents**

Go to Settings → drag and drop your CV, cover letters, project descriptions, and career files. The more you add, the more accurate the system becomes.

**Step 2 — Set your preferences**

Tell the system what you're looking for — remote, full-time, location, contract type.

**Step 3 — Score a job**

Go to Job Scorer → paste any job description → get your fit score, matching points, gaps, and reasoning.

**Step 4 — Generate a cover letter**

After scoring, click Generate Cover Letter → edit the result → copy to clipboard.

**Step 5 — Chat**

Ask anything about your career — the assistant answers from your stored documents.

---

## Known Issues & Roadmap

### Current Limitations
- **Single user** — no authentication, designed for personal use
- **ChromaDB async** — preferences update has a known async conflict with FastAPI's event loop (fix in progress)
- **Local only** — cloud deployment coming soon

### Roadmap
- [ ] Fix ChromaDB async conflict
- [ ] PDF cover letter download
- [ ] Authentication and multi-user support
- [ ] Cloud deployment with live demo URL
- [ ] Mobile responsive improvements

---

## Contributing

Sumud AI is actively looking for collaborators. If you're interested in contributing to an AI job seeker platform, reach out.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## Built By

**Ahmad Jaber** — CS Graduate (B.Sc. Informatik, German Jordanian University)

Self-directed AI engineering journey — built this while actively job searching in Germany.

- 📧 ahmad812002@gmail.com
- 💼 [LinkedIn](https://www.linkedin.com/in/ahmadjabr81)
- 🐙 [GitHub](https://github.com/Ahmad812002)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🇵🇸 Free Palestine**

*Sumud — صمود — steadfastness*

</div>
