# CAS Cloud Backend

# Install Docker 
```sh 
# Docker 
sudo apt update -y 
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y 
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update -y 
sudo apt install docker-ce -y 
sudo systemctl status docker 
sudo systemctl enable docker
sudo usermod -aG docker ${USER}
# Docker Compose
sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

# Install Ubuntu18
```sh 
apt-get install git -y 
git clone https://git.fmeet.vn/khanhct/cloud-portal-api
cd cloud-portal-api
apt-get install python3-pip virtualenv python3-dev libmysqlclient-dev gcc libssl-dev vim wget telnet chrony -y 
pip3 install -r requirement.txt
# Privated lib
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev -y
sudo pip3 install git+https://git.fmeet.vn/khanhct/foxcloud.git@ussuri#egg=foxcloud
```

# Running 
```sh 
cd extra/setup
docker-compose up -d 
cd ../..
python3 index.py
```