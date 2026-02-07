import json
from rich import print

data = {"placeholder": "json"}
print(json.dumps(data, indent=2))