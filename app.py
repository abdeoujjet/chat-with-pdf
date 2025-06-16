import os
import gradio as gr
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOllama
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain_chroma import Chroma

PDF_FOLDER = "./pdfs"
VECTOR_DIR_BASE = "./vectorstores"
MODEL = "gemma3:4b"

retriever_cache = {}
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def cargar_pdf_texto(pdf_path):
    import fitz
    texto_completo = ""
    doc = fitz.open(pdf_path)
    for pagina in doc:
        texto_completo += pagina.get_text()
    doc.close()
    return texto_completo

def crear_vectorstore(pdf_name):
    pdf_path = os.path.join(PDF_FOLDER, pdf_name)
    persist_dir = os.path.join(VECTOR_DIR_BASE, pdf_name.replace(".pdf", ""))

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        vect_store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    else:
        texto_pdf = cargar_pdf_texto(pdf_path)
        documento = Document(page_content=texto_pdf)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
        chunks = splitter.split_documents([documento])
        os.makedirs(persist_dir, exist_ok=True)
        vect_store = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_dir)

    return vect_store

def load_retriever_for_pdf(pdf_name):
    if pdf_name in retriever_cache:
        return retriever_cache[pdf_name]
    vect_store = crear_vectorstore(pdf_name)
    retriever = vect_store.as_retriever()
    retriever_cache[pdf_name] = retriever
    return retriever

# Estado global
current_pdf = None
current_chain = None

def setup_chain(pdf_name):
    global current_pdf, current_chain
    
    if current_pdf != pdf_name:
        print(f"🔄 Cambiando a: {pdf_name}")
        
        retriever = load_retriever_for_pdf(pdf_name)
        llm = ChatOllama(model=MODEL)
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        current_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=False
        )
        
        current_pdf = pdf_name
        print(f"✅ Configurado para: {pdf_name}")



def chat_function(message, history):
    """Función de chat ultra simple"""
    if not history or not isinstance(history, list):
        history = []

    if not message:
        return history, ""
    
    pdf_name = "Produccion_Nuevo_Gemelo.pdf"
    setup_chain(pdf_name)

    try:
        result = current_chain({"question": message})
        response = result["answer"]
        history.append([message, response])
        return history, ""
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        history.append([message, error_msg])
        return history, ""


# Interface usando solo gr.Interface (más simple que gr.Blocks)
def launch_simple():
    print("✅ Lanzando versión ultra-simple...")
    
    iface = gr.Interface(
        fn=lambda msg, hist: chat_function(msg, hist),
        inputs=[
            gr.Textbox(placeholder="Escribe tu pregunta..."),
            gr.State(value=[])
        ],
        # outputs=gr.Chatbot(),
        outputs=[
            gr.Chatbot(),
            gr.State()
        ],

        title="Chat con PDF - Versión Simple",
        description="Haz preguntas sobre el PDF"
    )
    
    # iface.launch(server_name="127.0.0.1", server_port=7860)
    iface.launch(server_name="0.0.0.0", server_port=7860, share=True)

if __name__ == "__main__":
    launch_simple()