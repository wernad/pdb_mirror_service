FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

ARG APP_NAME=pdb_mirror

# Update and add basic packages
RUN apt-get update && apt-get install -y --no-install-recommends  build-essential \
curl \
cmake \
git \
wget \
unzip \
libboost-all-dev \
&& rm -rf /var/lib/apt/lists/*

# ENV TZ=Europe/Prague

# Working directory
RUN mkdir -p /opt/${APP_NAME}
WORKDIR /opt/${APP_NAME}

# Dependencies
COPY ["requirements.txt", "/opt/${APP_NAME}"]
RUN --mount=type=bind,source=requirements.txt,target=/${APP_NAME}/requirements.txt,readonly \
    pip install --no-cache-dir --upgrade --root-user-action=ignore -r requirements.txt

# Copy source files.
COPY [".", "/opt/${APP_NAME}"]

# Create user
# RUN adduser -D ${APP_NAME} && chown -R ${APP_NAME} /opt/${APP_NAME}
RUN useradd --system --no-create-home --shell /usr/sbin/nologin pdb_mirror
RUN chown -R pdb_mirror:pdb_mirror /opt/pdb_mirror
USER ${APP_NAME}

# Expose port for FastAPI
EXPOSE 8000

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
