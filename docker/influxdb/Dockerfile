ARG IMAGE=influxdb
ARG TAG=2.7.6

FROM ${IMAGE}:${TAG}

# Only for homogeneity between all 3 services' Dockerfiles and yarn commands. Not used.
ARG VERSION=2.6.1

LABEL org.opencontainers.image.description "InfluxDB Docker image"

# https://github.com/krallin/tini
ARG TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENTRYPOINT [ "/tini", "--" ]
CMD [ "influxd" ]