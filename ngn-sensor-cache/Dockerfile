ARG PYTHON_VERSION=3.10

# Builder Stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS builder

WORKDIR /app
COPY ngn-sensor-cache /app/ngn-sensor-cache
COPY ngn-sensor-common /app/ngn-sensor-common

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
RUN pip install build~=0.9.0 && \
    python3 -m build --wheel --outdir /app/dist/ ngn-sensor-cache && \
    python3 -m build --wheel --outdir /app/dist/ ngn-sensor-common

# Runtime Stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS runtime

# Create a non-root user
RUN useradd ngn \
    && mkdir -p /home/ngn \
    && chown -R ngn:ngn /home/ngn

WORKDIR /home/ngn

ENV PATH=${PATH}:/home/ngn/.local/bin

# Copy from the builder stage
COPY --from=builder /app/dist/ngn_sensor*.whl \
    /app/ngn-sensor-cache/src/ngn/sensor/cache/* \
    /app/ngn-sensor-common/src/ngn/sensor/common/* \
    /home/ngn/

# Change ownership
RUN chown -R ngn:ngn /home/ngn
USER ngn:ngn

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
# Install application dependencies
RUN pip install build~=0.9.0 \
    && pip install --user --no-warn-script-location /home/ngn/ngn_sensor*.whl \
    && rm /home/ngn/*.whl
