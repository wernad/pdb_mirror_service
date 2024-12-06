FROM python:3.11-alpine

ARG APP_NAME=pdb_mirror

# Update and add basic packages
RUN apk update && apk add --no-cache build-base libpq-dev gcc musl-dev 
 
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
RUN adduser -D ${APP_NAME} && chown -R ${APP_NAME} /opt/${APP_NAME}
USER ${APP_NAME}

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
