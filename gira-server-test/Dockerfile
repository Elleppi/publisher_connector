ARG PYTHON_VERSION=3.10

# Builder Stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS builder

WORKDIR /app
COPY gira-server-test /app/gira-server-test

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
RUN pip install build~=0.9.0 && \
    python3 -m build --wheel --outdir /app/dist/ gira-server-test

# Runtime Stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS runtime

# Create a non-root user
RUN useradd ngn \
    && mkdir -p /home/ngn \
    && chown -R ngn:ngn /home/ngn

WORKDIR /home/ngn

ENV PATH=${PATH}:/home/ngn/.local/bin

# Copy from the builder stage
COPY --from=builder /app/dist/gira_server*.whl \
    /app/gira-server-test/src/gira/server/test/* \
    /home/ngn/

# Change ownership
RUN chown -R ngn:ngn /home/ngn
USER ngn:ngn

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"

# Install application dependencies
RUN pip install build~=0.9.0 \
    && pip install --user --no-warn-script-location /home/ngn/gira_server*.whl \
    && rm /home/ngn/*.whl
