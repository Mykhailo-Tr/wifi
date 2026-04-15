from flask import Flask, jsonify, render_template
import subprocess
import re
from collections import deque

app = Flask(__name__)

TARGET_IP = "8.8.8.8"
history = deque(maxlen=20)

def get_ping():
    try:
        result = subprocess.check_output(
            ["ping", "-c", "1", TARGET_IP],
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
        return 0, 1

    history.append(ping)

    if len(history) < 5:
        return 0, 1

    sorted_hist = sorted(history)
    median = sorted_hist[len(sorted_hist)//2]

    diff = abs(ping - median)

    movement = min(diff / (median + 20), 1)

    # 🔥 псевдо-дистанція
    distance = 1 - movement  # 0 = близько, 1 = далеко

    print(f"PING={ping:.2f} DIFF={diff:.2f} MOVE={movement:.3f} DIST={distance:.3f}")

    return movement, distance


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def data():
    movement, distance = get_movement()
    
    return jsonify({
        "movement": movement,
        "distance": distance
    })


app.run(host="0.0.0.0", port=5000)
