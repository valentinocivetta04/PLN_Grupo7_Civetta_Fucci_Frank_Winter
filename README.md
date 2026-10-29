# PLN · TP1, TP2 y TP3 · Grupo 7

Procesamiento del Lenguaje Natural, Tecnicatura Universitaria en Inteligencia Artificial (FCEIA, UNR). Comisión 2.

## Integrantes

| Integrante | Legajo |
|---|---|
| Civetta, Valentino | 45948755 |
| Frank, Maximiliano | 38726401 |
| Fucci, Milagros | 47076861 |
| Winter, Federico | 44101265 |

Docentes: Geary, Alan y Manson, Juan Pablo.

Cada trabajo práctico está en su propia carpeta (`tp1/`, `tp2/` y `tp3/`), con su código, sus datos, su consigna y su entrega. En la raíz quedan solo las dependencias, la plantilla de credenciales y este README.

## Estructura del repositorio

```
README.md                 este archivo
requirements.txt          dependencias de Python de los tres TPs
.env.example              plantilla de credenciales del TP2 (el .env real no se sube)
.gitignore
tp1/                      TP1: corpus propio con scraping
  scraper.py              scraper de Lectulandia
  data/libros.csv         corpus de 150 libros
  docs/TP-1.pdf           consigna
  docs/diseno_extraccion.md   diseño de la extracción (Parte 1 de la consigna)
tp2/                      TP2: embeddings y búsqueda semántica
  TP2_Civetta_Frank_Fucci_Winter.ipynb   notebook ejecutado, con salidas
  queries.json            conjunto de evaluación (12 consultas con sus libros relevantes)
  informe_tp2.pdf         informe (carátula + 3 páginas)
  docs/TP-2.pdf           consigna
tp3/                      TP3: recomendador personalizado de libros
  TP3_Civetta_Frank_Fucci_Winter.ipynb   notebook ejecutado (pasos 1 a 8 y conclusiones)
  grupo7_sospechosos.csv  libros marcados en la auditoría (slug y motivo)
  grupo7_preferencias.csv valoraciones del lector, con la columna conjunto
  informe_tp3.pdf         informe (carátula + 2 páginas)
  data/
    catalogo_tp3.jsonl    catálogo de la cátedra, 8747 libros (algunos contaminados)
    muestra_etiquetada.csv   500 libros con la columna contaminado (también en .xlsx)
    catalogo_limpio.csv   catálogo sin los sospechosos (lo genera el paso 2.7)
    ejemplo_sospechosos.csv, ejemplo_preferencias.csv   formato de los archivos de entrega (también en .xlsx)
  docs/TP-3.pdf           consigna
```

Hay archivos que existen en cada máquina pero no se suben (están en `.gitignore`): `.env`, el modelo SBW (`tp2/data/SBW-vectors-300-min5.bin.gz`, 1,1 GB, el notebook lo descarga solo si falta), el entorno virtual y la guía de estudio interna `tp2/docs/guia_estudio_tp2.pdf`.

## Instalación

```bash
git clone <URL_DEL_REPO>
cd <carpeta_del_repo>
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium      # solo hace falta para correr el scraper del TP1
python -m spacy download es_core_news_lg   # solo hace falta para el TP3 (NER y frases sustantivas)
```

## Credenciales: `.env` y `.env.example`

El notebook del TP2 necesita dos datos secretos: la URL de conexión a la base de Supabase (con su contraseña) y una clave de la API de NVIDIA NIM. Esos datos van en un archivo `.env` en la raíz del repo, que git ignora, así que nunca terminan en GitHub.

`.env.example` es la plantilla que sí se sube. Muestra qué variables hacen falta, con valores de ejemplo, para que cualquiera pueda armar su `.env`:

1. Copiar la plantilla: `cp .env.example .env` (en Windows: `copy .env.example .env`).
2. En `SUPABASE_DB_URL`, reemplazar `<PEDIR_AL_GRUPO>` por la contraseña, que se comparte por privado dentro del grupo.
3. En `NVIDIA_API_KEY`, poner una clave personal de [build.nvidia.com](https://build.nvidia.com). Solo hace falta para la parte avanzada (RAG).

El notebook del TP2 lee esas variables con `load_dotenv()`. El TP3 no usa credenciales.

**En Google Colab** no hay `.env`. Cargar `SUPABASE_DB_URL` y `NVIDIA_API_KEY` en los *Secrets* de Colab (el ícono de la llave) y ejecutar esto antes de la Parte E:

```python
import os
from google.colab import userdata
for nombre in ["SUPABASE_DB_URL", "NVIDIA_API_KEY"]:
    os.environ[nombre] = userdata.get(nombre)
```

`load_dotenv()` no pisa una variable que ya está definida, así que el notebook funciona igual en los dos casos.

## TP1 · Corpus de Lectulandia

En el **TP1** armamos un corpus propio: 150 libros de la categoría "Clásico" de [Lectulandia](https://ww3.lectulandia.co/genero/clasico/), con sus metadatos y sinopsis, extraídos con Playwright y BeautifulSoup.

**Cómo correrlo:** `python tp1/scraper.py`. Corre sin abrir ventana, espera 2 segundos entre fichas, guarda cada libro apenas lo procesa y reescribe `tp1/data/libros.csv` en cada ejecución, desde cualquier carpeta en la que se lo llame. La categoría, la URL y la cantidad de libros se cambian en las constantes del principio del archivo (`CATEGORIA`, `URL_CATEGORIA`, `LIBROS_OBJETIVO`).

### Dificultades que encontramos

- **La sinopsis no tiene siempre la misma estructura.** En algunas fichas el texto está dentro de un `<p class="description">` y en otras va directo en el `<div id="sinopsis">`. Lo resolvimos con el selector `#sinopsis`, que cubre los dos casos (ver `tp1/docs/diseno_extraccion.md`, sección 3).
- **El número de libro dentro de una serie no tiene etiqueta propia.** Aparece mezclado con el nombre de la serie ("Libro 9 de: ..."), así que lo sacamos con una expresión regular sobre el `<span class="tagTitle">`.
- **Las corridas se acumulaban.** La primera versión agregaba los libros al final del CSV existente, y cada ejecución sumaba datos de la anterior. Ahora el script borra el CSV al empezar.

### Campos de `tp1/data/libros.csv`

| Campo | Descripción | Tipo |
|---|---|---|
| titulo | Título del libro | texto |
| autores | Lista de autores | texto |
| generos | Lista de géneros | texto |
| serie | Serie a la que pertenece, o "N/A" | texto |
| numero_serie | Número dentro de la serie, o "N/A" | texto |
| sinopsis | Sinopsis completa | texto |
| url_libro | URL de la ficha (identifica a cada libro) | texto |
| categoria_origen | Categoría del scraping | texto |
| fecha_extraccion | Fecha y hora de extracción | fecha y hora |

## TP2 · Embeddings y búsqueda semántica

En el **TP2** convertimos esas sinopsis en vectores con tres modelos (un Word2Vec entrenado por nosotros, el Word2Vec pre-entrenado SBW y el modelo de oración SBERT), los guardamos en Supabase con pgvector, armamos un buscador semántico en SQL y lo evaluamos contra TF-IDF y contra el azar con 12 consultas propias. Como parte avanzada hicimos un RAG con la API de NVIDIA NIM.

**Cómo correrlo:** abrir `tp2/TP2_Civetta_Frank_Fucci_Winter.ipynb` desde la carpeta `tp2/` y ejecutar todas las celdas en orden, con el `.env` armado. Lee el corpus de `tp1/data/libros.csv` y las consultas de `tp2/queries.json`. La primera vez descarga SBW (1,1 GB) en `tp2/data/` y el modelo SBERT, así que tarda bastante; después la corrida completa lleva unos 10 minutos.

### Resultados

| Método | P@5 | P@10 | R-precision |
|---|---|---|---|
| Azar (esperado) | 0,025 | 0,025 | 0,025 |
| TF-IDF | 0,283 | 0,217 | 0,357 |
| Word2Vec propio | 0,167 | 0,125 | 0,159 |
| SBW | 0,267 | 0,208 | 0,286 |
| SBERT | 0,350 | 0,258 | 0,466 |

SBERT es el mejor en promedio y en los tres tipos de consulta, aunque con 12 consultas la diferencia con TF-IDF no es estadísticamente concluyente. El análisis completo, el caso de falla y el RAG están en `tp2/informe_tp2.pdf` y en el notebook.

## TP3 · Recomendador personalizado de libros

En el **TP3** armamos un recomendador personalizado de libros. Partimos de un catálogo de 8747 libros que la cátedra contaminó a propósito: enlaces, mensajes promocionales y libros inventados. Primero lo auditamos con varios detectores (expresiones regulares, normalización de Unicode, detección de idioma, NER, clasificadores de oraciones con TF-IDF y con embeddings, y vecinos más cercanos para encontrar copias). Después, con las preferencias de una persona del grupo, entrenamos clasificadores que ordenan los libros que todavía no leyó.

**Cómo correrlo:** abrir `tp3/TP3_Civetta_Frank_Fucci_Winter.ipynb` desde la carpeta `tp3/` y correr las celdas en orden. Lee los datos de `tp3/data/` y guarda los dos CSV de entrega en `tp3/`. El paso 3 lo corre solo el lector: muestra un libro por vez, guarda cada respuesta en el momento y se puede cortar y retomar. Como `grupo7_preferencias.csv` ya está completo, si se vuelve a correr no pregunta nada. Nosotros lo ejecutamos en Google Colab con GPU; ahí hay que descomentar la celda de instalación y poner `RUTA` y `ENTREGA` en `/content/` (o la carpeta donde se suban los archivos). El paso 2.7 codifica decenas de miles de oraciones con SBERT: con GPU tarda unos minutos y con CPU bastante más.

### Resultados

En el paso 1 quedaron 8593 libros del catálogo original.

| Motivo | Libros eliminados |
|---|---|
| Sin sinopsis | 1 |
| Sinopsis repetida (cursos y series completas) | 98 |
| Casi duplicado (mismo autor, título parecido, mismo tomo, sinopsis casi igual) | 55 |

En la auditoría (paso 2) medimos cada detector sobre la parte de prueba de la muestra etiquetada (150 libros, 30 contaminados):

| Detector | Precisión | Recall |
|---|---|---|
| Expresión regular | 1,00 | 0,23 |
| Normalización + dominios | 1,00 | 0,63 |
| Idioma por oración | 0,62 | 0,33 |
| Clasificador de oraciones TF-IDF | 1,00 | 0,93 |
| Clasificador de oraciones con embeddings | 0,90 | 0,87 |
| Copias (vecino más cercano) | 1,00 | 0,10 |
| Combinación (al menos uno) | 0,79 | 1,00 |

En el catálogo completo marcamos 703 libros (8,2 %) y quedaron 7890 en `catalogo_limpio.csv`. El detector de idioma es el que más falsos positivos suma.

El lector fue Valentino Civetta: valoró 101 libros (46 le interesaron, 54 no y uno quedó sin decidir). Con 80 libros para entrenar y 20 para probar:

| Lista de recomendación | F1 clase 1 (prueba) | F1 validación cruzada | precision@5 |
|---|---|---|---|
| TF-IDF + regresión logística | 0,35 | 0,42 ± 0,19 | 0,20 |
| Embeddings + regresión logística | 0,52 | 0,53 ± 0,16 | 0,80 |
| Similitud con el perfil del lector | | | 0,20 |
| Azar | | | 0,45 |

El clasificador con embeddings fue el único que recomendó mejor que el azar, aunque con 20 libros de prueba parte de esa diferencia puede ser suerte. En el catálogo completo recomendó cinco libros de intriga, espionaje y Segunda Guerra, y al lector le interesaron dos. El análisis completo está en el notebook y en `tp3/informe_tp3.pdf`.
