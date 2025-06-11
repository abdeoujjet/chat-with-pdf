FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# install dependencies 
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# create working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./
COPY . .

# Install requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# download HuggingFace  sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

RUN python generate_index_html.py

# Expose Gradio default port (7860)
EXPOSE 7860

CMD ["python", "app.py"]
