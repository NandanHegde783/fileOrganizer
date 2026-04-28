FROM python:3.12-slim

LABEL maintainer="fileOrganizer"
LABEL description="Smart File Organizer — sort, deduplicate, and schedule your files."

WORKDIR /app

# Copy the package into a subdirectory so `python -m fileOrganizer` resolves correctly.
# The build context is the fileOrganizer/ folder, so we copy its contents
# into /app/fileOrganizer/ inside the image.
COPY . ./fileOrganizer/

# Mount point for the host directory to organise
VOLUME ["/data"]

ENTRYPOINT ["python", "-m", "fileOrganizer", "/data"]
