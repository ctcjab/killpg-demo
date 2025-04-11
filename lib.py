import datetime, os, sys


wdth_by_col = {"cmd": 22}


def prn(*args, indent="", **kw):
    now = datetime.datetime.now().strftime('%H:%M:%S')
    cmd = repr(" ".join(sys.argv))
    ctx = {"cmd": cmd, "pid": os.getpid(), "pgid": os.getpgrp(), "ppid": os.getppid(), **kw}
    # ctx["sid"] = os.getsid(os.getpid())
    ctxstr = " ".join(f"{k}={str(v).ljust(wdth_by_col.get(k, 7))}" for (k, v) in ctx.items())
    print(f"[{now} {ctxstr}]{indent}", *args)
