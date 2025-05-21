# Use an official Python image as a base
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy all necessary files
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
# ENV OLLAMA_URL=http://localhost:11434
ENV OLLAMA_URL=http://10.0.0.210:11434
# ENV OLLAMA_URL=http://host.docker.internal:11434
ENV OLLAMA_MODEL=qwen2.5-coder:3b


# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
