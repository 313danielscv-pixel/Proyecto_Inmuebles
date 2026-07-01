# Proyecto_Inmuebles

# Idea del proyecto
Analizar el mercado inmobiliario global comparado con la ley Española de ocupación a la vivenda ,con la de otros paises para asegurar los posibles riesgos de la inversión para identificar qué países y tipos de inmuebles ofrecen mejores oportunidades de compra y alquiler desde un presupuesto de salario español, alrededor de 27.336 euros anuales, dependiendo de el ahorro , proyecto conjunto o prestamo


# Fuentes de datos

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


# Resumen de la fase de Pre-procesamiento

En la fase de **pre-procesamiento** preparamos y enriquecemos los datos para su análisis. Es el paso crucial donde transformamos datos dispersos y con formatos inconsistentes en una tabla lista para trabajar.

## Lo que hacemos

**Herramientas y técnicas:**
1. **Importamos librerías clave** (pandas, numpy) para manipulación eficiente de datos — son las herramientas que necesitamos para procesar millones de filas
2. **Creamos un diccionario de normalización de países** porque cada dataset viene con nombres diferentes: "USA" vs "United States", "Reino Unido" vs "UK". Necesitamos que todos usen el mismo nombre para unir sin errores
3. **Implementamos funciones de limpieza** (ej: `clean_location_name()`) para estandarizar ubicaciones y evitar duplicados que podrían falsear nuestros análisis
4. **Generamos nuevas columnas derivadas** (entry_price_eur, zone_rental_price) combinando múltiples variables — es decir, creamos la información que necesitamos (cuánto cuesta realmente invertir, cuánto renta obtendrías) a partir de datos base

**Procesos principales:**
1. **Unión de datos**: Mezclamos el catálogo de 147k inmuebles con factores de contexto país (GDP, delincuencia, educación, geografía) para que cada propiedad tenga su contexto macroeconomico
2. **Estimación de costes iniciales**: No es lo mismo el precio de venta que lo que realmente cuesta entrar. Calculamos entry_price_eur incluyendo entrada hipotecaria típica + gastos de compra
3. **Proyección de alquiler**: Si compras y lo alquilas, ¿cuánto ganas mensualmente? Estimamos zone_rental_price basándose en el rendimiento esperado del mercado
4. **Geolocalización**: Asignamos coordenadas precisas (latitud/longitud) a cada inmueble para poder visualizarlos en mapas — sin esto no sería posible ver dónde están

## Resultado
Un dataset limpio y enriquecido con todas las columnas necesarias: precio, ubicación real, características del inmueble, contexto país y estimaciones financieras realistas. Este es nuestro punto de partida para el análisis.


# Resumen de la fase de Procesamiento

En la fase de **procesamiento** transformamos los datos limpios en un análisis de ranking de oportunidades inmobiliarias:

## Lo que hacemos
Aplicamos un sistema de **puntuación multicomponente** que evalúa cada país considerando:
- **Seguridad jurídica**: Análisis del riesgo de ocupación ilegal, leyes de ocupación y índices de crimen
- **Rentabilidad**: Proximidad al rango de precio objetivo (30k EUR) y renta mínima (1.200€/mes)
- **Ubicación**: Preferencia urbana vs. playas


## Resultado
Generamos dos rankings de países según criterios de filtrado:
- **Top 20 ampliado**: Precio 30k-100k EUR (13 países disponibles)
- **Top 8 estricto**: Precio 30k-45k EUR + rent ≥1.200€ (máxima seguridad financiera)

## Visualización interactiva
Un dashboard en **Streamlit** que permite:
- Ver el mapa mundial con países destacados y scores
- Girar una "ruleta de oportunidad" (scoring 1-10)
- Buscar países específicos y ver detalles financieros y politicas de actuación de la ley frente a la ocupación ilegal
- Comparar inversiones con datos visuales claros 





