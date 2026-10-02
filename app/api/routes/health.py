from fastapi import APIRouter  

router = APIRouter()


@router.get("/health")
def health():
    return {
        "success": True,
        "message": "ERP AI Agent is running"
    }