
import os
import psutil, time, csv
from datetime import datetime

CSV_PATH   = "metrics.csv"
ITER_FILE  = "last_iter.txt"    

def collect():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mem_mb  = psutil.virtual_memory().used / 1024**2
    cpu_pct = psutil.cpu_percent(interval=0.5)

    hb_count = 0
    one_hour_ago = time.time() - 3600
    with open("logs/soul_heartbeat.log", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                ts = datetime.strptime(line[1:20], "%Y-%m-%d %H:%M:%S")
            except:
                continue
            if ts.timestamp() >= one_hour_ago:
                hb_count += 1

    try:
        with open(ITER_FILE) as f:
            iter_count = int(f.read().strip())
    except:
        iter_count = 0

    write_header = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow([
                "timestamp", "mem_mb", "cpu_pct",
                "hb_last_1h", "iter_count"
            ])
        writer.writerow([
            now,
            round(mem_mb, 2),
            round(cpu_pct, 1),
            hb_count,
            iter_count
        ])

    print(f"[metrics] {now} mem={round(mem_mb,2)}MB cpu={round(cpu_pct,1)}% hb_last_1h={hb_count}")

if __name__ == "__main__":
    collect()
