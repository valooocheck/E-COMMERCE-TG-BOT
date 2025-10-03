FROM python:3.12.11-slim AS base

ARG PROJECT_DIR=/opt/app
ARG PYTHON_VENV=/opt/.venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_DIR=${PROJECT_DIR} \
    DEBIAN_FRONTEND=noninteractive

FROM base AS builder

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*


FROM builder AS python-env
ARG REQUIREMENTS_FILE=requirements.txt

COPY src/requirements.txt /

RUN python -m venv "${PYTHON_VENV}" \
    && "${PYTHON_VENV}/bin/python" -m pip install --no-cache-dir --upgrade pip \
    && "${PYTHON_VENV}/bin/pip" install --no-cache-dir -r /$(basename ${REQUIREMENTS_FILE}) \
    && rm -rf /$(basename ${REQUIREMENTS_FILE})


FROM builder AS application

COPY --from=python-env ${PYTHON_VENV} ${PYTHON_VENV}
ENV PATH="${PYTHON_VENV}/bin:${PATH}"

COPY src/entrypoint.sh /
RUN chmod +x /entrypoint.sh

FROM application AS server

WORKDIR ${PROJECT_DIR}
COPY ./src ${PROJECT_DIR}

ENTRYPOINT ["/entrypoint.sh"]

# Required for docker compose interpreter for example in pycharm
FROM application AS local


