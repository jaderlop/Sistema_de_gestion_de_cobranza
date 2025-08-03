from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_prestamos():
    return {"mensaje": "Listado de cuotas"}