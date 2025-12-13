FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- System deps for pyodbc (and build tools if wheels are missing on 3.13) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl gnupg ca-certificates \
      unixodbc unixodbc-dev libgssapi-krb5-2 \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- Microsoft ODBC Driver 18 (Debian 12/bookworm) ---
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
      | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
 && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
      > /etc/apt/sources.list.d/microsoft-prod.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
 && rm -rf /var/lib/apt/lists/*

# --- Python deps ---
COPY requirements.txt .
RUN python --version \
 && pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# --- App code ---
COPY app ./app
COPY ui ./ui

ENV PYTHONPATH=/app:${PYTHONPATH}
EXPOSE 8080

CMD ["python", "-m", "streamlit", "run", "ui/dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
