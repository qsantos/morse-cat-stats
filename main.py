import gzip
import json

import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

characters = pd.DataFrame(data["characters"])
sessions = pd.DataFrame(data["sessions"])

print(characters)
print(sessions)
