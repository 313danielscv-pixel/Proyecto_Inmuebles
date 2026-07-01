import json

try:
    with open('proyecto-inmobiliario-global/procesamiento/procesamiento_ideas.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print(f'✓ Notebook válido: {len(nb["cells"])} celdas')
    
    # Verificar si VSC-d6349ae4 existe
    found = False
    for i, cell in enumerate(nb['cells']):
        if cell.get('id') == '#VSC-d6349ae4':
            found = True
            print(f'✓ Celda VSC-d6349ae4 encontrada en posición {i}')
            print(f'  Líneas: {len(cell["source"])}')
            break
    
    if not found:
        print('✗ Celda VSC-d6349ae4 NO ENCONTRADA')
        # Listar todas las celdas
        print('\nCeldas disponibles:')
        for i, cell in enumerate(nb['cells']):
            cell_id = cell.get('id', 'SIN ID')
            cell_type = cell.get('cell_type', '?')
            print(f'  {i}: {cell_id} ({cell_type})')
    
except json.JSONDecodeError as e:
    print(f'✗ Error JSON: {e}')
except Exception as e:
    print(f'✗ Error: {e}')
