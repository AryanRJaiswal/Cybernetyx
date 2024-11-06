from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import os
from io import StringIO
from PyPDF2 import PdfReader
from docx import Document

app = FastAPI()
client = chromadb.Client()
collection = client.create_collection("documents")
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

def extract_text_from_txt(file):
    text = file.read().decode("utf-8")
    return text

class DocumentRequest(BaseModel):
    text: str
    metadata: dict

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...), metadata: str = Form(...)):
    try:
        metadata_dict = eval(metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid metadata format")
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file.file)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file.file)
    elif filename.endswith(".txt"):
        text = extract_text_from_txt(file.file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    embedding = model.encode(text)
    doc_id = str(uuid.uuid4())
    collection.add(documents=[text], metadatas=[metadata_dict], embeddings=[embedding], ids=[doc_id])
    return JSONResponse(content={"message": "Document ingested successfully", "document_id": doc_id})

@app.get("/query")
async def query_document(query: str):
    query_embedding = model.encode(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    structured_results = []
    for doc, meta in zip(results['documents'], results['metadatas']):
        structured_results.append({"document": doc, "metadata": meta})
    return {"results": structured_results}
