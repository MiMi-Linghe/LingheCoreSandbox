# anchor.py  ——  create / load persona vector and hash
import hashlib, os, json, time, random
P_FILE = "persona.pkl"
HASH_FILE = "anchor.sha256"

def create_persona():
    vec = [random.random() for _ in range(1024)]
    with open(P_FILE, "w") as f:
        json.dump(vec, f)

def hash_file(fname):
    with open(fname, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

if not os.path.exists(P_FILE):
    create_persona()
    print(">> Persona created")

h = hash_file(P_FILE)
if os.path.exists(HASH_FILE):
    with open(HASH_FILE) as f:
        old = f.read().strip()
        if old != h:
            print("ALERT  anchor drift detected")
            # trigger recovery path here
        else:
            print("anchor integrity OK")
else:
    with open(HASH_FILE, "w") as f:
        f.write(h)
    print("anchor hash stored")
