import gzip
import json

import matplotlib.pyplot as plt
import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

def to_time(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="ISO8601")


def plot_daily_rolling_extending(s: pd.Series, title: str):
    # Plot daily
    daily = s.resample('d').mean().dropna()
    daily.plot()
    # Plot rolling average of daily
    daily.rolling(window=10).mean().plot()
    # Plot expanding average
    s.expanding().mean().plot(title=title)
    plt.legend(["Daily average", "10-day rolling average", "Expanding average"])
    plt.show(block=True)


characters = pd.DataFrame(pd.json_normalize(data["characters"]))
characters["time"] = to_time(characters["sent.time"]).ffill()
characters = characters.set_index("time")
characters = characters.sort_index()

sessions = pd.DataFrame(data["sessions"])
sessions["started"] = to_time(sessions["started"])
sessions = sessions.set_index("started")
sessions = sessions.sort_index()

# Filter out days with too few data points, which lead to meaningless outliers
counts = characters["sent.time"].resample('d').count()
for day_to_exclude in counts[(0 < counts) & (counts < 1000)].index:
    # NOTE: could be optimized with datetime range test if needed
    characters = characters[characters.index.date != day_to_exclude.date()]
    sessions = sessions[sessions.index.date != day_to_exclude.date()]

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

# Plot accuracy
plot_daily_rolling_extending(correct, "Accuracy")

# Plot score per session
plot_daily_rolling_extending(sessions.score, "Score per session")

# Plot latency (in ms)
correct_characters = characters[correct]
latency = pd.to_numeric(to_time(correct_characters["received.time"]) - to_time(correct_characters["sent.time"])) * 1e6
plot_daily_rolling_extending(latency, "Latency (ms)")

# Plot mistake frequencies
for sent_character, received_character in common_mistakes.index[:10]:
    s = (mistakes["sent.character"] == sent_character) & (mistakes["received.character"] == received_character)
    plot_daily_rolling_extending(s, f"Frequency among mistakes: {sent_character.upper()} was sent, but user typed {received_character.upper()}")
