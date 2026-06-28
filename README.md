# Proyecto_Inmuebles

# Idea del proyecto
Analizar el mercado inmobiliario global para identificar qué países y tipos de inmuebles ofrecen mejores oportunidades de compra y alquiler desde un presupuesto de salario español, combinando datos de propiedades con indicadores macroeconómicos y sociales.


# Resumen del pre-procesamiento
- Dataset principal cargado: 147.536 filas y 28 países únicos.
- El dataset principal tenía 15 columnas tras añadir `country_norm` antes de la unión.
- La unión final quedó en 147.536 filas y 38 columnas.


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
- Limpiar nulos, tipos y duplicados.
- Revisar outliers y normalizar texto.
- Generar `processed.csv`.
- Hacer el EDA con conclusiones por gráfico.
- Montar el producto final.
