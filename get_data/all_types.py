import json

with open("get_data\\data.json", "r", encoding="utf-8") as f : 
    data = json.load(f)

def get_types(): 
    types = set()
    
    for item in data : 
        t = item.get("type")
        if t : 
            types.add(t)
    return types

print(get_types())