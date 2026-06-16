import re
from time import sleep

from vars import F_PEER_CANDIDATES, PEER_POLL_INTERVAL, F_PEER_IP_LOG

WAIT = PEER_POLL_INTERVAL / 4
seen = set()

while True:
    with open(F_PEER_IP_LOG) as f_in:
        for line in f_in:
            name = line.strip()

            if re.match(r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", name):
                if not F_PEER_CANDIDATES.exists():
                    seen = set()

                if name not in seen:
                    with open(F_PEER_CANDIDATES, "a") as f_out:
                        f_out.write(name + "\n")
                    seen.add(name)
    sleep(WAIT)
