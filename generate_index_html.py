import os
from config import PDF_FOLDER, SERVER_PORT

# Obtener lista de PDFs
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

# HTML con selector de PDF
options_html = "\n".join([f'<option value="{PDF_FOLDER}/{file}">{file}</option>' for file in pdf_files])

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PDF Viewer & Chatbot</title>
<style>
  body, html {{
    margin: 0; padding: 0; height: 100%;
    font-family: Arial, sans-serif;
  }}
  .container {{
    display: flex;
    height: 100vh;
    width: 100vw;
  }}
  .left-pane {{
    flex: 1;
    border-right: 2px solid #ddd;
    display: flex;
    flex-direction: column;
  }}
  .left-pane header {{
    background-color: #4a90e2;
    color: white;
    padding: 10px;
    font-size: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .pdf-viewer {{
    flex-grow: 1;
    width: 100%;
    border: none;
  }}
  .right-pane {{
    flex: 1;
    display: flex;
    flex-direction: column;
  }}
  .right-pane header {{
    background-color: #4a90e2;
    color: white;
    padding: 10px;
    font-size: 1.2rem;
  }}
  iframe.chat-iframe {{
    flex-grow: 1;
    border: none;
    width: 100%;
  }}
  select {{
    font-size: 1rem;
    padding: 5px;
    margin-left: 10px;
  }}
  @media (max-width: 800px) {{
    .container {{
      flex-direction: column;
    }}
    .left-pane, .right-pane {{
      flex: unset;
      height: 50vh;
    }}
  }}
</style>
<script>
  function changePDF(select) {{
    const pdfViewer = document.getElementById("pdfViewer");
    pdfViewer.src = select.value;
    localStorage.setItem("lastPDF", select.value);
  }}

  window.onload = function() {{
    const lastPDF = localStorage.getItem("lastPDF");
    const select = document.getElementById("pdfSelect");
    if (lastPDF) {{
      select.value = lastPDF;
      document.getElementById("pdfViewer").src = lastPDF;
    }}
  }};
</script>
</head>
<body>

<div class="container">

  <div class="left-pane">
    <header>
      PDF Document
      <select id="pdfSelect" onchange="changePDF(this)">
        {options_html}
      </select>
    </header>
    <iframe id="pdfViewer" class="pdf-viewer" src=""></iframe>
  </div>

  <div class="right-pane">
    <header>Chat with the Document</header>
    <iframe class="chat-iframe" src="http://localhost:{SERVER_PORT}/"></iframe>
  </div>

</div>

</body>
</html>
"""

# Guardar el HTML
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ HTML generado correctamente con selector de PDFs y puerto={SERVER_PORT}")
