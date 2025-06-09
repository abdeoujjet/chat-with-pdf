import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings as HFEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import gradio as gr

# Cargar variables de entorno
from config import PDF_FILENAME, SERVER_PORT
load_dotenv()

def cargar_pdf(path_pdf):
    texto_completo = ""
    doc = fitz.open(path_pdf)
    for pagina in doc:
        texto_completo += pagina.get_text()
    doc.close()
    return texto_completo


def crear_vectorstore(texto, db_name="ChatVectors"):
    documento = Document(page_content=texto)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    chunks = text_splitter.split_documents([documento])

    embeddings = HFEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if os.path.exists(db_name):
        Chroma(persist_directory=db_name, embedding_function=embeddings).delete_collection()

    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_name)
    return vectorstore


def configurar_chain(vectorstore):
    llm = ChatOllama(model="gemma3:4b")
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    retriever = vectorstore.as_retriever()
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)
    return chain


def chat(message, history):
    result = conversation_chain.invoke({"question": message})
    return result["answer"]


# ============================
if __name__ == "__main__":
    # Cargar y procesar el PDF
    pdf_path = f"{PDF_FILENAME}.pdf"
    texto_pdf = cargar_pdf(pdf_path)
    vectorstore = crear_vectorstore(texto_pdf)

    # Crear la cadena conversacional
    conversation_chain = configurar_chain(vectorstore)

    # Crear la interfaz de Gradio
    view = gr.ChatInterface(chat, type="messages")
    view.launch(
        inbrowser=False,
        share=False,
        server_name="0.0.0.0",
        server_port=SERVER_PORT
    )
