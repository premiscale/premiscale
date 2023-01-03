ARG IMAGE=python
ARG TAG=3.11.1

FROM ${IMAGE}:${TAG}

ARG AUTOSCALE_VERSION=0.1.0

# ENV DOPPLER_TOKEN=...

USER root

LABEL org.opencontainers.image.description \
    Libvirt autoscaler Docker image

# Install dependencies.
RUN mkdir -p /etc/autoscaler && \
    useradd -rm -d /autoscaler -s /bin/bash -g root -G sudo -u 1001 autoscaler

# Copy in autoscaler.
WORKDIR /autoscaler
COPY scripts/run.sh .
RUN chmod +x run.sh && chown -R autoscaler:root /autoscaler

# https://github.com/krallin/tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# Install the Doppler CLI via apt for secrets retrieval.
RUN curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh

USER autoscaler

ENTRYPOINT [ "/tini", "--", "doppler", "run", "--" ]
CMD [ "./run.sh" ]
