import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from random import shuffle, randint
from time import sleep

import psutil

from blacklist import crash_detection, stalling_detection, update_skiplist, find_pid
from utils import log, read_json, write_json, RPKI_OBJTYPES
from vars import RP_TIMEOUT, RP_POLL_INTERVAL, VALIDATION_INTERVAL, D_SHARE, D_RP_OUT, D_RP_CACHE

F_VRP = D_SHARE / "vrp.json"
TALS = list(Path("/data/in/rpki-tals").glob("*.tal"))

RPKI_CMD = f"rpki-client -v -j -m -s {RP_TIMEOUT} -S {D_SHARE / 'master-skiplist.lst'} -d %s -t %s {D_RP_OUT}"
GRACE = 5


def aggregate_tal_vrps():
    uniq_objs = {objtype: set() for objtype in RPKI_OBJTYPES}
    tal_vrps = list(D_RP_OUT.glob("*.tal.json"))
    for tal_vrp in tal_vrps:
        vrp = read_json(tal_vrp)

        for objtype in RPKI_OBJTYPES:
            for entry in vrp.get(objtype, []):
                del entry["expires"]
                entry_str = json.dumps(entry)
                uniq_objs[objtype].add(entry_str)

    agg_vrp = {"metadata": {"buildtime": datetime.now().isoformat().split("Z")[0]}}
    agg_vrp.update({objtype: [json.loads(entry_str) for entry_str in entries] for objtype, entries in uniq_objs.items()})
    write_json(agg_vrp, "/tmp/tmp-vrp.json")
    os.rename("/tmp/tmp-vrp.json", F_VRP.absolute())
    log(__file__, f"updated {F_VRP} ({sum(len(agg_vrp[objtype]) for objtype in RPKI_OBJTYPES)} unique entries from {len(tal_vrps)} TALs)")


def kill_proc(name: str):
    pids = find_pid(name)
    for i in pids:
        psutil.Process(i).kill()


if __name__ == "__main__":
    start_index = randint(0, len(TALS) - 1)
    TALS = TALS[start_index:] + TALS[:start_index]

    for tal_cache in (D_RP_CACHE / tal.name.rstrip(".tal") for tal in TALS):
        tal_cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(["chown", "_rpki-client:_rpki-client", tal_cache])

    while True:
        for tal in TALS:
            log(__file__, "Starting packet monitor")
            mon_pid = subprocess.Popen(["python3", "conn_tracking.py"]).pid
            sleep(5)  # wait for sniffer to be fully initialized

            log(__file__, f"running RP for {tal.absolute()}")
            rp = subprocess.Popen((RPKI_CMD % (D_RP_CACHE / tal.name.rstrip(".tal"), str(tal.absolute()))).split())

            log(__file__, f"polling RP in {RP_POLL_INTERVAL} sec intervals...")
            while True:
                start_t = datetime.timestamp(datetime.now())
                skiplist = stalling_detection(start_t)
                if skiplist:
                    update_skiplist(skiplist)
                    log(__file__, "Killing stalled RP.")
                    kill_proc("rpki-client")
                    break

                status = rp.poll()
                if status is not None:
                    if status == 0:
                        log(__file__, "RPID is 0. No errors.")
                        (D_RP_OUT / "json").rename(D_RP_OUT / f"{tal.name}.json")
                        log(__file__, f"updated {D_RP_OUT}/{tal.name}.json")
                        break

                    log(__file__, f"RPID is {status}. Crash occurred.")
                    skiplist = crash_detection()
                    update_skiplist(skiplist)
                    break

                sleep(RP_POLL_INTERVAL)

            log(__file__, "Killing monitor")
            kill_proc("conn_tracking.py")

            aggregate_tal_vrps()

        log(__file__, f"Next validation run in {VALIDATION_INTERVAL} seconds")
        sleep(VALIDATION_INTERVAL)
        shuffle(TALS)
