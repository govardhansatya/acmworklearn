from langchain.vectorstores import FAISS
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

def build_vectorstore_from_docs(docs: list[str], persist_path: str = "data/faiss_index"):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)
    splits = text_splitter.create_documents(docs)
    vectorstore = FAISS.from_documents(splits, embedding=embedding_model)
    vectorstore.save_local(persist_path)
    return vectorstore

def load_vectorstore(persist_path: str = "data/faiss_index"):
    return FAISS.load_local(persist_path, embedding_model)
