# LocalClipInsight

## How it Works

The system ingests a directory of GoPro MP4 files, extracts visual embeddings using a lightweight CLIP model, stores them in a FAISS index, and provides a CLI to query moments by natural language. The top‑matched segments are trimmed and copied to a DaVinci Resolve project folder.

```mermaid
flowchart TD
    A[Start: Scan video folder] --> B[Extract frames (sampled)]
    B --> C[Generate CLIP embeddings]
    C --> D[Store embeddings in FAISS index]
    D --> E[User query (text)]
    E --> F[Retrieve top‑k similar embeddings]
    F --> G[Map to video timestamps]
    G --> H[Clip extraction & copy to Resolve folder]
    H --> I[Done]
```

![App Preview](assets/preview.jpg)

### Prerequisites
- Windows 10/11 (or WSL2) with Python 3.11
- M1‑class GPU or modern CPU (supports torch)

### Installation
```bat
setup_and_test.bat
```

### Usage
```bash
python cli.py search "sunny hill climb" --top 5
```

### Architecture Overview
The pipeline consists of three stages: **Ingestion**, **Indexing**, and **Query & Export**. Each stage is modular, enabling swapping of models or storage back‑ends without affecting the others.

---

## Development
Run tests with `pytest`.
