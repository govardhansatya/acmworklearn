import faiss
import numpy as np
import os
import pickle
import google.generativeai as genai
from config.settings import GEMINI_API_KEY
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

genai.configure(api_key=GEMINI_API_KEY)

# Embedding Generator
def get_gemini_embedding(text: str) -> List[float]:
    model = genai.GenerativeModel("embedding-001")
    response = model.embed_content(content=text, task_type="RETRIEVAL_QUERY")
    return response["embedding"]

# Document Chunking
def chunk_document(doc: str, chunk_size=500, overlap=50) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(doc)

# FAISS Storage Path
FAISS_DIR = "memory/faiss_index"
os.makedirs(FAISS_DIR, exist_ok=True)

# FAISS Wrapper
class GeminiFAISSStore:
    def __init__(self, dim=768, index_file=f"{FAISS_DIR}/index.pkl"):
        self.index_file = index_file
        self.index = faiss.IndexFlatL2(dim)
        self.doc_map = []
        if os.path.exists(index_file):
            self.load()

    def add_docs(self, docs: List[str]):
        embeddings = [np.array(get_gemini_embedding(doc), dtype=np.float32) for doc in docs]
        self.index.add(np.array(embeddings))
        self.doc_map.extend(docs)
        self.save()

    def search(self, query: str, k=5):
        query_vec = np.array([get_gemini_embedding(query)], dtype=np.float32)
        D, I = self.index.search(query_vec, k)
        return [self.doc_map[i] for i in I[0]]

    def save(self):
        with open(self.index_file, "wb") as f:
            pickle.dump((self.index, self.doc_map), f)

    def load(self):
        with open(self.index_file, "rb") as f:
            self.index, self.doc_map = pickle.load(f)
