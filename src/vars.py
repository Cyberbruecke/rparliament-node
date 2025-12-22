import os
from pathlib import Path

try:
    # setup
    D_RP_CACHE=Path(os.environ["D_RP_CACHE"])
    D_RP_OUT=Path(os.environ["D_RP_OUT"])
    D_SHARE=Path(os.environ["D_SHARE"])
    D_METRICS=Path(os.environ["D_METRICS"])
    D_RP_TALS=Path(os.environ["D_RP_TALS"])
    F_PEER_IP_LOG=Path(os.environ["F_PEER_IP_LOG"])

    # const
    F_PEER_CANDIDATES = Path("/tmp/peer_candidates")
    F_BL_DNSBOOK = Path("/tmp/dnsbook.json")
    F_BL_CONN_STATE = Path("/tmp/conn_state.json")
    F_SERVER_CRT = Path("/etc/ssl/certs/peering.crt")
    F_SERVER_KEY = Path("/etc/ssl/private/peering.key")
    F_ROOT_CRT = Path("/etc/ssl/certs/root.crt")

    # config
    CONSENSUS = float(os.environ.get("CONSENSUS", 0.5))
    PEER_DISCOVERY = bool(int(os.environ.get("PEER_DISCOVERY", 1)))
    VALIDATION_INTERVAL = int(os.environ.get("VALIDATION_INTERVAL", 120))
    RP_POLL_INTERVAL = int(os.environ.get("RP_POLL_INTERVAL", 10))
    RP_TIMEOUT = int(os.environ.get("RP_TIMEOUT", 600))
    BLACKLIST_EXPIRY = int(os.environ.get("BLACKLIST_EXPIRY", 7200))
    GLOBAL_TIMEOUT = int(os.environ.get("GLOBAL_TIMEOUT", 3600))
    PEER_TIMEOUT = int(os.environ.get("PEER_TIMEOUT", 10))
    PEER_TIMEOUT = None if PEER_TIMEOUT < 0 else PEER_TIMEOUT
    PEER_POLL_INTERVAL = int(os.environ.get("PEER_POLL_INTERVAL", 30))
    INIT_PEERING_DELAY = int(os.environ.get("INIT_PEERING_DELAY", 0))
    SNIFF_IFACE = os.environ.get("SNIFF_IFACE", "eth0")
    PEER_RETRIES = int(os.environ.get("PEER_RETRIES", 3))
    STALLING_THRESHOLD = float(os.environ.get("STALLING_THRESHOLD", 0.9))
    SELF_IP = os.environ["SELF_IP"]

except KeyError as e:
    print(f"missing environment variable: {e.args[0]}")
    exit(1)

except ValueError as e:
    print(f"invalid value for environment variable: {e.args[0]}")
    exit(1)


if __name__ == '__main__':
    for file in (F_ROOT_CRT, F_SERVER_CRT, F_SERVER_KEY):
        if not os.path.exists(file):
            print(f"missing required file: {file}")
            exit(1)
