FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="fileOrganizer"
LABEL description="Smart File Organizer — sort, deduplicate, and schedule your files."

WORKDIR /app

# Copy installed deps from builder
COPY --from=builder /install /usr/local

# Copy the package source
COPY . .

# Mount point for the host directory to organise
VOLUME ["/data"]

ENTRYPOINT ["python", "-m", "fileOrganizer", "/data"]
