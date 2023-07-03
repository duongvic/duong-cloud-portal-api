# How to setup DockerSwarm
## Prerequisite
- Ubuntu 16.04

## Worker node
```shell script
DOCKER_MANAGER=192.168.0.2
DOCKER_WOKER1=192.168.0.3
DOCKER_WOKER2=192.168.0.4

echo "$DOCKER_MANAGER dockermanager" >> /etc/hosts
echo "$DOCKER_WOKER1 dockerworker1" >> /etc/hosts
echo "$DOCKER_WOKER2 dockerworker2" >> /etc/hosts

sudo ./00-init-host.sh

ping -c 3 $DOCKER_MANAGER
ping -c 3 $DOCKER_WOKER1
ping -c 3 $DOCKER_WOKER2

```

## Master node
```shell script
DOCKER_MANAGER=192.168.0.2
DOCKER_WOKER1=192.168.0.3
DOCKER_WOKER2=192.168.0.4

sudo ./00-init-host.sh
echo "$DOCKER_MANAGER dockermanager" >> /etc/hosts
echo "$DOCKER_WOKER1 dockerworker1" >> /etc/hosts
echo "$DOCKER_WOKER2 dockerworker2" >> /etc/hosts

## Test 
ping -c 3 $DOCKER_MANAGER
ping -c 3 $DOCKER_WOKER1
ping -c 3 $DOCKER_WOKER2

docker swarm init --advertise-addr $DOCKER_MANAGER
```

## Worker node
```shell script
sudo ./00-init-host.sh

```