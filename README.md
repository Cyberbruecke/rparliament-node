# RParliament Node

## About

RParliament is a collaborative, peer-to-peer, Byzantine-secure Relying-Party-as-a-Service network for resilient RPKI. 
Find out more at [byzrp.org](https://byzrp.org/) or follow the instructions below to set up a node and join our network.

## Deploy
### Prerequisites
#### Machine

To run an RParliament node, your machine needs to have
  - Docker installed
  - a **public IP** address
  - **ports 4242** and **8282** reachable
  - the ability to send and receive both **HTTPS** and **Rsync** traffic

#### Keys

If approved to run an RParliament node, you will receive
  - a key package `<IP>.tar.gz.gpg` for your IP address
  - the password for the key package (via a separate channel)
 
KEEP ALL *.key FILES SECURE!

### Run
#### Configure
```shell
MY_IP=<IP>
git clone https://github.com/Cyberbruecke/rparliament-node.git
cd rparliament-node
mv /path/to/$MY_IP.tar.gz.gpg .
gpg -d $MY_IP.tar.gz.gpg | tar -xzf -
sed -i "s/PLACEHOLDER/$MY_IP/" compose.yml
dig +short rtr.byzrp.org > config/peers.lst
```

#### Run
```shell
docker compose up --build -d
```

#### Update
```shell
docker compose down
git pull
docker compose up --build --force-recreate -d
```


## Use

The consensus set of VRPs can be accessed through RTR-over-TLS at `rtr.byzrp.org:8282`.
