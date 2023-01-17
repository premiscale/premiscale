ARG IMAGE=python
ARG TAG=3.10.8

FROM ${IMAGE}:${TAG}

LABEL org.opencontainers.image.description \
    Libvirt autoscaler Docker image

USER root

# https://github.com/krallin/tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# Install the Doppler CLI via apt for secrets retrieval.
RUN curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh

RUN apt update && apt install -y libvirt-dev && \
    rm -rf /var/apt/lists/*

RUN mkdir -p /etc/autoscaler && \
    useradd -rm -d /autoscaler -s /bin/bash -g root -G sudo -u 1001 autoscaler

WORKDIR /autoscaler

# Copy autoscaler into container.
COPY ./docker/autoscaler/scripts/run.sh /autoscaler

RUN chmod +x run.sh && chown -R autoscaler:root .
USER autoscaler

# Install premiscale autoscaler.
ARG PYTHON_USERNAME=admin
ARG PYTHON_PASSWORD=1234
ARG PYTHON_REPOSITORY=pypi
ARG PYTHON_INDEX=https://${PYTHON_USERNAME}:${PYTHON_PASSWORD}@repo.ops.premiscale.com/repository/${PYTHON_REPOSITORY}/simple
ARG PYTHON_PACKAGE_VERSION=0.0.1
RUN pip install --no-cache-dir --no-input --index-url=${PYTHON_INDEX} premiscale==${PYTHON_PACKAGE_VERSION}

ENTRYPOINT [ "/tini", "--", "doppler", "run", "--" ]
CMD [ "./run.sh" ]
