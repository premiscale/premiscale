ARG IMAGE=influxdb
ARG TAG=2.7.0

FROM ${IMAGE}:${TAG}

# Only for homogeneity between all 3 services' Dockerfiles and yarn commands. Not used.
ARG VERSION=2.6.1

LABEL org.opencontainers.image.description \
    InfluxDB Docker image with Doppler env var wrapper

# Install the Doppler CLI via apt for secrets retrieval.
RUN curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh

ENTRYPOINT [ "doppler", "run", "--", "/entrypoint.sh" ]
CMD [ "influxd" ]
