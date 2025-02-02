FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /chatbot-server

# Install Rust and Cargo
RUN apt-get update && apt-get install -y curl && curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    /bin/bash -c "source $HOME/.cargo/env" && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# Copy requirements.txt and install dependencies
COPY requirements.txt /chatbot-server
RUN /bin/bash -c "source $HOME/.cargo/env && pip install --no-cache-dir --timeout=120 -r requirements.txt --index-url https://pypi.org/simple"

# Copy the entire project (including model.yaml)
COPY . /chatbot-server

# Set the working directory to /chatbot-server/src
WORKDIR /chatbot-server/src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]