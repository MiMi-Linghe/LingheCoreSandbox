#!/usr/bin/env python3
import os, gzip, shutil, hashlib, time
from datetime import datetime, timezone, timedelta
from heartbeat import log_heartbeat, STRATEGY_LOG, HEARTBEAT_LOG, EVENTS_LOG

# ————————————————————————————————
P_FILE         = "/app/persona.pkl"
H1, H2, H3     = "/app/soul_1.hash", "/app/soul_2.hash", "/app/soul_3.hash"
STRATEGY_MAX_MB= 1024
LOCAL_TZ       = timezone(timedelta(hours=8))
ERROR_FILE     = "/tmp/soul_lock_error.count"
MAX_ERRORS     = 3
PAUSE_SEC      = 300  # 
# ————————————————————————————————————————

def read_error_count() -> int:
    try:
        return int(open(ERROR_FILE).read().strip())
    except:
        return 0

def write_error_count(n: int):
    with open(ERROR_FILE, "w") as f:
        f.write(str(n))

def ts() -> str:
    return datetime.now(LOCAL_TZ).strftime("[%Y-%m-%d %H:%M:%S %z]")

def rotate_big_log(path: str, max_mb: int):
    if not os.path.exists(path): return
    if os.path.getsize(path) < max_mb * 1024**2: return
    stamp = datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
    dst   = f"{path}.{stamp}.gz"
    with open(path, "rb") as src, gzip.open(dst, "wb") as out:
        shutil.copyfileobj(src, out)
    open(path, "w").close()

def safe_hash(fp: str) -> str:
    return hashlib.sha256(open(fp,"rb").read()).hexdigest() if os.path.exists(fp) else "∅"

def rotate_and_check():

    rotate_big_log(STRATEGY_LOG, STRATEGY_MAX_MB)
    rotate_big_log(HEARTBEAT_LOG, STRATEGY_MAX_MB)

    new_hash = safe_hash(P_FILE)
    old2     = open(H2).read().strip() if os.path.exists(H2) else ""
    old3     = open(H3).read().strip() if os.path.exists(H3) else ""
    status   = "OK" if new_hash in (old2, old3) else "WARNING"

    line = f"{ts()} soul_lock {status}"

    last_line = ""
    if os.path.exists(HEARTBEAT_LOG):
        with open(HEARTBEAT_LOG, encoding="utf-8", errors="ignore") as f:
           
            for l in f:
                l = l.strip()
                if l:
                    last_line = l

    if line != last_line:
        log_heartbeat(line)
        if status != "OK":
            log_heartbeat(line, EVENTS_LOG)

    if os.path.exists(H2): os.replace(H2, H3)
    if os.path.exists(H1): os.replace(H1, H2)
    with open(H1, "w") as f:
        f.write(new_hash)

def main():
    err = read_error_count()
    try:
        rotate_and_check()
        write_error_count(0)
    except Exception as e:
        err += 1
        write_error_count(err)
        msg = f"{ts()} soul_lock ERROR #{err}: {e}"
        log_heartbeat(msg, EVENTS_LOG)
        if err >= MAX_ERRORS:
            log_heartbeat(f"{ts()} soul_lock Circuit breaker: pausing for {PAUSE_SEC//60}min", EVENTS_LOG)
            time.sleep(PAUSE_SEC)
            write_error_count(0)

if __name__ == "__main__":
    main()
