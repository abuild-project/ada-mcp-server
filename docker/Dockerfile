# syntax=docker/dockerfile:1
# SPDX-License-Identifier: MIT
FROM debian:trixie-slim@sha256:7378260c0a098d27ac206225db5e7d92b8c7c84ea7afccc86eeb513756bbd392

ARG SOURCE_SHA
ARG PROJECT_VERSION
ARG ALS_VERSION=2026.3.202607051
ARG ALS_SHA256=9dfa29af05418913ff445be0c6875f7a51ebad5fc781f3446d3e2c3903d09787
ARG ALS_LICENSE_SHA256=589ed823e9a84c56feb95ac58e7cf384626b9cbf4fda2a907bc36e103de1bad2

LABEL org.opencontainers.image.title="abuild-project Ada MCP Server"
LABEL org.opencontainers.image.source="https://github.com/abuild-project/ada-mcp-server"
LABEL org.opencontainers.image.revision="${SOURCE_SHA}"
LABEL org.opencontainers.image.version="${PROJECT_VERSION}"
LABEL io.abuild-project.license-scope="Own source MIT; dependencies retain individual licenses"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl git gcc gnat gnat-14=14.2.0-19 gprbuild=2025.0.0-4 \
       make python3 python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /usr/sbin/nologin ada-mcp

# docker/build supplies only the immutable committed Git archive as context.
# Its bind mount avoids repeated COPY layers with Docker VFS.
# proxy_ca is optional on ordinary hosts and transient in managed Cloud builds.
RUN --mount=type=bind,source=.,target=/context,readonly \
    --mount=type=secret,id=proxy_ca \
    set -eu; \
    mkdir -p /opt/ada-mcp/project /opt/ada-mcp/bin \
      /usr/share/licenses/ada-language-server /usr/share/licenses/ada-mcp-server; \
    cp -a /context/. /opt/ada-mcp/project/; \
    if [ -f /run/secrets/proxy_ca ]; then \
      export CURL_CA_BUNDLE=/run/secrets/proxy_ca PIP_CERT=/run/secrets/proxy_ca; \
    fi; \
    python3 -m venv /opt/ada-mcp/venv; \
    /opt/ada-mcp/venv/bin/pip install --no-cache-dir --only-binary=:all: \
      --require-hashes -r /opt/ada-mcp/project/requirements/development.lock; \
    /opt/ada-mcp/venv/bin/pip install --no-deps --no-build-isolation /opt/ada-mcp/project; \
    curl --fail --location --silent --show-error \
      "https://github.com/AdaCore/ada_language_server/releases/download/${ALS_VERSION}/als-${ALS_VERSION}-linux-x64.tar.gz" \
      --output /tmp/als.tar.gz; \
    printf '%s  /tmp/als.tar.gz\n' "$ALS_SHA256" | sha256sum --check -; \
    tar -xzf /tmp/als.tar.gz -C /opt/ada-mcp/bin --strip-components=5 \
      integration/vscode/ada/x64/linux/ada_language_server; \
    curl --fail --location --silent --show-error \
      "https://raw.githubusercontent.com/AdaCore/ada_language_server/${ALS_VERSION}/LICENSE" \
      --output /usr/share/licenses/ada-language-server/LICENSE; \
    printf '%s  /usr/share/licenses/ada-language-server/LICENSE\n' "$ALS_LICENSE_SHA256" \
      | sha256sum --check -; \
    cp /opt/ada-mcp/project/LICENSE /usr/share/licenses/ada-mcp-server/LICENSE; \
    chmod 0755 /opt/ada-mcp/bin/ada_language_server; \
    dpkg-query -W -f='${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\n' \
      > /usr/share/licenses/ada-mcp-server/debian-packages.tsv; \
    /opt/ada-mcp/venv/bin/python /opt/ada-mcp/project/scripts/license_index.py \
      --output /usr/share/licenses/ada-mcp-server/components.json; \
    find /opt/ada-mcp/project -type d -exec chmod a+rx {} +; \
    find /opt/ada-mcp/project -type f -exec chmod a+r {} +; \
    rm -f /tmp/als.tar.gz

ENV ALS_PATH=/opt/ada-mcp/bin/ada_language_server
ENV HOME=/home/ada-mcp
ENV PATH=/opt/ada-mcp/venv/bin:/opt/ada-mcp/bin:${PATH}
ENV PYTHONDONTWRITEBYTECODE=1
USER 1000:1000
WORKDIR /workspace
ENTRYPOINT ["/opt/ada-mcp/venv/bin/python", "-I", "-B", "-m", "ada_mcp"]
