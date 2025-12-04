from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UploadResponse(BaseModel):
    filename: str
    file_path: str
    message: str
    document_id: Optional[str] = None

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 4

class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]

class RetrieveResponse(BaseModel):
    results: List[DocumentChunk]
