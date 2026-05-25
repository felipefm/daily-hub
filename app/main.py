from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import models
from database import engine

# 1. Adicione a importação do calendar_generator aqui
from routers import tasks, analysis, calendar_generator, backup, routines
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily-HUB API", version="1.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(tasks.router)
app.include_router(analysis.router)
app.include_router(routines.router)

# 2. Engate o roteador de impressão
app.include_router(calendar_generator.router)
# 3. Engate o roteador de backup
app.include_router(backup.router)

@app.get("/")
def read_root():
    return FileResponse("static/index.html")