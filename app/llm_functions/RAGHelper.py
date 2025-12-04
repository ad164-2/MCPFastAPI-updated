
import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
from app.llm_functions.LLMDefination import get_embeddings

class RAGHelper:
    def __init__(self):
        self.upload_dir = settings.upload_directory
        self.vector_store_path = os.path.join(self.upload_dir, "chroma_db")
        # Initialize embeddings using the centralized definition
        self.embeddings = get_embeddings()

    def embed_documents(self, documents: List[Document]) -> int:
        """
        Splits and embeds documents into the vector store.
        Returns the number of chunks created.
        """
        # Split
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        # Embed and Store
        # Chroma handles persistence automatically if persist_directory is set
        Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings, 
            persist_directory=self.vector_store_path
        )
        return len(splits)

    def retrieve(self, query: str, top_k: int = 4) -> List[Document]:
        """
        Retrieves relevant documents for a given query.
        """
        if not os.path.exists(self.vector_store_path):
             return []
             
        vectorstore = Chroma(
            persist_directory=self.vector_store_path, 
            embedding_function=self.embeddings
        )
        return vectorstore.similarity_search(query, k=top_k)
