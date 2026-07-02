
# Proyecto_Inmuebles

## Contexto y Motivación

Este proyecto nace de una pregunta simple pero compleja: **¿Dónde puedo invertir en inmuebles de forma segura?**

La realidad es que la inversión inmobiliaria es difícil. No solo tienes que encontrar una propiedad barata — también necesitas:
- Entender los riesgos legales de cada país (¿qué pasa si alguien ilegalmente ocupa tu inmueble?)
- Calcular la rentabilidad real (no solo el precio, sino cuánto ganará en alquiler)
- Considerar el contexto económico y social (desempleo, delincuencia, educación)
- Evaluar ubicación (¿es una zona turística? ¿es zona urbana o rural?)

Nuestro objetivo: **crear un sistema que analice automáticamente el mercado inmobiliario global y rank de oportunidades** considerando TODOS estos factores simultáneamente, desde la perspectiva de un inversor español con presupuesto limitado.

### Objetivo específico

Crear un sistema que identifique oportunidades de compra-alquiler en el mercado inmobiliario global desde la perspectiva de un inversor con estas características:
- Presupuesto: ~30.000€ (ahorro de salario español típico)
- Riesgo tolerance: media (quiero seguridad legal, no casinos)
- Horizonte: 3-10 años (quiero recuperar dinero rápido, no esperar 15 años)
- Geografía: flexible (estoy dispuesto a invertir en cualquier país del mundo)

Comparamos contra la ley española de ocupación como referencia de "seguridad legal" conocida. Y analizamos de otros países (¿qué tan claros son sus marcos legales comparado con España?)


# Fuentes de datos (12 datasets de Kaggle)

## ¿De dónde sacamos toda esta información?

Combinamos 12 datasets de Kaggle. Cada uno responde una pregunta específica:

### 1. world_real_estate_data(147k).csv
**Pregunta:** ¿Cuáles son todas las propiedades disponibles en el mundo?

- **Qué contiene**: 147.000 inmuebles con precio, ubicación, característica (m², tipo, etc.)
- **Importancia**: Es la COLUMNA VERTEBRAL del proyecto. Sin esto, no hay nada.
- **Desafío**: Datos caóticos, con nombres de países en 50+ variantes diferentes
- **Enlace**: [Kaggle](https://www.kaggle.com/datasets/toriqulstu/worlds-real-estate-data147k)

### 2. countries_by_gpd_(ppp).csv
**Pregunta:** ¿Cuál es la salud económica de cada país?

- **Qué contiene**: GDP por país (poder adquisitivo)
- **Por qué importa**: GDP bajo = mercado inmobiliario barato, pero también menos demanda de alquiler
- **Contexto**: Un país con GDP bajo es más barato pero también es más riesgoso
- **Enlace**: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

### 3. countries_by_income_equality.csv
**Pregunta:** ¿Cuán desigual es cada país?

- **Qué contiene**: Índice de Gini (medida de desigualdad económica)
- **Escala**: 0 = igualdad perfecta, 100 = desigualdad máxima
- **Ejemplos**: España ~34, Alemania ~31, Portugal ~35, México ~48
- **Por qué importa**: Desigualdad alta = menos clase media = menos demanda de alquiler
- **Contexto**: México tiene Gini más alto que Europa. Significa: menos gente comprando vivienda, menos turismo interno.
- **Enlace**: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

### 4. countries_by_population_(united nations).csv
**Pregunta:** ¿Cuánta gente vive dónde y eso está creciendo?

- **Qué contiene**: Población por país y tasa de crecimiento anual
- **Por qué importa**: Población creciente = demanda de inmuebles sube (buenos para alquilar)
- **Ejemplo**: India creciendo 1.3% anual = más gente, más viviendas necesarias
- **Enlace**: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

### 5. crime_index_by_country.csv
**Pregunta:** ¿Es seguro vivir/invertir aquí?

- **Qué contiene**: Índices de crimen y seguridad por país
- **Rango**: 0-100 (más alto = más peligroso)
- **Impacto en decisión**: Un piso barato en un país peligroso = más difícil alquilar (menos turismo, menos demanda)
- **Uso**: Lo ponderamos en nuestro scoring (es parte de la evaluación de "seguridad general")
- **Enlace**: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

### 6. unemployment_rate_by_country.csv
**Pregunta:** ¿Cuánta gente está sin trabajo?

- **Qué contiene**: Tasa de desempleo por país
- **Por qué importa**: Desempleo alto = menos gente puede alquilar = renta baja
- **Ejemplo**: España post-2008 tuvo desempleo 25%. La renta de inmuebles cayó porque menos gente podía pagar.
- **Enlace**: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

### 7. countries_by_latitude.csv
**Pregunta:** ¿Dónde está cada país geográficamente?

- **Qué contiene**: Coordenadas (latitud/longitud) de cada país
- **Para qué**: Mapas interactivos. Visualizar dónde están tus oportunidades de inversión.
- **Enlace**: [Kaggle](https://www.kaggle.com/code/mauricioasperti/crime-index-study-and-prediction-by-country)

### 8. education_index_by_country.csv
**Pregunta:** ¿Cuál es el nivel educativo?

- **Qué contiene**: Índice de educación (0-1 scale, donde 1 es máxima educación)
- **Por qué importa**: Educación alta = menos crimen (correlación histórica), más demanda de vivienda de calidad
- **Contexto**: Canadá, Suecia, Alemania tienen índices altos. Mali, Sierra Leone tienen bajos.

### 9. cost_of_living.csv
**Pregunta:** ¿Qué tan cara es la vida en cada país?

- **Qué contiene**: Índice de costo de vida
- **Por qué importa**: Si la vida es cara, también es cara la renta. Si es barata, renta también es barata.

### 10. plotly_countries_and_codes.csv
**Pregunta:** ¿Cuáles son los códigos ISO de cada país?

- **Qué contiene**: Nombre oficial, código ISO de 2 letras (es/pt/th), código ISO de 3 letras
- **Para qué**: Normalizar nombres de países (unificar "USA" = "United States" = "US" en un solo "ES")

### 11. cost_of_living.csv
**Pregunta:** ¿Cuál es la relación entre costo de vida e inmuebles?

- **Qué contiene**: Índice de costo de vida comparado con base 100 (USA)
- **Ejemplo**: Portugal 60, España 65, Tailandia 45
- **Uso**: Ajustar expectativas de renta. Si la vida es 45% más barata, la renta típica también es ~45% más barata.

### 12. Otros datasets (areas, densidad población, etc.)
**Para qué**: Contexto general. Densidad poblacional (¿es zona urbana?), área del país (¿es grande/pequeño?).

### Síntesis: ¿Por qué estos 12 datasets?

Cada uno responde UNA pregunta específica. Juntos, pintan un cuadro:
- **Datos de mercado** (inmuebles, precios): los datasets 1, 10
- **Datos económicos** (GDP, costo vida, empleo): datasets 2, 3, 11
- **Datos de seguridad** (crimen, educación): datasets 5, 8
- **Datos demográficos** (población, densidad): datasets 4, 7, 12, 9

Cuando combinas todo, tienes respuesta a: "¿Qué país, a qué precio, con qué renta, cuán seguro, y cuán sostenible?"


# Resumen de la fase de Pre-procesamiento

En la fase de **pre-procesamiento** preparamos y enriquecemos los datos para su análisis. Es el paso crucial donde transformamos datos dispersos y con formatos inconsistentes en una tabla lista para trabajar.

## Lo que hacemos

**Herramientas y técnicas (lo técnico, pero con propósito real):**

1. **Importamos pandas y numpy** — son las herramientas básicas. Sin ellas, procesar 147.000 filas sería insano. Con ellas, es casi fácil.

2. **Creamos un diccionario de normalización de países** — esto es el verdadero herói silencioso. Imagina que tienes 10 datasets diferentes, todos con el mismo país pero nombres distintos:
   - Dataset 1 dice "USA"
   - Dataset 2 dice "United States of America"
   - Dataset 3 dice "United States"
   - Dataset 4 dice "US"
   
   Sin solucionar esto, tu unión de datos te devuelve 4 países "diferentes" cuando en realidad es 1. Desastre.
   
   Solución: creamos un diccionario centralizado que dice "todos estos nombres = Portugal" y los fuerza a ser iguales.

3. **Implementamos funciones de limpieza** — particularmente `clean_location_name()`. El campo "location" viene sucio:
   - "Lisboa, Portugal" en un dataset
   - "Lisbon, Portugal" en otro
   - "LIsbOa" en otro con errores tipográficos
   
   La función estandariza todo a "Lisboa, Portugal" para que no termines con 100 "Lisboas" diferentes siendo contadas como ciudades distintas.

4. **Generamos nuevas columnas derivadas** — esta es la parte donde CREAMOS información nueva:
   - `entry_price_eur`: el precio de venta NO es lo que te cuesta. Necesitas entrada (30%), gastos de notaría (2-3%), impuestos. Por país esto cambia. En España es ~30%, en Tailandia es ~15%. Creamos una columna que dice "realmente te cuesta X euros", no "la propiedad vale Y euros"
   - `zone_rental_price`: estimamos cuánto rentaría mensualmente basándonos en el rendimiento esperado (6% anual) ajustado por zona y tamaño

**Procesos principales (de verdad, uno a uno):**

1. **Unión de datos**: Imagina que tienes 147k inmuebles pero solo 15 columnas de datos sobre ellos. Casas vacías de información. 
   Tienes otro dataset con contexto de países (GDP, delincuencia, educación). Usamos la columna "país" como llave para unir: "este inmueble en Portugal" + "Portugal tiene GDP = X" = mezclamos todo.
   
   Resultado: cada inmueble ahora conoce el contexto país. Un piso en Lisboa sabe que Portugal tiene desempleo del 5%, educación media de 8.5/10, crimen moderado. Eso es información valiosa.

2. **Estimación de costes iniciales**: Es el paso donde dejamos de soñar y miramos la realidad.
   - Un inmueble cuesta 60.000€ (precio de venta)
   - Pero realmente necesitas: entrada (30%) = 18.000€ + gastos = 4.000€ 
   - entry_price_eur = 22.000€
   
   ¿Por qué importa? Porque si tu presupuesto es 30.000€, necesitas saber que REALMENTE puedes comprar (no si teóricamente en otro planeta).

3. **Proyección de alquiler**: Si compras y lo alquilas, ¿cuánto ganas?
   - Asumimos 6% de rendimiento anual (estándar en mercados razonables)
   - Un piso de 60.000€ genera 3.600€ anuales = 300€ mensuales
   - Pero lo ajustamos por zona (Lisboa es más cara que pueblo rural) y tamaño (apartamento pequeño, mediano, grande)
   - Resultado: zone_rental_price = estimación realista de lo que rentará mensualmente

4. **Geolocalización**: Sin coordenadas precisas, no hay mapa.
   - Usamos APIs de geocoding que convierten "Calle Gran Vía 50, Lisboa" → (38.7223, -9.1393)
   - Esto nos permite plotear cada inmueble en un mapa real
   - Sin esto, tus datos son números en una hoja de Excel. Con esto, ves dónde está el dinero geográficamente.

## Resultado
Un dataset limpio y enriquecido con **41 columnas** que incluyen:
- **Ubicación**: país, localidad, coordenadas precisas (puedes hacerlas clic en Google Maps)
- **Precio e inversión**: precio de venta vs. capital real que necesitas (entry_price_eur)
- **Alquiler**: renta mensual estimada si lo alquilas
- **Contexto país**: GDP (riqueza del país), población (mercado potencial), crimen (seguridad), desempleo (estabilidad), educación (desarrollo)
- **Seguridad jurídica**: ¿Qué protecciones legales tienes si alguien ilegalmente ocupa tu inmueble?
- **Características físicas**: tamaño, dormitorios, baños, extras

Sobre estos datos, **calculamos un score multicomponente** que sintetiza toda la información:

$$\text{score\_oportunidad} = 28\% \times \text{target\_profile} + 18\% \times \text{legal} + 13\% \times \text{yield} + 11\% \times \text{affordability} + 11\% \times \text{location} + 10\% \times \text{payback} + 8\% \times \text{rent} + 1\% \times \text{safety}$$

Este score es el valor fundamental que luego usamos en la fase de procesamiento para el ranking final.


# Resumen de la fase de Procesamiento

En la fase de **procesamiento** transformamos los datos limpios en un análisis de ranking de oportunidades inmobiliarias. Aquí es donde aplicamos toda la "inteligencia" del sistema.

## El desafío: ¿Cómo comparar inmuebles tan diferentes?

Cuando tienes 147.000 propiedades en 28 países, es IMPOSIBLE decidir solo. ¿Inviertes en Lisboa (60k€, rent 900€) o en Bangkok (40k€, rent 1.200€)?

- Lisboa: país estable, legal claro, pero menos rentable
- Bangkok: más rentable, pero mayor riesgo legal

¿Cómo comparas? Hay que ser honesto: no hay respuesta perfecta. Pero hay respuestas INFORMADAS.

Por eso creamos un **sistema de scoring**: convertir cada propiedad en un número (0-100) que resume: "¿Qué tan bueno es este inmueble para mí, considerando TODO?"

Es como comparar móviles. Un móvil A tiene mejor cámara, otro B tiene mejor batería. No puedes decir "A es mejor", pero SÍ puedes hacer un scoring que diga "considerando cámara, batería, precio y rendimiento, el A sacaeste puntuación".

## Lo que hacemos

**Factor 1: Seguridad jurídica (18% del score)**
Pregunta real: ¿Si invierto en este país, qué pasa si alguien ILEGALMENTE ocupa mi propiedad?

- En España: hay leyes claras, puedes desalojar (aunque tarda meses)
- En Portugal: muy similar a España
- En Vietnam: ¿leyes? Poco documentadas, mayor riesgo
- En Tailandia: riesgo, porque los extranjeros no pueden poseer tierra directamente

Medimos:
- Riesgo de ocupación (bajo/medio/alto)
- Presencia de leyes documentadas
- Índice de crimen país (indicador de orden general)

**Factor 2: Objetivo precio-renta (28% del score)** — EL MÁS IMPORTANTE
Pregunta: ¿Este inmueble está en mi rango realista?

Definimos un objetivo: queremos 30k€ de entrada Y 1.200€/mes de renta.

Para cada inmueble, medimos: ¿cuán cerca está de ambos objetivos?

- Piso en Tailandia: 25k entrada (bueno), 1.500€ renta (muy bueno) → score alto
- Piso en Portugal: 20k entrada (excelente), 900€ renta (por debajo objetivo) → score medio
- Piso en Paris: 50k entrada (lejos), 2.000€ renta (bueno) → score bajo

**Factor 3: Rentabilidad (13% yield + 10% payback + 8% renta = 31% TOTAL)**
Pregunta: ¿Me va a hacer dinero este inmueble?

Yield: ¿Cuál es el rendimiento anual histórico?
- España: típicamente 3-4% (casas caras, renta baja)
- Portugal: 4-5% (mejor)
- Tailandia: 6-8% (muy bueno pero riesgo legal)

Payback: ¿Cuántos años hasta recuperar mi dinero?
- 2 años: excelente (recuperas rápido, puedes vender y reinvertir)
- 5 años: bueno
- 10 años: aceptable
- 15+ años: malo (tu dinero está congelado demasiado tiempo)

Renta mensual: simple, ¿cuánto dinero tienes cada mes?

**Factor 4: Ubicación (11% del score)**
Pregunta: ¿Será fácil alquilarlo o venderlo después?

- Zona urbana: 70% puntuación
- Zona playa (turística): 100% puntuación
- Zona rural: 30% puntuación

¿Por qué? Porque alquilar un piso en centro de Lisboa es fácil (turismo, negocios). Alquilar en campo serbio es complicado.

**Factor 5: Otros (affordability, safety, crime = 12%)**
- ¿Está dentro de mi presupuesto inicial?
- ¿Es un país seguro en general (no solo legalmente)?
- ¿Cómo es la delincuencia callejera?

## Resultado
Generamos dos rankings:

- **Top 13 ampliado**: Precio 30k-100k EUR + rent documentado — son los 13 mejores que encontramos que cumplen criterios amplios
- **Top 8 estricto**: Precio 30k-45k EUR AND rent ≥1.200€/mes — solo los que cumplen TODO sin excepciones. Oro puro.

Cada país tiene un **score de oportunidad (0-100%)** que puedes entender y explicar. No es "magia", es matemáticas transparentes.

## Cómo visualizamos esto
Un dashboard web (Streamlit) que muestra:
- Mapa interactivo: dónde está el dinero
- Ruleta: comparación visual entre países
- Gráficos: patrones y tendencias
- Tabla: datos verificables con enlaces reales

(Más detalle de todo esto en la sección de Dashboard, que es donde realmente cobra sentido)


# Visualización: El Dashboard Streamlit

Aunque toda la lógica y análisis está en los notebooks, la **verdadera magia ocurre cuando los datos cobran vida en el dashboard web**. Ahí es donde el usuario final puede explorar, entender y tomar decisiones.

El dashboard es un **Streamlit app** que transforma tablas frías de números en una experiencia visual interactiva:
- **Página 1**: Métricas globales, mapa interactivo, gráficos de tendencias, tabla Top 13
- **Página 2**: Ruleta de scoring, búsqueda por país, tabla Top 8 estricto

¿Cómo funciona? Cargas el CSV con los 13 países, y el dashboard computa dinámicamente todos los scores visibles: "esta oportunidad tiene 82% en seguridad, 71% en rentabilidad, 88% en precio".

**Para la presentación en clase**, lee la sección "**PRESENTACIÓN EN VIVO DEL DASHBOARD**" (más abajo) donde explicamos exactamente qué ve el usuario, cómo interactúa, y por qué es especial este dashboard.

Por ahora, solo recuerda: **los datos son lo importante, pero la visualización es lo que hace posible que alguien los entienda en 2 minutos.**


# Concepto: Payback Years (Años de Recuperación)

Antes de invertir, quieres saber: **¿Cuánto tarda mi dinero en volver a mis bolsillos?**

**Payback years** responde exactamente eso: cuántos años hasta que la renta acumulada iguala tu inversión inicial.

**Fórmula:**
$$\text{payback\_years} = \frac{\text{entrada realista en EUR}}{\text{renta mensual} \times 12}$$

**Ejemplo real:** Una propiedad te cuesta 30.000€ (entrada realista) y genera 1.200€/mes de renta:
- Renta anual: 1.200€ × 12 = 14.400€
- Payback: 30.000 ÷ 14.400 = **2,1 años**

Significa: en 2 años y 1 mes, recuperas TODO tu dinero. Luego cada mes los 1.200€ son ganancia pura.

**¿Por qué es importante?**

- **2-3 años**: Excelente. Recuperas rápido, puedes reinvertir en otro lugar. Compounding potencial.
- **5 años**: Bueno. Estándar en mercados sanos.
- **8-10 años**: Aceptable. Típico de mercados desarrollados (Madrid, Barcelona).
- **15+ años**: Malo. Tu dinero está congelado demasiado tiempo. Mejor meterlo en banco o acciones.

En nuestro análisis, **Top 8 estricto tiene payback de 2-4 años**. Compare con España (típicamente 8-12 años). Eso es la diferencia entre una oportunidad real y un mercado estancado.


# Desafíos y decisiones clave

# Desafíos y decisiones clave (historias reales del proyecto)

**1. Normalización de datos dispersos (el caos inicial)**

*Problema:* Cada dataset venía de fuente diferente. Los nombres de países eran un desastre:
- Dataset 1 dice "USA" 
- Dataset 2 dice "United States"
- Dataset 3 dice "US"
- Dataset 4 dice "United States of America"
- Dataset 5 dice "America"

*Intentamos:* La unión directa. Error masivo. Terminábamos con 5 "países" diferentes siendo 1 solo.

*Solución:* Crear un diccionario centralizado donde mapeamos TODAS las variantes a un nombre oficial. Fue tedioso (40+ variantes para algunos países), pero salvó el proyecto. Sin esto, nuestro ranking sería basura — tenías "USA" en top 10 pero "United States" no aparecía.

*Lección:* Los datos limpios no son bonitos — son útiles.

**2. Estimación de costes reales (dejar de soñar)**

*Problema:* Un inmueble "cuesta" 60k€. Pero si tienes 60k€ en el banco, ¿puedes comprarlo?

NO. Porque necesitas:
- Entrada: típicamente 20-30% (12-18k€)
- Gastos de notaría: 1-2% (600-1.200€)
- Impuestos de transferencia: 3-10% (1.800-6.000€)
- Gastos legales: 500-2.000€
- Seguros/garantías: 1-2k€

Total real: el "60k" es realmente 70-80k€.

*Intentamos:* Usar porcentaje fijo global (30% para todo el mundo). Error. Portugal es ~30%, pero Vietnam es ~15%, Suiza es ~35%.

*Solución:* Investigar por país. Usamos referencias de Global Property Guide, bancos españoles, entidades internacionales. Creamos una tabla: "Spain = 30%, Vietnam = 15%, Thailand = 12%". 

Para países sin info, fallback a 30% (conservador).

*Resultado:* entry_price_eur real. Un inversor ve "necesito 22k€, no 20k€" — y eso es la diferencia entre viable e inviable.

**3. Proyección de rentas consistentes (cómo estimar lo desconocido)**

*Problema:* No todos los inmuebles tienen histórico de renta. ¿Cómo estimas? 

*Intentamos:* Usar rentabilidad real del inmueble (si la tenía). Pero 40% de datos faltaban.

*Solución:* Usar yield estándar de mercado (6% anual) ajustado por contexto:
- Un piso de 60k€ en Lisboa genera 3.600€ anuales = 300€/mes
- Pero lo ajustamos: Lisboa zona céntrica renta más que periferia
- También ajustamos por tamaño: T1 renta menos que T3

Resultado: zone_rental_price = estimación DOCUMENTADA. No es magia, es matemáticas aplicadas.

*Limitación honesta:* No es garantía. Es estimación. El mercado cambia.

**4. Decisión: ¿"Top 20" si solo tenemos 13?**

*Problema:* Nuestro objetivo inicial era Top 20 países. Cuando corrimos el análisis, solo 13 cumplían criterios mínimos (precio 30-100k AND rent documentada).

*Tentación:* Relajar criterios. "Bueno, ponemos a países con rent inferior, así llegamos a 20"

*Decisión:* NO. Preferimos ser honestos.

*Consecuencia:* El proyecto se llama "Top 20" pero contamos 13. Parece un fracaso. NO LO ES. Es integridad. Mejor "Top 13 verificables" que "Top 20 inventados".

Esto genera confianza: el usuario sabe que no estamos mentiendo para quedar bien.

*Lección:* Los números honrados valen más que los números inflados.


# Hallazgos principales

# Hallazgos principales (cosas que nos sorprendieron)

**1. Solo 8 países cumplen TODOS los criterios estrictos**

Esperábamos Top 20. Corremos el análisis...

Resultado: 8 países.

¿Qué significa? Que en el mundo, encontramos SOLO 8 lugares donde:
- Precio entrada realista: 30-45k€
- Renta mensual: ≥1.200€
- Marco legal documentado: sí
- Seguridad razonable: sí

Eso es HONESTO. De 147k inmuebles, estos 8 son la crema.

**2. El riesgo legal domina la decisión (aunque matemáticamente sea 18%)**

En la fórmula, seguridad jurídica = 18%. Pero emocionalmente para el inversor = 80% del miedo.

Un piso en Tailandia podría ser perfect matemáticamente (score 82%), pero ¿y si ocupan tu casa y tarda años desalojar porque las leyes son opacas?

Por eso destacamos el score legal en el dashboard (aparece primero, es el mayor). No es por matemáticas, es por realidad psicológica.

**3. La ubicación urbana vale 70% más que playa**

Nuestra fórmula dice: urbano = bueno, playa = excelente.

PERO en datos reales, encontramos que para ALQUILAR (que es lo que quieres hacer), urbano es más consistente. 

- Piso urbano en Lisboa: siempre hay demanda (negocio, turismo, gente viviendo)
- Piso playa en Portugal: excelente en verano (temporada), muerto en invierno

Por eso el score urbano sube. Es sobre consistencia de ingresos mensuales.

**4. Payback típico de nuestro Top 8: 2-4 años**

Comparado con España (8-12 años en ciudades grandes), esto es REVOLUCIONARIO.

¿Qué significa? Que inviertes 30k€, en 3 años recuperas TODO ese dinero en renta. Luego todo lo que entra durante 17 años más es ganancia pura.

Esto es lo que permite reinvertir rápidamente. En España esperas 10 años para recuperar. En nuestro Top 8, esperas 3 años.

La diferencia es: ¿puedes hacer 5 inversiones en 15 años (Top 8) o solo 1 inversión (España)?


# Conclusión

## ¿Qué hemos logrado?

Este proyecto demuestra que es **posible sistematizar decisiones complejas** usando datos, sin perder la humanidad de la decisión.

No es una bola de cristal que te dice "invierte aquí y te harás rico". Es una **herramienta que te muestra la realidad**: estos son los inmuebles, este es su score, estas son las variables. TÚ decides.

Mucho más honesto que cualquier asesor que te diga "créeme".

## El valor real

**Para inversores:**

Antes: investigas Portugal, encuentras 1 piso interesante, luego investigas Tailandia y encuentras otro, luego Vietnam... 6 meses de investigación manual.

Ahora: en 30 segundos ves: "Hey, estos 13 países tienen oportunidades reales". Luego explores los que te interesan.

Impacto: ahorras semanas y tomas decisiones basadas en comparación, no en lo primero que encontraste.

**Para analistas de datos:**

Aprendemos que los datos son bellos, pero limpiarlos es el verdadero trabajo. 

Practicamos scoring multicomponente — técnica que usan bancos (credit scoring), seguros (risk pricing), plataformas (reputación de usuarios).

Es una habilidad que te abre puertas en fintech, seguros, consultoría, AI.

**Para el mercado immobiliario:**

Este proyecto abre la conversación: ¿por qué es España TAN caro comparado con Portugal? ¿por qué no invierten más en mercados como Tailandia?

Muestra que rentabilidad = riesgo. Mayor rentabilidad ≠ automáticamente malo. Es una decisión.

## Limitaciones honestas (esto es importante)

**1. Los datos son un snapshot, no tiempo real**

Cuando corremos el análisis, hacemos una "foto" del mercado. Pero:
- Las propiedades se venden constantemente
- Las leyes de ocupación cambian (una nueva ley en Vietnam cambiaría nuestro scoring)
- Los precios suben/bajan
- El CSV se vuelve obsoleto cada mes

Solución: actualizar datos regularmente. Pero requiere recursos (APIs, código, dedicación).

**2. El score no te dice "compra ya"**

Un score de 85% significa "los datos dicen que esto es bueno".

NO significa "pon tu dinero aquí".

Antes de invertir necesitas:
- Visitar el país
- Hablar con abogados locales
- Ver la propiedad en persona
- Verificar que el inmueble REALMENTE existe (no todas las URLs son confiables)
- Entender impuestos de tu país (la repatriación de ganancias es compleja)

Nuestro score es el primer paso, no la decisión final.

**3. Las predicciones de renta son estimativas, no promesas**

Cuando decimos "este piso rentará 1.200€/mes", usamos:
- 6% de rendimiento anual (referencia de mercado)
- Ajustes por zona y tamaño
- Análisis de competencia local

Pero si baja turismo, sube desempleo, sube oferta de pisos... la renta cae.

Esto NO es culpa nuestra. Es realidad del mercado.

**4. Sesgo hacia documentación en inglés**

Priorizamos países con leyes documentadas EN INGLÉS (o fácilmente traducibles).

Esto favorece países europeos/desarrollados vs. mercados emergentes.

Vietnam, Colombia, Argentina podrían tener igual de buenas oportunidades. Pero sin leyes en inglés bien documentadas, nuestro "score legal" baja.

Es un sesgo del proyecto. Honesto, pero sesgo.

## Posibles mejoras futuras

**Corto plazo (3-6 meses):**
- APIs de actualización automática: conectar con Airbnb/booking para rentas reales
- Políticas migratorias: ¿Cómo de fácil es trabajar/vivir en el país? (afecta demanda)
- Desastres naturales: huracanes, terremotos, inundaciones (que baje valor de propiedad)

**Mediano plazo (6-12 meses):**
- Machine Learning: predictir tendencia de precios ("Valencia está en auge", "Madrid estancado")
- Análisis de tendencias: "¿Qué países son futuro?" vs. "¿Cuáles ya pasaron su momento?"
- Simulador de cartera: "Si invierto 30k en Portugal + 20k en Vietnam, ¿cuál es mi rentabilidad esperada?"

**Largo plazo (1-2 años):**
- Integración con brokers: datos en tiempo real
- Marketplace: conectar inversores con propietarios/gestores
- Sistema de reputación: ¿Cuán confiable es el propietario? ¿Paga en tiempo?

## Reflexión final

La inversión inmobiliaria global NO es para todos. 

Requiere:
- Capital (mínimo 20-30k€)
- Tolerancia al riesgo (monedas extranjeras, mercados inestables)
- Paciencia (los inmuebles no dan dinero rápido)

Pero para quien tiene esos tres ingredientes, este proyecto prueba algo importante: **es posible tomar decisiones inteligentes usando datos**.

En un mundo donde hay 147.000 inmuebles disponibles, nuestro ranking de 13 oportunidades verificables es HONESTO. 

No te decimos "invierte en Tailandia porque está de moda" — te decimos "estos 13 países cumplen TUS criterios financieros específicos Y tienen marcos legales documentados AND tienen rentabilidad realista en un horizonte 2-10 años".

Es más trabajo hacer eso. Pero es también mucho más útil.

**El futuro de la inversión no será sobre tener acceso a más datos — será sobre organizarlos de forma honesta.**


---


# PRESENTACIÓN EN VIVO: Dashboard Streamlit

## ¿Cómo hacemos accesible toda esta complejidad?

Hasta ahora hemos hablado de datos, análisis, scoring. Todo correcto, pero también: aburrido.

**Aquí es donde entra Streamlit.** Es un framework que te permite crear dashboards web en Python sin necesidad de HTML/CSS/JavaScript. Perfecto para científicos de datos que quieren mostrar resultados sin convertirse en desarrolladores web.

Cuando ejecutas `streamlit run streamlit_app.py`, obtienes:
1. Una aplicación web interactiva en `http://localhost:8501`
2. Navegación entre páginas (Página 1: análisis global, Página 2: exploración detallada)
3. Elementos interactivos (filtros, tablas, gráficos que responden al click)
4. Todo actualizado en tiempo real si cambias el CSV

## Página 1: Visión Global (la parte de "wow, mira esto")

### Top: Métricas resumen
Cuando entras, lo primero que ves son 4 números grandes:
- **Paises Top 13**: Cuántos países cumplen criterios
- **Score medio**: Rentabilidad promedio de esos países (te dice si el ranking general es bueno)
- **Precio medio**: EUR promedio de los 13 inmuebles
- **Renta media**: EUR/mes promedio que generarían

Estos 4 números te dan el contexto en 3 segundos: "¿Este análisis vale mi tiempo?"

### Mapa: Donde está el dinero

Luego ves un **mapa interactivo de Plotly** mostrando:
- Todos los países del mundo (grisáceos de fondo)
- Los 13 países Top resaltados en naranja/rojo (según su score)
- Un punto POR CADA INMUEBLE en esos países, tamaño proporcional a la renta, color según score

**Interactividad:**
- Hover sobre un país: ve el país completo iluminado
- Hover sobre un punto (inmueble): ve detalles (ciudad, score, precio, renta)
- Zoom y pan: explora zonas específicas del mundo
- El mapa responde a filtros (si los activas en la barra lateral)

¿Por qué es importante? Porque **ver el mapa despierta la intuición**. No es lo mismo leer "Portugal tiene 3 propiedades" que VER esos 3 puntos alrededor de Lisboa. Tu cerebro comprende información espacial mejor que tablas.

### Gráficos: Patrones y comparaciones

Debajo del mapa hay dos gráficos side-by-side:

**Gráfico 1: Score por país (barras)**
- Eje X: países (Top 13)
- Eje Y: score oportunidad (0-100%)
- Colores: gradient de azul (bajo) a azul oscuro (alto)
- Se puede ordenar haciendo click
- Hover muestra detalles (yield, riesgo, etc.)

Este gráfico te permite **comparar directamente**: "¿Tailandia tiene mejor score que Portugal?" (Respuesta: usualmente sí, porque es más rentable pero con más riesgo legal)

**Gráfico 2: Ubicación - Urbano vs Playa**
- Eje X: países
- Eje Y: porcentaje (0-100%)
- 3 barras por país: urbano (azul), playa (naranja), rural (gris)
- Agrupadas por país para comparar

Este gráfico muestra **por qué recomendamos cada país**. Si ves que "Portugal es 80% urbano", entiendes por qué: mercado rentable estable.

### Tabla: El desglose completo

Al final de Página 1, la **tabla Top 13** con 13 columnas:
- Ranking final
- País
- Ubicación específica
- Precio en EUR
- Entry (capital inicial)
- Renta mensual estimada
- Leyes de ocupación (comentario)
- Leyes de ocupación (URL a fuente)
- Score Legal %
- Score Ubicación %
- Score Oportunidad %
- Payback Years
- URL al inmueble (clickeable)

**¿Qué te muestra?**
- Es verificable: cada inmueble tiene una URL real
- Es completo: tienes todos los números que necesitas
- Es honesto: ves score legal bajo si corresponde (ej: Vietnam ~40%)

**Interactividad:**
- Sorteable: haz click en "Payback Years" para ver cuál recuperas dinero más rápido
- Filtrable: algunos campos se pueden filtrar
- Link directo: haz click en URL para ir al inmueble real (¿existe realmente? Verifica)

## Página 2: Exploración Detallada (la parte de "elige TU inversión")

Página 2 tiene una energía diferente. Aquí el usuario toma control.

### La Ruleta: Scoring 1-10 como circulo

Lo primero que ves es un **gráfico circular (pie chart)** mostrando:
- 13 segmentos (uno por país)
- Tamaño proporcional al score 1-10
- Colores del espectro (rojo = bajo, verde = alto)
- El nombre del país en cada segmento
- Al pasar mouse, ve el score exacto

**¿Por qué es un círculo?**
- Porque es visualmente satisfactorio
- Porque permite "girar mentalmente" y comparar
- Porque es lo opuesto a datos aburridos (es casi un juego)

La ruleta responde a 2 cosas:
1. **Cómo se calcula el score**: 55% seguridad legal + 45% objetivo precio-renta (esto está explicado en caption)
2. **Los valores reales**: Si Portugal sale 7.8/10, es porque esa es su puntuación real

### Nota explicativa (el manual)

Debajo de la ruleta hay una **caption que explica qué es cada componente**:

> "Puntuación 1-10 por país: 55% seguridad (riesgo ocupacion + leyes ocupacion + crime_index + safety_index) + 45% objetivo precio-renta (cercania a 30k EUR & 1.200 EUR/mes)"

Esta nota es CRÍTICA. Sin ella, el usuario ve números mágicos. Con ella, entiende la lógica.

### Búsqueda por país: "Enseñame los detalles"

La sección central permite **buscar un país específico**:
- Dropdown o búsqueda de texto para seleccionar país
- Botones "Anterior" y "Siguiente" para navegar entre países
- Muestra un resumen del país seleccionado:
  - Nombre y flag (bandera) del país
  - Score overall
  - 13 sub-scores desglosados (legal, yield, payback, etc.)
  - Información geográfica (capital, región, moneda)

**¿Por qué esta interactividad?**
- Porque el usuario puede sentirse abrumado por 13 países simultáneamente
- Aquí puede decir: "Quiero saber TODO de Portugal"
- Y ve:
  - Su score legal (65%) - puedes confiar legalmente?
  - Su score rentabilidad (78%) - gana dinero?
  - Su payback (3.2 años) - ¿cuándo recupero mi dinero?
  - Todo en UNA vista, sin tablas confusas

### Tabla Top 8 Estricto: El "oro puro"

Debajo del país seleccionado, ves la **tabla Top 8** (los mejores de los mejores):
- Solo 8 propiedades (vs 13 de la Página 1)
- Todos cumplen: precio 30k-45k EUR Y rent ≥1.200€
- Mismas columnas que Página 1, pero datos más seguros

Esta tabla es tu "lista de compra" — si vas a invertir, empieza aquí.

## Cómo ejecutar

```bash
streamlit run streamlit_app.py
```

Se abre automáticamente en `http://localhost:8501`

**Requisitos:**
- Python 3.8+ 
- Librerías: pandas, streamlit, plotly
- CSV de datos: `streamlit_data/top20_paises_verificables.csv`

**Primeros 5 segundos en el dashboard:**
1. Ves métricas (Score medio: 72%)
2. Ves mapa (Portugal, Tailandia y otros países iluminados)
3. Ves gráficos (Portugal lidera en score urbano)
4. Entiendes: "Hay oportunidades reales en múltiples países"

**Si quieres explorar más:**
1. Clickea Página 2
2. Busca tu país favorito (¿Vietnam?)
3. Ve su score detallado
4. Lee la tabla Top 8
5. Haz click en URLs para verificar propiedades reales

## Lo que hace ESPECIAL este dashboard

**1. Equilibrio entre automatización e información**
- Podríamos mostrar todos los 147k inmuebles
- Pero elegimos mostrar solo lo relevante (Top 13/8)
- Decisión consciente: calidad > cantidad

**2. Transparencia**
- Todas las URLs son clickeables y verificables
- Ves qué score tiene cada inmueble (no es mágico)
- Ves cómo se calcula el score (la fórmula está en caption)

**3. Intuición visual**
- El mapa muestra geografía (donde está el dinero)
- La ruleta muestra comparación (Portugal vs Tailandia a golpe de vista)
- Los gráficos muestran patrones (urbano > rural)

**4. Exploración sin abrumar**
- Página 1: vista global (40 segundos)
- Página 2: zoom a un país (2-3 minutos)
- Si quieres más detalle: abre la URL real

## El punto de vista del usuario final

Cuando un inversor abre este dashboard, vive 3 emociones:

**Primero:** "¡Wow, es bonito y entiendo todo en 30 segundos!"

**Segundo:** "Espera, ¿Portugal tiene 7.2 de score? Pensaba que era mejor... veo que es por el riesgo legal (score 65%)"

**Tercero:** "Entiendo. Este sistema no me dice 'invierte', me dice 'estos son los datos, TÚ decides'"

Eso es lo que queremos lograr. No vender. Informar.