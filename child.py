#!/usr/bin/env python3

import os, signal, subprocess, sys, time
from lib import prn as prn_

MAXDEPTH = 3
depth = int(next(iter(i.partition("=")[2] for i in reversed(sys.argv) if i.startswith("--depth=")), 0))
assert depth <= MAXDEPTH
# The following allows us to demo that the SIGKILL fallback logic in parent.py works as intended.  # TODO: Get it working for depth > 0.
simulate_hang = depth == 0

def prn(*args):
    prn_("😈" if simulate_hang else "", *args, indent="  " * (depth + 1))

if simulate_hang:
    prn("Running in simulate_hang mode: will ignore SIGTERM")
else:
    prn("Running...")

def sig_handler(signum, frame):
    prn(f"Received {signal.Signals(signum).name} ->", "ignoring!" if simulate_hang else "exiting")
    if not simulate_hang:
        raise SystemExit(-signum)

signal.signal(signal.SIGTERM, sig_handler)

if depth < MAXDEPTH:
    cmd = f"./child.py --depth={depth + 1}"
    prn(f"Spawning {cmd!r}")
    subprocess.Popen(cmd.split())

if depth == 1:
    prn("Exiting now -> my descendants will outlive me")
    raise SystemExit

while True:
    prn("Sleeping for 3s...")
    time.sleep(3)
