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
        return 0

    history.append(ping)

    if len(history) < 5:
        return 0

    # 🔹 медіана (стабільніше ніж середнє)
    sorted_hist = sorted(history)
    median = sorted_hist[len(sorted_hist)//2]

    diff = abs(ping - median)

    # 🔹 адаптивна нормалізація
    movement = diff / (median + 20)

    # 🔹 згладжування
    movement = min(movement, 1)

    print(f"PING={ping:.2f} MEDIAN={median:.2f} DIFF={diff:.2f} MOVE={movement:.3f}")

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
