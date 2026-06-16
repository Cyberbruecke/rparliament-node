# RParliament Node

## About

RParliament is a collaborative, peer-to-peer, Byzantine-secure Relying-Party-as-a-Service network for resilient RPKI.
Find out more at [rparliament.org](https://rparliament.org/) or follow the instructions below to set up a node and join our network.

## Deploy
### Prerequisites
#### Machine

To run an RParliament node, your machine needs to have
  - Docker installed
  - **ports 4141** and **8282** reachable
  - the ability to send and receive both **HTTPS** and **Rsync** traffic

#### Keys

If approved to run an RParliament node, you will receive
  - a key package `node.rparliament.org.tar.gz.gpg` for your node
  - the password for the key package (via a separate channel)

KEEP ALL *.key FILES SECURE!

### Run
#### Configure
```shell
git clone https://github.com/Cyberbruecke/rparliament-node.git
cd rparliament-node
mv /path/to/node.rparliament.org.tar.gz.gpg .
gpg -d node.rparliament.org.tar.gz.gpg | tar -xzf -
dig +short PTR node.rparliament.org > config/peers.lst
echo "NODENAME=$(openssl x509 -noout -subject -in keys/node.crt | sed 's/.*CN *= *//')" > .env
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

The consensus set of VRPs can be accessed at each individual node through RTR-over-TLS via `*.node.rparliament.org:8282` (or in round-robin at `node.rparliament.org:8282`) using the RParliament root cert.
Run [`rparliament-client`](https://github.com/Cyberbruecke/rparliament-client) locally to automatically aggregate node output, or use the RTR-over-TLS endpoint `rtr.rparliament.org:8282`, which deploys the client as a service.
