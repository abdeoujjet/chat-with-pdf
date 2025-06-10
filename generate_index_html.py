import os
from config import PDF_FOLDER, SERVER_PORT

# Obtener todos los archivos PDF disponibles
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

# HTML content
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
    }}
    .selector {{
      margin: 10px;
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
    // Obtener parámetros de la URL
    function getQueryParam(name) {{
      const urlParams = new URLSearchParams(window.location.search);
      return urlParams.get(name);
    }}

    function updatePDF() {{
      const pdf = document.getElementById("pdf-select").value;
      window.location.href = "?pdf=" + encodeURIComponent(pdf);
    }}

    window.onload = function () {{
      const pdfParam = getQueryParam("pdf");
      const pdfSelect = document.getElementById("pdf-select");

      // Seleccionar el PDF actual en el dropdown
      if (pdfParam) {{
        pdfSelect.value = pdfParam;
      }}

      document.getElementById("pdf-frame").src = "{PDF_FOLDER}/" + (pdfParam || pdfSelect.value);
      document.getElementById("chat-frame").src = "http://localhost:{SERVER_PORT}/?pdf=" + encodeURIComponent(pdfParam || pdfSelect.value);
    }}
  </script>
</head>
<body>

<div class="container">

  <div class="left-pane">
    <header>PDF Document</header>
    <div class="selector">
      <label for="pdf-select">Choose a PDF:</label>
      <select id="pdf-select" onchange="updatePDF()">
        {"".join([f'<option value="{pdf}">{pdf}</option>' for pdf in pdf_files])}
      </select>
    </div>
    <iframe class="pdf-viewer" id="pdf-frame" src=""></iframe>
  </div>

  <div class="right-pane">
    <header>Chat with the Document</header>
    <iframe class="chat-iframe" id="chat-frame" src=""></iframe>
  </div>

</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ index.html generado con {len(pdf_files)} PDFs y puerto {SERVER_PORT}")
