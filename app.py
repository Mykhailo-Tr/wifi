from flask import Flask, jsonify, render_template
import subprocess
import re
import time
from collections import deque

app = Flask(__name__)

ROUTER_IP = "8.8.8.8"  # зміни якщо треба
history = deque(maxlen=10)

def get_ping():
    try:
        result = subprocess.check_output(
            ["ping", "-c", "1", ROUTER_IP],
            stderr=subprocess.DEVNULL
        ).decode()

        match = re.search(r'time=(\d+\.?\d*)', result)
        if match:
            return float(match.group(1))
    except:
        return None

    return None


def get_movement():
    ping = get_ping()
    
    if ping is None:
        return 0

    history.append(ping)

    if len(history) < 5:
        return 0

    avg = sum(history) / len(history)
    diff = abs(ping - avg)

    # нормалізація (під UI)
    movement = min(diff / 10, 1)

    return movement


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def data():
    movement = get_movement()
    
    return jsonify({
        "movement": movement
    })


app.run(host="0.0.0.0", port=5000)
