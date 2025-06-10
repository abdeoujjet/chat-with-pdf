# 📄 PDF Chatbot with Gradio + LangChain + Ollama + Chroma
This project is designed to store and maintain history between chats and PDFs, enabling users to keep contextual continuity when interacting with documents.

This project lets you **chat with PDF documents** using a local model (`gemma3:4b` via Ollama), embeddings from `sentence-transformers`, vector storage via ChromaDB, and a web interface built with Gradio. It features a split-screen view: the PDF on the left, the chatbot on the right.

---

## 🚀 What does this project do?

- 📂 **Loads PDFs** from a local folder.
- 📚 **Extracts and chunks text** from each PDF.
- 🧠 **Creates embeddings** with `sentence-transformers/all-MiniLM-L6-v2`.
- 💾 **Stores the vectors** in a persistent ChromaDB store.
- 🧵 **Maintains chat history** across interactions.
- 💬 **Lets you ask questions** about the documents content.
- 🌐 **Web UI** with PDF selector + viewer + chatbot.

---

## 🛠️ Requirements

- Python 3.10+
- Ollama models (`gemma3:4b`) pre-installed
- The following Python dependencies:

```bash
pip install -r requirements.txt
```
---


## 📁 Project Structure

```
.
├── pdfs/               # Folder containing the PDFs
├── vectorstores/       # Folder where Chroma vectorstores are saved
├── app.py              # Main script to run the Gradio server
├── index.html          # Web UI with PDF viewer + chatbot
├── config.py           # Folder and port settings
└── README.md           # This file
```

---

## ⚙️ Configuration

Create a file named `config.py` with:

```python
PDF_FOLDER = "./pdfs"
SERVER_PORT = 7860
```

Then place your PDF files in the `pdfs/` folder.

---

## ▶️ How to use

1. **Run the server**:

```bash
python app.py
```

---

## 📄 Adding New PDFs

To add a new PDF:

1.  Place your `.pdf` file in the `pdfs/` folder.
2.  Run the following command to regenerate the HTML index:
    ```bash
    python generate_index_html.py
    ```
    This script updates the dropdown menu in `index.html` so the new PDF appears in the list.

⚠️ **You must re-run `generate_index_html.py` every time you add a new PDF.**

If you don’t, the PDF won’t show up in the dropdown.

---


2. **Open the `index.html`** file in your browser:

```bash
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

3. **Select a PDF**, wait a few seconds for processing, and start chatting with your document.

---

## 🧠 How does it work?

- Upon selecting a PDF, the app builds or loads a persistent vectorstore.
- It uses LangChain's `ConversationalRetrievalChain` with memory.
- The LLM (`gemma3:4b`) runs **locally** via Ollama, no cloud APIs needed.

---

## 🤖 Model Used

The app uses the `gemma3:4b` model, run locally with Ollama via LangChain:

```python
MODEL = "gemma3:4b"  # You can replace this with another supported model
```

---

## ✨ Web Interface

The `index.html` file includes:

- A **PDF dropdown selector**
- A **built-in PDF viewer**
- A **Gradio iframe chatbot**

---

## 🧑‍💻 Author

Crafted with care by  **Abde Oujjet Moumen**  
[LinkedIn](https://www.linkedin.com/in/abde-oujjet-moumen-962402143/)
