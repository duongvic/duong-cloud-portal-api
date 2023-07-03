# How to deploy CAS Portal
---
## Step 1 Prepare ENV
```sh
sudo su 
ROOT_DIR = `pwd`
./01-init-host.sh
./02-prepare-env.sh
```
## Step 2: Setup Postgres DB
Please refer [Manual Guide](./DEPLOY_PG_DB.md)

## Step 3 Build Cas Portal Image
```sh
cd ${ROOT_DIR}/deployment/dashboard
./build.sh

## Step 3 Buil Cas Webssh Image
cd ${ROOT_DIR}/deployment/webssh
./build.sh
```
## Step 4 Deploy system
```sh
./03-deploy-cas.sh
```
---
## How to setup private Docker registry 
```shell script
docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

Or with Cert
```shell script
docker run -d \
  --restart=always \
  --name registry \
  -v "$(pwd)"/certs:/certs \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  -p 443:443 \
  registry:2
```

Test Local Registry 
```shell script
docker pull ubuntu:16.04
docker images tag ubuntu:16.04 localhost:5000/my-ubuntu
docker push localhost:5000/my-ubuntu
docker pull localhost:5000/my-ubuntu
```

## Login public (Dockerhub)[https://hub.docker.com]
```shell script
cat passord.txt | docker login --username ${DOCKER_USERNAME} --password-stdin
```

## Build Docker images
```shell script
cp -R ../../application ./dashboard
cp -R ../ngix/ssl ./dashboard
#source ./common.env
docker build --no-cache -t ${CAS_PORTAL_IMAGE} -f {DOCKERFILE}
docker images tag ${CAS_PORTAL_IMAGE} ${DOCKER_USERNAME}/${CAS_PORTAL_IMAGE}:${CAS_PORTAL_VERSION} 
docker push ${DOCKER_USERNAME}/${CAS_PORTAL_IMAGE}:${CAS_PORTAL_VERSION} 
rm -rf ../../../application
```

# Gen certificate for Ngin
```shell script
# password import .pfx: Compute@data
# password pem key: Cas@2020
openssl pkcs12 -in cas.pfx -nocerts -out cas.key
openssl pkcs12 -in cas.pfx -clcerts -nokeys -out cas.crt

```
