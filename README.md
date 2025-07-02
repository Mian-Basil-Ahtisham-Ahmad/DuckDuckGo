# 🔍 AI-Powered Unified DuckDuckGo Search Engine

A smart, multi-modal search app built using **Streamlit**, powered by **DuckDuckGo Search API** and enhanced with **Google Gemini Embeddings** via LangChain.

This app allows users to:
- Search across **Text**, **Images**, **Videos**, and **GIFs**
- Apply **semantic ranking** on text results using Gemini embeddings
- View and **export results to CSV**
- Preview and open result links in-browser

---

## 🚀 Features

✅ Unified interface to search:
- 📄 Text  
- 🖼️ Images  
- 📹 Videos  
- 🎞️ GIFs

✅ Optional **Semantic Search** (requires Gemini API)  
✅ CSV Export of results  
✅ Gemini Embedding support using `langchain-google-genai`  
✅ Clean and responsive **Streamlit UI**

---

## 🛠️ Tech Stack

- `streamlit` – frontend UI
- `duckduckgo_search` – API-based search
- `langchain-google-genai` – Gemini 1.5 Embedding support
- `dotenv` – secure API key management
- `BeautifulSoup`, `requests` – for content fetching and parsing
- `pandas`, `numpy` – result manipulation and similarity scoring

---

## 🧠 Semantic Search (Optional)

If enabled, the app:
1. Embeds your query using Gemini’s embedding model  
2. Embeds the search result content (title/description/body)  
3. Ranks results based on **cosine similarity**

> Requires a Google Gemini API key with access to `models/embedding-001`.

---

## 🔧 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/unified-duckduckgo-search.git
cd unified-duckduckgo-search
