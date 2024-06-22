FROM python:3-alpine
ARG POETRY_DYNAMIC_VERSIONING_BYPASS="0.0.0"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache tini

COPY . /python-build
RUN python3 -m pip install /python-build && rm -rf /python-build

COPY docker/entrypoint /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/entrypoint"]
