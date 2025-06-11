FROM python:3.10-slim

# Evitar prompts de Debian
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio del app
WORKDIR /app

# Copiar requirements y archivos
COPY requirements.txt ./
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Descargar modelo HuggingFace para sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Puerto por defecto de Gradio
EXPOSE 7860

CMD ["python", "app.py"]
