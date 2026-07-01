# Proyecto_Inmuebles

# Idea del proyecto
Analizar el mercado inmobiliario global comparado con la ley Española de ocupación a la vivenda ,con la de otros paises para asegurar los posibles riesgos de la inversión para identificar qué países y tipos de inmuebles ofrecen mejores oportunidades de compra y alquiler desde un presupuesto de salario español, combinando datos de propiedades con indicadores macroeconómicos y sociales.


# Resumen del pre-procesamiento
- Dataset principal cargado: 147.536 filas y 28 países únicos.
- El dataset principal tenía 15 columnas tras añadir `country_norm` antes de la unión.
- La unión final quedó en 147.536 filas y 38 columnas.


# Estado actual (2026-06-29)
- Dataset operativo para BI: 144.961 filas y 41 columnas.
- Export listo para Power BI: `proyecto-inmobiliario-global/pre-procesamiento/processed_powerbi_es.csv`.
- Formato Power BI ES aplicado: separador `;`, decimal `,`, codificación `utf-8-sig`.
- Columnas geográficas disponibles:
	- `latitude` / `longitude`: coordenada de país.
	- `latitud_inmueble` / `longitud_inmueble`: coordenada por ubicación de inmueble (cuando hay resolución específica).


# Nueva columna financiera
- Columna añadida: `entry_price_eur`.
- Significado: estimación del capital inicial en euros para poder tomar posesión del inmueble.
- Resumen incluido en una sola cifra por vivienda: entrada + plus de gastos de compra/posesión.
- Fórmula aplicada:
	- `entry_price_eur = price_in_Euro_calculo * total_initial_pct_country`


# Nueva columna de alquiler estimado
- Columna añadida: `zone_rental_price` (renombrada desde `rent_building_country_eur_monthly_est`).
- Significado: estimación del ingreso mensual en euros si el inmueble ya es tuyo y lo alquilas al precio medio de mercado de la zona.
- Fórmula aplicada:

$$
\text{rent\_base\_monthly} = \frac{\text{price\_in\_Euro\_calculo} \times 0{,}06}{12}
$$

$$
\text{zone\_rental\_price} = \text{mediana}\left(\text{rent\_base\_monthly}\right)_{\text{country},\ \text{apartament\_m2}}
$$

- Criterio de cálculo:
	- Se asume un yield bruto anual de referencia del **6%** sobre el precio de compra.
	- El valor por fila es la **mediana del grupo** (`country` + `apartament_m2`) para reflejar el precio medio de la zona, no el valor individual.
	- Fallback: si el grupo no tiene valores suficientes, se usa la mediana por país.
- Formato visual: igual que `price_in_Euro` — separador de miles con `.`, decimales con `,` y símbolo `€` (ej: `1.395 €`, `876,53 €`).
- Uso recomendado en BI:
	- Ver cuánto generaría mensualmente el inmueble si se alquila.
	- Comparar precio de compra vs renta estimada.
	- Construir indicadores de rentabilidad (yield bruto, payback aproximado).


# Fuente y criterio de cálculo (entry_price_eur)
- Esta columna es una estimación orientativa para analítica BI (no asesoría legal/hipotecaria).
- Se ha usado un porcentaje total por país (`total_initial_pct_country`) que resume:
	- porcentaje de entrada hipotecaria típico,
	- más gastos de cierre/compra para llegar a posesión.
- Referencias utilizadas para construir el criterio:
	- Global Property Guide (rangos de costes de compra por país): https://www.globalpropertyguide.com/
	- Banco de España (costes habituales de compraventa/hipoteca en España): https://clientebancario.bde.es/
	- CFPB - Consumer Financial Protection Bureau (costes de cierre y entrada en EE. UU.): https://www.consumerfinance.gov/
- Regla de fallback para países sin porcentaje específico en el mapeo: `30%` del precio en euros.


# Geocodificación de inmuebles (en curso)
- Caché incremental: `proyecto-inmobiliario-global/pre-procesamiento/geocode_location_cache.csv`.
- Snapshot de progreso: 5.940 consultas cacheadas.
- Resultado actual de la caché: 5.883 `ok` y 57 `not_found`.
- Se usa reintento automático para rate-limit/timeouts y fallback por coordenada país para mantener tabla completa en Power BI.


# Fuentes Kaggle (Markdown)

## world_real_estate_data(147k).csv
- Fuente: Kaggle Dataset (listado global de inmuebles con precio, ubicacion y caracteristicas de vivienda)
- Enlace: [Kaggle](https://www.kaggle.com/datasets/toriqulstu/worlds-real-estate-data147k)

## countries_by_gpd_(ppp).csv
- Fuente: Kaggle Notebook/Referencia (contexto macroeconomico por pais, incluyendo variables usadas en analisis comparativos)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## countries_by_income_equality.csv
- Fuente: Kaggle Notebook/Referencia (desigualdad por pais, indicador tipo Gini para contexto social)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## countries_by_population_(united nations).csv
- Fuente: Kaggle Notebook/Referencia (poblacion por pais y variaciones anuales para contexto demografico)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## crime_index_by_country.csv
- Fuente: Kaggle Notebook/Referencia (indices de crimen y seguridad por pais)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## unemployment_rate_by_country.csv
- Fuente: Kaggle Notebook/Referencia (tasas de desempleo por pais con valores actuales y previos)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## countries_by_latitude.csv
- Fuente: Kaggle Notebook/Referencia (coordenadas geograficas por pais para mapas y analisis espaciales)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## plotly_countries_and_codes.csv
- Fuente: Kaggle Dataset (codigos ISO y mapeo de paises para visualizaciones, por ejemplo en Plotly)
- Enlace: [Kaggle](https://www.kaggle.com/datasets/mauricioasperti/crime-index)

## cost_of_living.csv
- Fuente: Kaggle Dataset (indices de costo de vida por pais y periodo)
- Enlace: [Kaggle](https://www.kaggle.com/datasets/naifnoor/global-cost-of-living-index-by-country-20182026/)

## countries_by_area.csv
- Fuente: Kaggle Notebook/Referencia (superficie territorial por pais para contexto geografico)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

## Densidad_poblacion.csv
- Fuente: Kaggle Dataset (densidad de poblacion por pais, habitantes por km2)
- Enlace: [Kaggle](https://www.kaggle.com/datasets/varpit94/world-population-density)

## education_index_by_country.csv
- Fuente: Kaggle Notebook/Referencia (indice educativo por pais para contexto social)
- Enlace: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)




# Próximos pasos
- Finalizar geocodificación por ubicación para reducir `not_found`.
- Consolidar export final de `processed_powerbi_es.csv` tras cerrar la caché.
- Revisar `not_found` frecuentes y normalizar ubicaciones ambiguas.
- Hacer el EDA con conclusiones por gráfico.
- Montar el producto final.



## Objetivo de esta sesión
- Corregir recomendaciones globales para mostrar Top 20 (1 mejor inmueble por país).
- Mantener mapa + tarjetas finales como salida principal.
- Eliminar UAE de la selección forzada.
- Forzar presencia de España en posición 3.

## Problema detectado
- El notebook acumuló múltiples celdas de prueba y versiones intermedias.
- Hay duplicación de bloques (Top 5, búsquedas de URLs, versiones de tarjetas y versiones de Top 20).
- La celda activa de Top 20 todavía contiene lógica antigua con `paises_forzados = ['Spain', 'UAE']`.

## Estado técnico actual
- Archivo en uso: `proyecto-inmobiliario-global/procesamiento/procesamiento_ideas.ipynb`.
- Variables base funcionando:
	- `df` cargado desde `processed_powerbi_es.csv`.
	- `work` con `score_oportunidad` calculado.
- Visualización final existente:
	- Celda de tarjetas/mapa Top 20 usa `top20_global`.
- Bloque pendiente de corrección:
	- La generación de `top20_global` sigue incluyendo UAE.

## Lógica final acordada (objetivo)
1. Construir `top_por_pais` (mejor inmueble por país por score).
2. Excluir solo España del ranking natural.
3. Tomar top 2 natural (`top_2`).
4. Insertar España en posición 3.
5. Completar hasta 20 con el resto.

Resultado esperado de ranking:
- #1 Georgia (score alto natural)
- #2 Austria (score alto natural)
- #3 Spain (forzado)
- UAE fuera del Top 20 forzado

## Alcance que se quiere dejar en el notebook
- Mantener:
	- Carga de datos
	- Cálculo de score
	- Top 20 global (limpio)
	- Mapa + tarjetas finales
- Sacar o ignorar para flujo principal:
	- Celdas antiguas de Top 5
	- Celdas de scraping/búsquedas de reemplazo de URL
	- Bloques duplicados de tarjetas

## Checklist para retomar (pendiente inmediato)
- [ ] Reescribir celda Top 20 para quitar UAE y forzar España en #3.
- [ ] Ejecutar en orden: carga -> score -> Top 20 -> mapa/tarjetas.
- [ ] Verificar visualmente que UAE no aparezca y España esté en #3.
- [ ] Confirmar que el mapa y tarjetas usen exactamente ese `top20_global`.


## Estado aplicado (2026-07-01)
- ✅ Celda Top 20 final aplicada y ejecutada con estas reglas:
	- Excluir `UAE`.
	- Forzar `Spain` en posición #3.
	- Filtrar rentabilidad mínima: `rent_eur_month_num >= 1000`.
	- Filtrar eficiencia: `payback_years <= 20`.
- ✅ Celda de mapa + tarjetas finales aplicada y ejecutada sobre `top20_global`.
- ✅ Se confirma el caso de negocio que pediste: evitar oportunidades de poca renta (ej. ~200/mes).


## Power BI (entrega final en 2 páginas)

### ¿Hace falta Power Query?
- Sí, recomendable para limpiar y tipar columnas (precio, renta, payback, coordenadas) antes de visuales.
- No hace falta descargar nada externo obligatorio para arrancar.

### Fuente recomendada para el reporte
- Usar `proyecto-inmobiliario-global/pre-procesamiento/processed_powerbi_es.csv`.
- Si quieres exactamente el Top 20 filtrado final del notebook, exportar también una tabla final desde notebook (sugerido nombre: `top20_global_final.csv`).

### Página 1 (Resumen Ejecutivo)
- KPI Cards:
	- Total inmuebles válidos
	- Renta media mensual
	- Payback medio
	- Score medio
- Tabla ranking Top 20:
	- `country`, `location`, `price_in_Euro`, `zone_rental_price`, `score_oportunidad`, `payback_years`
- Barras por país:
	- Eje X: país
	- Eje Y: score_oportunidad (o renta media)
	- Tooltip: precio, renta, payback

### Página 2 (Mapa interactivo)
- Visual mapa (Azure Maps o ArcGIS Maps for Power BI):
	- Latitud: `latitude`
	- Longitud: `longitude`
	- Tamaño punto: `score_oportunidad`
	- Color punto: `payback_years` (menor mejor)
- Capa heatmap / densidad:
	- Activar capa de densidad para concentraciones de oportunidad.
- Segmentadores (slicers):
	- País
	- Rango de renta mensual (`>= 1000`)
	- Rango de payback (`<= 20`)

### Medidas DAX recomendadas
```DAX
Renta Mensual Num = VALUE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE([zone_rental_price], "€", ""), ".", ""), ",", "."))

Precio Num = VALUE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE([price_in_Euro], "€", ""), ".", ""), ",", "."))

Payback Years = DIVIDE([Precio Num], [Renta Mensual Num] * 12)

Es Rentable = IF([Renta Mensual Num] >= 1000 && [Payback Years] <= 20, 1, 0)
```

### Filtros finales del reporte
- Filtro de página: `Es Rentable = 1`
- Excluir país: `country <> "UAE"`
- Si quieres fijar España #3 en la tabla visual, usar orden personalizado (columna ranking calculada en Power Query o DAX).
