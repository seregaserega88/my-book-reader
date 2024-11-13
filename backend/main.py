from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем доступ с любого источника
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BOOKS_DIR = "uploaded_books"
os.makedirs(BOOKS_DIR, exist_ok=True)

class User(BaseModel):
    username: str
    password: str

users = []

@app.post("/register")
def register(user: User):
    for existing_user in users:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already exists")
    users.append({"username": user.username, "password": user.password})
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: User):
    for existing_user in users:
        if existing_user["username"] == user.username and existing_user["password"] == user.password:
            return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/upload-book")
async def upload_book(file: UploadFile = File(...)):
    file_path = os.path.join(BOOKS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Book uploaded successfully", "filename": file.filename}

@app.get("/read-book/{filename}")
async def read_book(filename: str):
    file_path = os.path.join(BOOKS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Book not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
