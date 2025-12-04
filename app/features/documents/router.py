from fastapi import APIRouter, UploadFile, File, HTTPException
from app.features.documents.service import DocumentService
from app.features.documents.schemas import UploadResponse, RetrieveRequest, RetrieveResponse, DocumentChunk

router = APIRouter(tags=["Documents"])
service = DocumentService()

@router.post("/documents/upload/storage", response_model=UploadResponse)
async def upload_to_storage(file: UploadFile = File(...)):
    """
    Upload a document to storage without embedding.
    """
    try:
        file_path = await service.save_file(file)
        return UploadResponse(
            filename=file.filename,
            file_path=file_path,
            message="File uploaded successfully to storage"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/upload/embed", response_model=UploadResponse)
async def upload_and_embed(file: UploadFile = File(...)):
    """
    Upload a document, parse it, and store its embeddings.
    """
    try:
        file_path, chunks_count = await service.process_and_embed(file)
        return UploadResponse(
            filename=file.filename,
            file_path=file_path,
            message=f"File uploaded and embedded successfully. Created {chunks_count} chunks."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/retrieve", response_model=RetrieveResponse)
async def retrieve_documents(request: RetrieveRequest):
    """
    Retrieve relevant document chunks based on a query.
    """
    try:
        results = await service.retrieve(request.query, request.top_k)
        chunks = [
            DocumentChunk(content=doc.page_content, metadata=doc.metadata) 
            for doc in results
        ]
        return RetrieveResponse(results=chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
