#!/bin/bash
pip install --no-cache-dir fastapi uvicorn sqlalchemy requests pydantic python-multipart
uvicorn main:app --host 0.0.0.0 --port 8000 --reload