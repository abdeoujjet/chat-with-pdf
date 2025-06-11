import os
from urllib.parse import urlparse, parse_qs

import gradio as gr
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.schema.messages import AIMessage, HumanMessage
from langchain_community.chat_models import ChatOllama
from langchain_chroma import Chroma

PDF_FOLDER = "./pdfs"
VECTOR_DIR_BASE = "./vectorstores"
MODEL = "gemma3:4b"

retriever_cache = {}
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def cargar_pdf_texto(pdf_path):
    import fitz  # PyMuPDF
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


def chatbot_interface(message, history, request: gr.Request):
    """
    Processes a user message, interacts with the RAG chain, and returns the AI's response.

    Args:
        message (str): The user's input message.
        history (list[list[str, str]]): The conversation history in Gradio's format.
        request (gr.Request): The Gradio request object to access HTTP headers.

    Returns:
        str: The AI's response message.
    """
    if not message:
        return ""

    # 1. Get PDF name from the request URL
    referer = request.headers.get("referer", "")
    parsed = urlparse(referer)
    query_params = parse_qs(parsed.query)
    pdf_name = query_params.get("pdf", ["Produccion_Nuevo_Gemelo.pdf"])[0]

    retriever = load_retriever_for_pdf(pdf_name)
    llm = ChatOllama(model=MODEL)

    # 2. Convert Gradio's history (list of lists) to LangChain's ChatMessageHistory
    message_history = ChatMessageHistory()
    for user_msg, ai_msg in history:
        message_history.add_user_message(user_msg)
        message_history.add_ai_message(ai_msg)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        return_messages=True,
    )

    # 3. Create the conversational chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )

    # 4. Get the answer from the chain
    result = conversation_chain.invoke({"question": message})
    answer = result["answer"]

    # 5. Return only the string response.
    # gr.ChatInterface handles history management in the UI automatically.
    return answer

def launch_chat():
    """Launches the Gradio Chat Interface."""
    print("🚀 Server started at http://localhost:7860")
    demo = gr.ChatInterface(
        fn=chatbot_interface,
        # No additional_inputs needed for gr.Request
        title="Chat with your PDF",
        description="Select a PDF and start chatting."
    )
    demo.launch(server_port=7860, share=False)



if __name__ == "__main__":
    launch_chat()
