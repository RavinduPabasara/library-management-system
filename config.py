import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Data directory
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
BOOKS_CSV_PATH = DATA_DIR / "books.csv"
USERS_CSV_PATH = DATA_DIR / "users.csv"

# RAG Vector Store path
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# Simple check for placeholder .env value
# In real app, you might add more robust checks or default values
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-...":
    print("Warning: OPENAI_API_KEY is not set or is using the placeholder value in .env")
    # Optionally, you could raise an error or exit here
    # raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env")

# --- Add other configurations as needed ---
# Example: RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150