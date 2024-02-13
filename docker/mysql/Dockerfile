ARG IMAGE=mysql
ARG TAG=8.2.0

FROM ${IMAGE}:${TAG}

# Only for homogeneity between all 3 services' Dockerfiles and yarn commands. Not used.
ARG VERSION=8.0.31

LABEL org.opencontainers.image.description "MySQL Docker image"

# https://github.com/krallin/tini
ARG TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENTRYPOINT [ "/tini", "--" ]
CMD [ "mysqld" ]