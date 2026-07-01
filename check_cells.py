import json
with open('proyecto-inmobiliario-global/procesamiento/procesamiento_ideas.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells']):
    if i >= 19 and i <= 23:
        print(f'Cell {i}: id={cell.get("id")}, execution_count={cell.get("execution_count")}, type={cell.get("cell_type")}')
