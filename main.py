import gzip
import json

import matplotlib.pyplot as plt
import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

characters = pd.DataFrame(pd.json_normalize(data["characters"]))
characters["time"] = pd.to_datetime(characters["sent.time"], format="ISO8601").ffill()  # or characters["received.time"]
characters = characters.set_index("time")
characters = characters.sort_index()
print(characters)

mistakes = characters[characters.result == "Incorrect"]
common_mistakes = mistakes[["sent.character", "received.character"]].value_counts()
mistake_grid = common_mistakes.unstack().fillna(0)
print(mistake_grid.to_string())
print(common_mistakes.reset_index().head(50))

sessions = pd.DataFrame(data["sessions"])
sessions["started"] = pd.to_datetime(sessions["started"], format="ISO8601")
sessions = sessions.set_index("started")
sessions = sessions.sort_index()
print(sessions)

print()

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
