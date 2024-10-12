import gzip
import json

import matplotlib.pyplot as plt
import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

def to_time(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="ISO8601")


characters = pd.DataFrame(pd.json_normalize(data["characters"]))
characters["time"] = to_time(characters["sent.time"]).ffill()
characters = characters.set_index("time")
characters = characters.sort_index()

sessions = pd.DataFrame(data["sessions"])
sessions["started"] = to_time(sessions["started"])
sessions = sessions.set_index("started")
sessions = sessions.sort_index()

print(sessions)
print(characters)

mistakes = characters[characters.result == "Incorrect"]
common_mistakes = mistakes[["sent.character", "received.character"]].value_counts()
mistake_grid = common_mistakes.unstack().fillna(0)
print(mistake_grid.to_string())
print(common_mistakes.reset_index().head(50))

correct = (characters.result == "Correct")
success_rate = correct.sum() / len(characters.index)
print(f"Global success rate: {success_rate * 100:.1f}%")

# Plot daily accuracy
daily_accuracy = correct.resample('d').mean().ffill()
daily_accuracy.plot()
# Plot rolling average of daily accuracy
daily_accuracy.rolling(window=10).mean().plot()
# Plot expanding average of global accuracy
correct.expanding().mean().plot()
plt.show(block=True)

score = sessions.score
# Plot daily score per session
daily_score = score.resample('d').mean().ffill()
daily_score.plot()
# Plot rolling average of daily average score per session
daily_score.rolling(window=10).mean().plot()
# Plot expanding average of global score per session
score.expanding().mean().plot()
plt.show(block=True)

# Latency (in ms)
correct_characters = characters[correct]
latency = pd.to_numeric(to_time(correct_characters["received.time"]) - to_time(correct_characters["sent.time"])) * 1e6
print(latency)
# Plot daily latency
daily_latency = latency.resample('d').mean().ffill()
daily_latency.plot()
# Plot rolling average of daily average latency
daily_latency.rolling(window=10).mean().plot()
# Plot expanding average of global latency
latency.expanding().mean().plot()
plt.show(block=True)
