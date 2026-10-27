---
lang: es
geometry: "a4paper, margin=1.8cm"
fontsize: 10pt
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
header-includes:
  - \usepackage{graphicx}
  - \usepackage{xcolor}
  - \usepackage{titling}
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyfoot[C]{\small\thepage}
  - \fancyhead[L]{\small\sffamily\color{gray}TP3 · Recomendador personalizado de libros}
  - \fancyhead[R]{\small\sffamily\color{gray}Grupo 7}
  - \renewcommand{\headrulewidth}{0pt}
---

```{=latex}
\begin{titlepage}
\thispagestyle{empty}
\centering\sffamily
\vspace*{1cm}
\includegraphics[width=0.42\textwidth]{logo_fceia.png}\par
\vspace{1.2cm}
{\large Facultad de Ciencias Exactas, Ingeniería y Agrimensura\par}
\vspace{0.2cm}
{\large Universidad Nacional de Rosario\par}
\vspace{0.6cm}
{\Large Tecnicatura Universitaria en Inteligencia Artificial\par}
\vspace{2.2cm}
{\huge\bfseries Procesamiento del Lenguaje Natural\par}
\vspace{0.6cm}
{\LARGE\color{gray} Trabajo Práctico N.º 3\par}
\vspace{0.2cm}
{\Large\color{gray} Recomendador personalizado de libros\par}
\vfill
{\large\bfseries Grupo 7\par}
\vspace{0.4cm}
\begin{tabular}{ll}
Civetta, Valentino & Legajo 45948755 \\
Frank, Maximiliano & Legajo 38726401 \\
Fucci, Milagros & Legajo 47076861 \\
Winter, Federico & Legajo 44101265 \\
\end{tabular}\par
\vspace{1cm}
{Docentes: Geary, Alan y Manson, Juan Pablo\par}
\vspace{0.3cm}
{Octubre de 2026\par}
\vspace*{0.5cm}
\end{titlepage}
\setcounter{page}{1}
```

## 1. Auditoría del catálogo: detectores y costo de un falso positivo

*[COMPLETAR con la tabla del paso 2.7, calculada sobre la parte de prueba de la muestra: precisión y recall de cada detector y de la combinación.]*

Usamos cinco detectores. La **expresión regular** (URLs, correos y teléfonos) encuentra los enlaces escritos de forma explícita. La **normalización** (palabras en lugar de signos, letras separadas, `[.]`, letras de otro alfabeto, caracteres invisibles) recupera los enlaces disimulados y se acompaña de una regex de dominios sin `http`. La **detección de idioma por oración** encuentra mensajes en otro idioma dentro de una sinopsis en español, con un mínimo de *[N]* palabras y una probabilidad de *[P]* elegidos sobre la muestra de desarrollo. Los **clasificadores de oraciones** (TF-IDF y embeddings, con umbral para precisión 0,90) encuentran el texto promocional sin enlaces. Los **vecinos más cercanos** (coseno sobre TF-IDF, autores distintos, una sinopsis que contiene a la otra) encuentran libros que copian una sinopsis ajena. El NER con spaCy *[COMPLETAR: ¿detectó o solo explicó?]*.

Un falso positivo es un libro legítimo que sale del catálogo y que el recomendador ya no puede ofrecer nunca. Por eso combinamos los detectores con una unión ("al menos uno lo marca") y miramos la precisión de la unión, no solo su recall. *[COMPLETAR: cuántos falsos positivos dejó la combinación y cuáles fueron, por ejemplo sinopsis que mencionan sitios reales.]*

## 2. Qué representa la etiqueta `interes` y quién la dio

`interes` vale 1 si a la persona le interesaría leer el libro después de ver su título y su sinopsis, y 0 si no. No mide si el libro es bueno ni si lo leyó: es una intención declarada a partir de un texto corto. Las valoraciones las dio *[COMPLETAR: nombre del lector]*, una sola persona, en casa y antes de ver ninguna predicción, recorriendo el catálogo limpio en el orden de `df.sample(frac=1, random_state=42)`. Quedaron *[N]* respuestas válidas (*[N1]* con 1 y *[N0]* con 0), *[N]* abstenciones y *[N]* libros marcados como contaminados por revisión manual.

## 3. TF-IDF contra embeddings

*[COMPLETAR con las dos tablas: detección de contaminación (paso 2.5) y clasificación de preferencias (paso 6).]*

En la **detección** esperamos que TF-IDF gane con cadenas literales (una URL, una palabra de oferta que se repite) y que los embeddings generalicen mejor a frases nuevas con el mismo sentido, como las que hay en el catálogo y no en la muestra. *[COMPLETAR con lo que mostraron los números: recall a igual precisión y por tipo de contaminación.]* En la **clasificación de preferencias** tenemos *[N]* libros de entrenamiento y *[N]* de prueba; la media y el desvío del F1 de la clase 1 en la validación cruzada fueron *[X ± Y]* con TF-IDF y *[X ± Y]* con embeddings. *[COMPLETAR: en qué tarea fue mayor la diferencia y por qué. Pistas: en la auditoría hay cientos de oraciones por clase y el texto insertado es corto y repetitivo; en las preferencias hay unas pocas decenas de libros y la señal es el tema, no una cadena de texto.]*

## 4. ¿Mejoró algún clasificador a la similitud?

| Lista (mismos libros de prueba) | Aciertos en los 5 primeros | precision@5 |
|---|---|---|
| TF-IDF + clasificador | *[N]* | *[X]* |
| Embeddings + clasificador | *[N]* | *[X]* |
| Similitud con el perfil | *[N]* | *[X]* |
| Azar (proporción de 1 en prueba) | | *[X]* |

*[COMPLETAR: responder sí o no con estos números. Con cinco libros por lista, un acierto de diferencia mueve 0,20, y con 20 libros de prueba esa diferencia puede ser puro azar; decirlo.]*

## 5. Error encontrado y límites del experimento

*[COMPLETAR: un error concreto del paso 6 (falso positivo o falso negativo) con el título del libro, la probabilidad que dio cada modelo y por qué creemos que pasó. Opcional: un libro contaminado que el lector encontró y los detectores no.]*

Los límites que ya conocemos: el lector es una sola persona y sus 100 respuestas son una muestra chica, así que las métricas de prueba (20 libros) son orientativas; la muestra etiquetada tiene 20 % de contaminados y el catálogo mucho menos, de modo que la precisión que medimos es más optimista que la real; la muestra no incluye todas las variantes de contaminación; SBERT lee como máximo 128 tokens y corta las sinopsis largas; y una puntuación alta es una estimación del modelo, no garantía de que el libro le guste después de leerlo.

## 6. Uso de asistentes de IA

Usamos Claude (Anthropic) como asistente durante el trabajo: para entender los pasos de la consigna, escribir y depurar el código del notebook y redactar los textos y una primera versión de este informe. Las valoraciones de `interes` son exclusivamente las del lector elegido, y la interpretación de los resultados la discutimos en el grupo. Somos responsables de todo lo que entregamos.
