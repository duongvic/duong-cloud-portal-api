#!/bin/bash

if sudo grep -q "${USER}" /etc/sudoers; then
    echo ""
else
   echo "$USER ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee --append /etc/sudoers > /dev/null
fi

#####################################################################################
sudo apt update 

# Install basic packages
sudo apt-get install curl git redis-tools -y

#===============================================================================
#                   Install docker
#===============================================================================
e_header "Install docker"

if [ -x "$(command -v docker)" ]; then
    e_note  "Docker has been installed. Skip"
else
    # Docker
     sudo apt remove --yes docker docker-engine docker.io \
        && sudo apt update \
        && sudo apt --yes --no-install-recommends install \
            apt-transport-https \
            ca-certificates \
        && wget --quiet --output-document=- https://download.docker.com/linux/ubuntu/gpg \
            | sudo apt-key add - \
        && sudo add-apt-repository \
            "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu \
            $(lsb_release --codename --short) \
            stable" \
        && sudo apt update \
        && sudo apt --yes --no-install-recommends install docker-ce \
        && sudo usermod --append --groups docker "$USER" \
        && sudo systemctl enable docker \
        && e_success 'Docker has been installed  successfully'
        group=docker
        if [ $(id -gn) != $group ]; then
          exec sg $group "$0 $*"
        fi
    e_note 'Waiting for Docker to start...'

sleep 3
fi

#===============================================================================
#                   Install compose
#===============================================================================
e_header "Install docker compose"
if [ -x "$(command -v docker-compose)" ]; then
    e_note  "Docker compose has been installed. Skip"
else
    COMPOSE_VERSION=`git ls-remote https://github.com/docker/compose | grep refs/tags | grep -oP "[0-9]+\.[0-9][0-9]+\.[0-9]+$" | tail -n 1`
    sudo sh -c "curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"
    sudo chmod +x /usr/local/bin/docker-compose
    sudo sh -c "curl -L https://raw.githubusercontent.com/docker/compose/${COMPOSE_VERSION}/contrib/completion/bash/docker-compose > /etc/bash_completion.d/docker-compose"
    e_success 'Docker Compose has been installed successfully'
fi

