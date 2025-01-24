FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

# Install Rust and Cargo
RUN apt-get update && apt-get install -y curl && curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    /bin/bash -c "source $HOME/.cargo/env" && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

COPY src/requirements.txt /app

# Increase timeout and use a faster mirror
RUN /bin/bash -c "source $HOME/.cargo/env && pip install --no-cache-dir --timeout=120 -r requirements.txt --index-url https://pypi.org/simple"

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]