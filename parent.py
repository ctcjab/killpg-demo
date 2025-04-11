#!/usr/bin/env python3

import contextlib, os, signal, subprocess, sys, time
from lib import prn

prn("Running...")

prn("Spawning subprocess in new process group...")
subproc = subprocess.Popen(
    ("./child.py", "--depth=0"),
    # This is what allows us to kill the entire subprocess tree
    # with a single os.killpg() call (see `finally` block below):
    process_group=0,
)
pgid = subproc.pid
assert pgid != os.getpgrp(), "subprocess not spawned into new process group"

prn("Sleeping 5s...")
try:
    time.sleep(5)
    prn("Woke up")
except KeyboardInterrupt:
    print()
    prn("Got SIGINT")
finally:
    for sig in ("SIGTERM", "SIGKILL"):
        try:
            os.killpg(pgid, getattr(signal, sig))
        except ProcessLookupError:
            prn(f"Could not send {sig} to process group {pgid}")
            break
        prn(f"Sent {sig} to process group {pgid}")
        if sig == "SIGTERM":
            prn("Sleeping 3s to give subprocesses a chance to exit gracefully")
            time.sleep(3)
    prn("Goodbye")
