ARG IMAGE=mysql
ARG TAG=8.0.33

FROM ${IMAGE}:${TAG}

# Only for homogeneity between all 3 services' Dockerfiles and yarn commands. Not used.
ARG VERSION=8.0.31

LABEL org.opencontainers.image.description \
    MySQL Docker image with Doppler env var wrapper

# Install the Doppler CLI via apt for secrets retrieval.
RUN curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh

# Wrap this Docker image in secrets we can pull from doppler.
ENTRYPOINT [ "doppler", "run", "--", "docker-entrypoint.sh" ]
CMD [ "mysqld" ]
