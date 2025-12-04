import os
import shutil
from typing import List
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_core.documents import Document
from app.llm_functions.RAGHelper import RAGHelper

class DocumentService:
    def __init__(self):
        self.upload_dir = settings.upload_directory
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
        self.rag_helper = RAGHelper()

    async def save_file(self, file: UploadFile) -> str:
        file_path = os.path.join(self.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path

    async def parse_document(self, file_path: str) -> List[Document]:
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext == ".txt":
                loader = TextLoader(file_path)
            elif ext == ".csv":
                loader = CSVLoader(file_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
            
            return loader.load()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

    async def process_and_embed(self, file: UploadFile):
        # 1. Save file
        file_path = await self.save_file(file)
        
        # 2. Parse
        documents = await self.parse_document(file_path)
        
        # 3. Embed and Store (Delegated to RAGHelper)
        num_chunks = self.rag_helper.embed_documents(documents)
        
        return file_path, num_chunks

    async def retrieve(self, query: str, top_k: int = 4) -> List[Document]:
        # Delegated to RAGHelper
        return self.rag_helper.retrieve(query, top_k)
