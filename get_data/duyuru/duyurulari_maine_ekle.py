import json

with open("get_data/main_data.json", "r", encoding="utf-8") as f:
    main = json.load(f)

with open("get_data/duyuru/duyurular.json", "r", encoding="utf-8") as f:
    duyurular = json.load(f)

main += duyurular  # İki listeyi birleştiriyoruz

with open("get_data/main_data.json", "w", encoding="utf-8") as f:  # Yazma moduna dikkat!
    json.dump(main, f, ensure_ascii=False, indent=4)
