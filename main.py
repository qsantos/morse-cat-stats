import gzip
import json

import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

characters = pd.DataFrame(data["characters"])
sessions = pd.DataFrame(data["sessions"])

print(characters)
print(sessions)
print()

correct = (characters.result == "Correct").sum()
total = len(characters.index)
success_rate = correct / total

print(f"Global success rate: {success_rate * 100:.1f}%")
