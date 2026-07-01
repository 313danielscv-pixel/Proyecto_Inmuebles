import json

# Load notebook
with open('proyecto-inmobiliario-global/procesamiento/procesamiento_ideas.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# New code for cell (the Top 20 logic cell at index 21)
new_code = """# ===== TOP 20 GLOBAL: MEJOR PISO DE CADA PAÍS (España en puesto 3) =====
import requests

print('='*120)
print('GENERANDO TOP 20: El mejor piso de cada uno de los 20 mejores países (España en puesto 3)')
print('='*120)

# 1. Filtrar pisos con URLs válidas
pisos_con_url = work[
    (work['url'].notna()) & 
    (work['url'] != '') & 
    (work['score_oportunidad'].notna()) &
    (work['latitude'].notna()) &
    (work['longitude'].notna())
].copy()

print(f'\\nTotal pisos disponibles: {len(pisos_con_url):,}')

# 2. Obtener el mejor piso por país
print(f'\\nSELECCIONANDO MEJOR PISO POR PAÍS:')
print('-'*120)

top_por_pais = (
    pisos_con_url
    .sort_values(['country', 'score_oportunidad'], ascending=[True, False])
    .drop_duplicates('country', keep='first')
    .sort_values('score_oportunidad', ascending=False)
)

# Extraer España para posicionarla en puesto 3
paises_forzados = ['Spain']
top20_forced = []

for pais in paises_forzados:
    pais_data = top_por_pais[top_por_pais['country'] == pais]
    if len(pais_data) > 0:
        top20_forced.append(pais_data.iloc[0])
        print(f'✓ Forzado en puesto 3: {pais} (Score: {pais_data.iloc[0]["score_oportunidad"]:.2f})')

# Obtener los demás países (excluyendo España)
otros = top_por_pais[~top_por_pais['country'].isin(paises_forzados)]
top_2 = otros.head(2)  # Primeros 2 puestos
rest = otros.iloc[2:].head(17)  # El resto (máximo 17 para llegar a 20 total)

# Combinar: Top 2 + España (puesto 3) + resto
import pandas as pd
top20_global = pd.concat([top_2, pd.DataFrame(top20_forced), rest], ignore_index=True).reset_index(drop=True)

# Asegurar máximo 20
top20_global = top20_global.head(20).reset_index(drop=True)

print(f'\\nTop 20 PAÍSES (por score del mejor piso):')
for rank, (_, prop) in enumerate(top20_global.iterrows(), 1):
    country = str(prop.get('country', 'N/A'))
    score = prop.get('score_oportunidad', 0)
    price = str(prop.get('price_in_Euro', 'N/A'))
    location = str(prop.get('location', 'N/A'))
    forced = ' ⭐ EN PUESTO 3' if country in paises_forzados else ''
    print(f'{rank:2d}. {country:20s} | Score: {score:6.2f} | {price:15s} | {location[:35]}{forced}')

print(f'\\nVerificando URLs...')
urls_status = []
for rank, (_, prop) in enumerate(top20_global.iterrows(), 1):
    url = str(prop.get('url', ''))
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.head(url, timeout=5, headers=headers, allow_redirects=True)
        status = '✅' if response.status_code == 200 else f'⚠️ {response.status_code}'
    except:
        status = '⚠️ TIMEOUT'
    urls_status.append(status)

top20_global['url_status'] = urls_status
print(f'\\n✓ Top 20 por país verificado y listo (España en puesto 3)')
"""

# Split into lines for notebook cell source
code_lines = new_code.split('\n')
source = [line + '\n' for line in code_lines[:-1]] + [code_lines[-1]]

# Find cell 21 (the Top 20 cell with id 8941db92, execution_count 58)
cell = notebook['cells'][21]
if cell.get('id') == '8941db92':
    cell['source'] = source
    print(f"✓ Modified cell 21 (id={cell.get('id')})")
    
    # Save notebook
    with open('proyecto-inmobiliario-global/procesamiento/procesamiento_ideas.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
    print("✓ Notebook saved successfully")
else:
    print(f"ERROR: Expected cell 21 to have id=8941db92, but got {cell.get('id')}")
