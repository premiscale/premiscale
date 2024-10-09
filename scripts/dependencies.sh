#! /usr/bin/env bash
# Install this repository's depndencies for development.

asdf plugin add nodejs   https://github.com/asdf-vm/asdf-nodejs.git
asdf plugin-add yarn     https://github.com/twuni/asdf-yarn.git
#asdf plugin-add protoc   https://github.com/paxosglobal/asdf-protoc.git
asdf plugin-add devspace https://github.com/virtualstaticvoid/asdf-devspace.git
asdf plugin add https://github.com/comdotlinux/asdf-pre-commit.git

asdf install

if [ "$(conda info --envs --json | jq -r '.envs[]' | awk '/(premiscale)$/')" = "" ]; then
    conda create -y -n premiscale python=3.10
fi

sudo apt install -y bats libvirt-dev

conda activate premiscale
# pip install -r requirements.txt