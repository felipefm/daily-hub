"""
Configuração do pytest para os testes da aplicação Daily-HUB.
Define fixtures compartilhadas, setup e teardown.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
import sys
import os
from datetime import datetime
import logging

# Adiciona o diretório da app ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import Base, get_db
from main import app

# Configuração de logging
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Adicione esta linha
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    """Fixture que fornece uma sessão de banco de dados limpa para cada teste."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Fixture que fornece um cliente TestClient para fazer requisições HTTP."""
    return TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Setup inicial dos logs."""
    logger.info("=" * 80)
    logger.info(f"INICIANDO SUITE DE TESTES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    yield
    logger.info("=" * 80)
    logger.info(f"FINALIZANDO SUITE DE TESTES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Arquivo de log salvo em: {log_file}")
    logger.info("=" * 80)

@pytest.fixture
def test_logger():
    """Fixture que fornece um logger para testes individuais."""
    return logger
