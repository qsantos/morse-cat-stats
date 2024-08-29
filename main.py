import gzip
import json

import matplotlib.pyplot as plt
import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

characters = pd.DataFrame(pd.json_normalize(data["characters"]))
characters["time"] = pd.to_datetime(characters["sent.time"], format="ISO8601").fillna(method="ffill")  # or characters["received.time"]
characters = characters.sort_values("time").reset_index(drop=True)
print(characters)

sessions = pd.DataFrame(data["sessions"])
sessions["started"] = pd.to_datetime(sessions["started"], format="ISO8601")
sessions = sessions.sort_values("started").reset_index()
print(sessions)

print()

correct = (characters.result == "Correct").sum()
total = len(characters.index)
success_rate = correct / total

print(f"Global success rate: {success_rate * 100:.1f}%")

characters["correct"] = characters.result == "Correct"
characters.rolling(window=10000).correct.mean().plot()
plt.show(block=True)

sessions.rolling(window=1000).score.mean().plot()
plt.show(block=True)
