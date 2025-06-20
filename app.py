import os
import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOllama
from langchain_chroma import Chroma
import urllib.parse  # Add this import

# ---------------------------
# Configuración global
# ---------------------------
BASE_STATIC   = "./static"
PDF_FOLDER    = os.path.join(BASE_STATIC, "pdfs")
VECTOR_DIR    = "./vectorstores"
MODEL_NAME    = "gemma3:4b"

# Aseguramos carpetas
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

# Cache de retrievers
retriever_cache = {}

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Estado actual de la cadena
current_pdf   = None
current_chain = None

# ---------------------------
# Funciones auxiliares
# ---------------------------
def cargar_pdf_texto(path: str) -> str:
    # Normalize path for OS compatibility
    normalized_path = os.path.normpath(path)
    texto = ""
    doc = fitz.open(normalized_path)  # Use normalized path
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    return texto

def crear_vectorstore(pdf_name: str) -> Chroma:
    # Decode URL-encoded filename
    decoded_name = urllib.parse.unquote(pdf_name)
    pdf_path = os.path.normpath(os.path.join(PDF_FOLDER, decoded_name))
    
    # Validate PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    # Create safe directory name
    persist_dir = os.path.normpath(
        os.path.join(VECTOR_DIR, os.path.splitext(decoded_name)[0])
    )
    
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    
    texto = cargar_pdf_texto(pdf_path)
    doc   = Document(page_content=texto)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    chunks   = splitter.split_documents([doc])
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_dir)

def get_retriever(pdf_name: str):
    if pdf_name in retriever_cache:
        return retriever_cache[pdf_name]
    retr = crear_vectorstore(pdf_name).as_retriever()
    retriever_cache[pdf_name] = retr
    return retr

def setup_chain(pdf_name: str):
    global current_pdf, current_chain
    decoded_name = urllib.parse.unquote(pdf_name)
    
    if current_pdf != decoded_name:
        # Verify PDF exists before processing
        pdf_path = os.path.normpath(os.path.join(PDF_FOLDER, decoded_name))
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        retriever = get_retriever(decoded_name)
        llm       = ChatOllama(model=MODEL_NAME)
        memory    = ConversationBufferMemory(memory_key="chat_history",
                                             return_messages=True,
                                             output_key="answer")
        current_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=False
        )
        current_pdf = pdf_name

# ---------------------------
# FastAPI + CORS + Static
# ---------------------------
app = FastAPI()

@app.get("/list_pdfs")
async def list_pdfs():
    pdf_files = []
    for filename in os.listdir(PDF_FOLDER):
        if filename.lower().endswith(".pdf"):
            pdf_files.append(filename)
    return {"pdfs": pdf_files}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Ajusta si quieres restringir orígenes
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Montamos los estáticos en /static
app.mount("/static", StaticFiles(directory=BASE_STATIC), name="static")

# GET / → sirve index.html
@app.get("/")
async def home():
    return FileResponse(os.path.join(BASE_STATIC, "index.html"))

# ---------------------------
# Endpoint: subir PDF
# ---------------------------
@app.post("/uploadpdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Validación de extensión
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Solo se permiten archivos .pdf"})
    # Generar ruta de guardado
    filename = file.filename
    save_path = os.path.join(PDF_FOLDER, filename)
    # Evitar colisiones
    base, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(save_path):
        filename = f"{base}_{i}{ext}"
        save_path = os.path.join(PDF_FOLDER, filename)
        i += 1
    # Guardar
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"filename": filename}

# ---------------------------
# Endpoint: updateBackendPDF (opcional)
# ---------------------------
@app.post("/set_pdf")
async def set_pdf(req: Request):
    data = await req.json()
    if "pdf_name" not in data:
        return JSONResponse(status_code=400, content={"error":"Falta 'pdf_name'"})
    # Puedes hacer tracking si quieres
    return {"status":"ok"}

# ---------------------------
# Endpoint: chat
# ---------------------------
@app.post("/chat")
async def chat(req: Request):
    payload  = await req.json()
    message  = payload.get("message","").strip()
    history  = payload.get("history",[])
    pdf_name = payload.get("pdf_name","").strip()

    if not pdf_name:
        return JSONResponse(status_code=400, content={"error":"Falta 'pdf_name'"})
    if not message:
        return JSONResponse(status_code=400, content={"error":"El 'message' está vacío"})

    # (Re)configuramos la cadena si cambia de PDF
    setup_chain(pdf_name)

    try:
        # Ensure PDF exists before processing
        pdf_path = os.path.normpath(os.path.join(PDF_FOLDER, pdf_name))
        if not os.path.exists(pdf_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"PDF not found: {pdf_name}"}
            )
            
        setup_chain(pdf_name)
        result = current_chain({"question": message})
        answer = result["answer"]
    except Exception as e:
        print("Error en chain:", e)
        answer = "Lo siento, hubo un error procesando tu pregunta."

    history.append([message, answer])
    return {"history": history, "response": answer}

# ---------------------------
# Launch
# ---------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
