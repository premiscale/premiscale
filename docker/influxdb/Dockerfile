ARG IMAGE=influxdb
ARG TAG=2.5.1

# ENV DOPPLER_TOKEN=...

FROM ${IMAGE}:${TAG}

LABEL org.opencontainers.image.description \
    InfluxDB Docker image with Doppler env var wrapper

# Install the Doppler CLI via apt for secrets retrieval.
RUN curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh

ENTRYPOINT [ "doppler", "run", "--", "/entrypoint.sh" ]
CMD [ "influxd" ]
