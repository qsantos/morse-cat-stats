#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib>=3.10.0",
#     "pandas>=2.2.3",
#     "pyqt5>=5.15.11",
# ]
# ///
import gzip
import json

from argparse import ArgumentParser
import matplotlib.pyplot as plt
import pandas as pd

parser = ArgumentParser()
parser.add_argument("file", help="For instance, morse-cat-data.json.gz")
args = parser.parse_args()

opener = gzip.open if args.file.endswith("gz") else open
with opener(args.file) as f:
    data = json.load(f)


def to_time(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="ISO8601")


def plot_daily_rolling_extending(s: pd.Series, title: str):
    # Plot daily
    daily = s.resample('D').mean().dropna()
    daily.plot()
    # Plot rolling average of daily
    daily.rolling(window=10).mean().plot()
    # Plot expanding average
    s.expanding().mean().plot(title=title)
    # Show setting changes
    for time, label in diffs:
        # draw a faint red line
        plt.axvline(time, color='red')
        plt.text(time, plt.ylim()[1], label, rotation=90, verticalalignment='bottom', fontsize=8)
    # Add legend
    plt.legend(["Daily average", "10-day rolling average", "Expanding average"])
    # Actual draw
    plt.show(block=True)


sessions = pd.DataFrame(data["sessions"])
sessions["started"] = to_time(sessions["started"])
sessions["finished"] = to_time(sessions["finished"])
sessions.index = sessions["started"]
sessions = sessions.sort_index()

# Find days when settings changed
prev_settings = sessions['settings'].shift()
changes = sessions[sessions['settings'] != prev_settings]
diffs = []
for idx, row in changes.iterrows():
    prev_values = prev_settings.loc[idx]
    diff = []
    for key, value in row['settings'].items():
        prev_value = prev_values.get(key) if prev_values is not None else None
        if value != prev_value:
            diff.append(f"{key}:{prev_value}→{value}")
    diffs.append((idx.date(), ', '.join(diff)))

characters = pd.DataFrame(pd.json_normalize(data["characters"]))
characters["time"] = to_time(characters["sent.time"]).ffill()
characters = characters.set_index("time")
characters = characters.sort_index()

# Filter out days with too few data points, which lead to meaningless outliers
counts = characters["sent.time"].resample('D').count()
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

# Plot session duration
elapsed = (sessions["finished"] - sessions["started"]).dt.total_seconds()
plot_daily_rolling_extending(elapsed, "Session duration")

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
