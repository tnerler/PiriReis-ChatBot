import json

with open("get_data\\data.json", "r", encoding="utf-8") as f : 
    main = json.load(f)

with open("get_data\\Ders-Icerikleri_BilgisayarMühendisliği.json", "r", encoding="utf-8") as f: 
    new_1 = json.load(f)

main.append(new_1)


with open("get_data/data.json", "w", encoding="utf-8") as f : 
    json.dump(main, f, indent=2, ensure_ascii=False)

