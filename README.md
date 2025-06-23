# PDF ChatBot with Gradio, LangChain, Ollama, and Chroma

## Overview

This project showcases an interactive PDF chatbot interface built using Gradio. The application leverages LangChain for PDF
processing and embeddings from `sentence-transformers`, while ChromaDB is used for vector storage. The result is a split-screen
interface with the PDF on one side and the chatbot on the other, enabling engaging document interactions.


---
![Screenshot_3](https://github.com/user-attachments/assets/0f34fca1-40a4-434d-a88c-70878dd9bd95)

---
![Screenshot_2](https://github.com/user-attachments/assets/058b8a8f-8a31-4518-87eb-b9e6adbec697)
---

## What Does This Project Do?

- **Loads PDFs** automatically from a local folder
- **Extracts and Chunks Text** from each PDF
- **Creates Embeddings** using `sentence-transformers/all-MiniLM-L6-v2`
- **Stores Vectors** in a persistent ChromaDB store
- **Enables Question Answering** about the document content
- **Maintains Chat History** across interactions for each PDF
- Provides a **Web Interface** with a PDF selector, viewer, and chatbot

## Requirements

- Python 3.10+
- Ollama (with `gemma3:4b` model installed)
- Required Python dependencies:

```bash
pip install -r requirements.txt
```

### Project Structure

```
.
├── static/          # Folder for PDF documents
├──── index.html     # Web interface
├──── pdfs/          # Folder for PDF documents
├── vectorstores/  # Auto-generated ChromaDB stores
├── ChatVectors/   # Auto-generated store of vectors to speed the setup
├── app.py         # Main Gradio server script
├── requirements.txt 
├── config.py      # Configuration settings
├── generate_index_html.py  # Generates the html (not necessary)
├── Dockerfile
├── docker-compose.yml
└── README.md   # Project documentation
```

### Configuration

Create a `config.py` file in the root directory:

```python
PDF_FOLDER = "./pdfs"
SERVER_PORT = 7860
```

Place your PDF files into the `pdfs/` folder.

## How to Use

1. **Run the Server:**

   ```bash
   python app.py
   ```

2. **Access the Interface:**

   The server starts at `http://localhost:7860`. Open `index.html` in your browser:


3. **Interact with the Chatbot:**

   Select a PDF, wait for processing (the firs time initial load may take longer), and start chatting!

## Adding New PDFs

1. Place your `.pdf` file into the `pdfs/` folder.
2. Regenerate the HTML index:

   ```bash
   python generate_index_html.py
```

**Important:** Run this script every time you add a new PDF; otherwise, it won't appear in the dropdown.

## How It Works

1. **PDF Processing:** When a PDF is selected, the app either builds a new vector store or loads an existing one from
`vectorstores/`.
2. **Chat Management:** LangChain's ConversationalRetrievalChain handles interactions, maintaining context and history.
3. **Local Inference:** The gemma3:4b model runs locally via Ollama, eliminating the need for external APIs.

## Model Used

The application uses the `gemma3:4b` model:

```python
MODEL = "gemma3:4b"  # Replace with another supported Ollama model if desired
```

## Web Interface Features

- **PDF Dropdown:** Easily switch between documents.
- **PDF Viewer:** Built-in viewer for document navigation.
- **Chat Integration:** Seamless interaction with the Gradio chatbot.
- **Mobile-Friendly:** Responsive design for device versatility.

## Author

Crafted by Abde Oujjet Moumen with care and precision.

[LinkedIn Profile](https://www.linkedin.com/in/abde-oujjet-moumen-962402143?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
