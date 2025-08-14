flowchart LR
  subgraph User["User (Client / L1 / L2 / L3 / Admin)"]
    UI["Streamlit UI (black & white)"]
  end

  subgraph Frontend["frontend (Docker)"]
    UI
  end

  subgraph Backend["backend (FastAPI, Docker)"]
    API["REST API (auth, controls, evidence, approvals)"]
    DB[(Postgres)]
    Files[("uploads/ (bind mount)")]
  end

  subgraph AI["ai_service (FastAPI, Docker)"]
    RAG["RAG Orchestrator"]
    EMB["Sentence-Transformers\n(all-MiniLM-L6-v2)"]
    QD[(Qdrant Vector DB)]
    MLF["MLflow Tracking"]
  end

  subgraph Host["Host macOS"]
    OLL["Ollama (mistral / llama3.1)"]
  end

  UI -->|HTTPS JSON| API
  API <-->|JSON| RAG
  API --- DB
  API --- Files

  RAG -->|Embeddings| EMB
  EMB -->|Upsert/Search| QD
  RAG -->|Retrieve| QD
  RAG -->|Prompt/Completion| OLL
  RAG -->|log params/artifacts| MLF
