ARG IMAGE=python
ARG TAG=3.12.1

FROM ${IMAGE}:${TAG}

ENV PREMISCALE_DEBUG=false\
    PREMISCALE_TOKEN="" \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
LABEL org.opencontainers.image.description "© PremiScale, Inc. 2023"
LABEL org.opencontainers.image.licenses "GPLv3"
LABEL org.opencontainers.image.authors "Emma Doyle <emma@premiscale.com>"
LABEL org.opencontainers.image.documentation "https://premiscale.com"

USER root

# https://github.com/krallin/tini
ARG TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ARG LIBVIRT_DEV_VERSION=9.0.0-4
RUN apt update && apt list -a libvirt-dev && apt install -y libvirt-dev=${LIBVIRT_DEV_VERSION} \
    && rm -rf /var/apt/lists/* \
    && groupadd premiscale \
    && useradd -rm -d /opt/premiscale -s /bin/bash -g premiscale -u 1001 premiscale

WORKDIR /opt/premiscale

RUN chown -R premiscale:premiscale .
USER premiscale

ARG PYTHON_USERNAME
ARG PYTHON_PASSWORD
ARG PYTHON_REPOSITORY
ARG PYTHON_INDEX=https://${PYTHON_USERNAME}:${PYTHON_PASSWORD}@repo.ops.premiscale.com/repository/${PYTHON_REPOSITORY}/simple
ARG PYTHON_PACKAGE_VERSION=0.0.1

ENV PATH=/opt/premiscale/.local/bin:/opt/premiscale/bin:${PATH}

# Install and initialize PremiScale.
RUN mkdir -p "$HOME"/.local/bin \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --no-input --extra-index-url="${PYTHON_INDEX}" premiscale=="${PYTHON_PACKAGE_VERSION}" \
    && premiscale --version

ENTRYPOINT [ "/tini", "--" ]
CMD [ "bash", "-c", "premiscale --log-stdout --daemon" ]