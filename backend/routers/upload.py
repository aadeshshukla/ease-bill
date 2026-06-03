from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    return {"filename": file.filename, "status": "uploaded"}
