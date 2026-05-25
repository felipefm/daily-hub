from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os

# Importa o 'engine' do SQLAlchemy para podermos gerenciar as conexões
from database import engine

router = APIRouter(prefix="/backup", tags=["Backup"])

# O caminho para o arquivo do banco de dados.
# Assumindo que o app roda de dentro do diretório /app, e o DB está na raiz do projeto.
DB_PATH = "daily_hub.db"

@router.get("/export", summary="Exporta o banco de dados")
def export_backup():
    """
    Força o download do arquivo do banco de dados (daily_hub.db).
    """
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Arquivo de banco de dados não encontrado.")
    
    return FileResponse(
        path=DB_PATH,
        filename="daily_hub.db",
        media_type="application/vnd.sqlite3" # Mime type específico para sqlite
    )

@router.post("/import", summary="Importa um banco de dados")
async def import_backup(file: UploadFile = File(...)):
    """
    Recebe um arquivo .db/.sqlite, valida, e substitui o banco de dados atual.
    """
    # 1. Valida a extensão do arquivo
    if not file.filename.endswith(('.db', '.sqlite')):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Por favor, envie um arquivo .db ou .sqlite.")

    # 2. Encerra todas as conexões ativas no pool do SQLAlchemy.
    # Este é um passo CRÍTICO para evitar corrupção ao substituir o arquivo.
    engine.dispose()

    # 3. Substitui o arquivo de banco de dados
    try:
        with open(DB_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    # Na próxima requisição, o SQLAlchemy criará novas conexões para o novo arquivo.
    return {
        "detail": "Backup importado com sucesso! A aplicação agora utilizará o novo banco de dados."
    }