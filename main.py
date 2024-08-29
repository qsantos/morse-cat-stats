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

mistakes = characters[characters.result == "Incorrect"]
common_mistakes = mistakes[["sent.character", "received.character"]].value_counts()
mistake_grid = common_mistakes.unstack().fillna(0)
print(mistake_grid.to_string())
print(common_mistakes.reset_index().head(50))

sessions = pd.DataFrame(data["sessions"])
sessions["started"] = pd.to_datetime(sessions["started"], format="ISO8601")
sessions = sessions.sort_values("started").reset_index()
print(sessions)

print()

correct = (characters.result == "Correct").sum()
total = len(characters.index)
success_rate = correct / total

print(f"Global success rate: {success_rate * 100:.1f}%")

rolling = (characters.result == "Correct").rolling(window=10000).mean()
rolling.index = pd.to_datetime(pd.to_numeric(characters["time"]).rolling(window=10000).min())
rolling.plot()
plt.show(block=True)

rolling = sessions.rolling(window=1000).score.mean()
rolling.index = pd.to_datetime(pd.to_numeric(sessions["started"]).rolling(window=1000).min())
rolling.plot()
plt.show(block=True)
