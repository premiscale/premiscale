#! /usr/bin/env bash
# Add a Helm repository.

REPOSITORY="${1:-helm}"
LOCAL_REFERENCE="${2:-premiscale}"

if grep -ioq "${LOCAL_REFERENCE}" <(helm repo list | tail -n +2 | awk '{ print $1 }'); then
    helm repo remove "$LOCAL_REFERENCE"
fi

pass show premiscale/nexus/password | awk NF | helm repo add "$LOCAL_REFERENCE" https://repo.ops.premiscale.com/repository/"$REPOSITORY"/ --username "$(pass show premiscale/nexus/username)" --password-stdin