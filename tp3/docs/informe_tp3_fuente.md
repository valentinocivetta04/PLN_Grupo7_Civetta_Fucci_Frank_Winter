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

## 1. Detectores de la auditoría y costo de un falso positivo

Medimos cada detector sobre la parte de prueba de la muestra etiquetada (150 libros, 30 contaminados), separada por libro con `random_state=42`. Los umbrales y patrones salieron siempre de la parte de desarrollo.

| Detector | Qué contaminación encuentra | Precisión | Recall |
|------------------------|----------------------------------------------------------|----------:|-------:|
| Expresión regular | Enlaces explícitos, correos y teléfonos | 1,00 | 0,23 |
| Normalización + dominios | Enlaces disimulados: letras separadas, `[.]`, cirílico, invisibles | 1,00 | 0,63 |
| Idioma por oración | Mensajes en inglés o portugués dentro de la sinopsis | 0,62 | 0,33 |
| Clasificador TF-IDF | Publicidad con palabras que se repiten | 1,00 | 0,93 |
| Clasificador con embeddings | Publicidad dicha con otras palabras | 0,90 | 0,87 |
| Copias (vecino más cercano) | Libros inventados que copian otra sinopsis | 1,00 | 0,10 |
| **Combinación (al menos uno)** | | **0,79** | **1,00** |

Mirando los motivos de cada libro contaminado de prueba, la regex encontró los 4 enlaces explícitos, la normalización 12 de los 14 enlaces disimulados y el detector de idioma los 5 mensajes en otro idioma. La publicidad en español sin enlace (7 libros) solo la encontraron los clasificadores. El idioma de la sinopsis completa no sirvió: langdetect dijo `es` para los 350 libros de desarrollo. El NER con spaCy lo usamos para explicar y no para detectar: en el texto insertado predominan las MISC («Download this ebook for FREE», «EPUB sin registro») y confunde imperativos con personas («compartila», «Ganá»).

Un falso positivo es un libro legítimo que sale del catálogo y nunca se va a poder recomendar. La combinación tuvo 8 en prueba, y 6 vinieron del detector de idioma. En el catálogo completo marcamos 703 libros (8,2 %) y quedaron 7.890. Es más de lo esperable, porque la muestra está enriquecida al 20 % y el catálogo tiene bastante menos contaminación. El idioma marcó 261 libros, 172 sin que coincidiera ningún otro detector, muchos de ellos antologías y revistas de ciencia ficción. Si lo repitiéramos, exigiríamos que el idioma coincida con otro detector antes de sacar un libro.

## 2. La etiqueta `interes` y quién valoró

`interes` vale 1 si al lector le interesaría leer el libro después de ver su título y su sinopsis, y 0 si no. Es una intención declarada a partir de un texto corto: no dice si el libro es bueno ni si lo leyó. Todas las valoraciones las hizo Valentino Civetta, en varias tandas y antes de ver predicciones, recorriendo el catálogo limpio en el orden de `df.sample(frac=1, random_state=42)`. Vio 101 libros: 46 con 1, 54 con 0 y uno sin valorar porque no pudo decidir. No encontró contaminados que se le hubieran escapado al paso 2. Con `train_test_split` estratificado quedaron 80 libros de entrenamiento (37 positivos) y 20 de prueba (9 positivos).

## 3. TF-IDF contra embeddings

| Tarea y medida | TF-IDF | Embeddings |
|------------------------------------------------------------|---------------:|---------------:|
| Auditoría, prueba (precisión / recall) | 1,00 / 0,93 | 0,90 / 0,87 |
| Auditoría, desarrollo con precisión 0,90 (recall) | 0,91 | 0,93 |
| Preferencias, prueba (F1 de la clase 1) | 0,35 | 0,52 |
| Preferencias, validación cruzada 5×10 (F1, media ± desvío) | 0,42 ± 0,19 | 0,53 ± 0,16 |
| Preferencias, precision@5 | 0,20 | 0,80 |

En la auditoría quedaron casi empatados y TF-IDF fue apenas mejor en prueba. Ahí había 2.095 oraciones de entrenamiento y publicidad que repite palabras exactas («Visitá», «gratis», `.example`), justo lo que TF-IDF capta. Clasificamos oraciones porque el mensaje insertado mide unos 81 caracteres contra unos 970 de una sinopsis, y en el vector de la sinopsis entera queda diluido. Para los mensajes nuevos del catálogo, con el mismo sentido y otras palabras, esperamos que generalicen mejor los embeddings, que son multilingües.

La diferencia fue mayor en las preferencias. Con 80 sinopsis, TF-IDF arma un vocabulario de 4.008 palabras con muy pocos ejemplos de cada una y termina dándoles peso a palabras vacías («su», «para», «de»). Los embeddings traen el significado aprendido de antes, y para captar un gusto por temas (ciencia, guerra, historia) eso sirve más que las palabras exactas.

## 4. ¿Algún clasificador mejoró a la similitud?

Sí, el de embeddings. Sobre los mismos 20 libros de prueba, sus 5 primeros tuvieron 4 libros de interés (precision@5 de 0,80), mientras que el clasificador con TF-IDF y la similitud con el perfil del lector acertaron 1 de 5 (0,20). Elegir al azar da 0,45 en promedio. Igual hay que tomarlo con cuidado: si se eligen 5 libros al azar entre esos 20, la probabilidad de acertar 4 o más es de casi 10 %. Lo que lo hace más creíble es que en la validación cruzada embeddings también rindió mejor. Creemos que el perfil anduvo mal porque es el promedio de 37 libros muy variados y queda en un punto medio que no se parece a ninguno. El clasificador, en cambio, también aprende de los libros que no le interesaron.

## 5. Un error y los límites del experimento

*La promesa del barón*, una novela romántica de época que el lector valoró con 0, fue un falso positivo de los dos modelos, con probabilidades de 0,53 y 0,50. Las palabras que más empujaron al modelo TF-IDF fueron «su», «desde», «para», «familia» y «de»: palabras vacías que aparecen en cualquier sinopsis. En el catálogo completo el clasificador recomendó cinco libros de intriga, espionaje y Segunda Guerra, y el lector aceptó dos (*Hitler y las teorías de la conspiración* y *El espía de Madrid. Barcelona, 1936*). Le interesaron los de fondo histórico real y no los policiales de ficción, una diferencia que el modelo no hace. El resumen extractivo también falló en un caso: en *El hombre en la red* se perdió la oración que dice que las sospechas recaen sobre el protagonista.

El límite principal es el tamaño: un solo lector, 100 valoraciones y 20 libros de prueba, donde un libro cambia 0,05 la exactitud y más todavía la precisión o el recall. Un modelo que respondiera que sí a todo tendría F1 de 0,62 en prueba, más que los nuestros, así que el F1 solo no alcanza para decir que los clasificadores aprendieron. Además SBERT lee solo los primeros 128 tokens de cada sinopsis, la muestra etiquetada no tiene todas las variantes de contaminación y una puntuación alta es una estimación, no una garantía de que el libro le guste.

## 6. Uso de asistentes de IA

Usamos Claude (Anthropic) para comprender conceptos, programar y revisar errores del notebook, y como apoyo en la redacción. Las valoraciones de `interes` son del lector y los resultados los discutimos en el grupo.
