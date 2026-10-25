# TP2 de PLN: resumen de lo que hicimos

Grupo 7: Civetta, Frank, Fucci y Winter. Octubre de 2026.

Este resumen cuenta qué se hizo en el TP2 durante las sesiones de trabajo con Claude: primero Valentino desde su Mac y después Federico desde su PC. La idea es que todos sepamos en qué estado quedó el TP, dónde está cada cosa y qué falta. Para entender los conceptos a fondo está la guía de estudio (`docs/guia_estudio_tp2.pdf`, ver más abajo).

## Estado actual

El TP está completo y subido al repo. Tiene las partes A a F de la consigna, la evaluación (Parte 5) y una parte avanzada (Parte 6, RAG). El notebook está ejecutado de punta a punta, sin errores y con todas las salidas.

| Entregable de la consigna | Dónde está | Estado |
|---|---|---|
| Notebook ejecutado con salidas | `src/TP2_Civetta_Frank_Fucci_Winter.ipynb` | Listo |
| Conjunto de evaluación | `queries.json` | Listo (12 consultas) |
| Informe (máx. 3 páginas) | `informe.pdf` | Listo (carátula + 3 páginas) |
| Base poblada en Supabase | Proyecto de Valentino | Lista (2 tablas con índice HNSW) |

## Qué hicimos, parte por parte

**Partes A a D (corpus y modelos).** Usamos las 150 sinopsis del TP1 en dos versiones: una cruda para SBERT y una limpia (minúsculas, sin puntuación ni stopwords) para Word2Vec y TF-IDF. Entrenamos un Word2Vec propio (Skip-gram, 100 dimensiones) y lo comparamos con SBW, que viene pre-entrenado (300 dimensiones). También generamos embeddings con SBERT (`distiluse-base-multilingual-cased-v1`, 512 dimensiones). SBERT lee como máximo 128 tokens, y 134 de las 150 sinopsis son más largas, así que se cortan. Después comparamos los tres modelos con rankings, con la similitud entre pares de libros al azar y con una proyección PCA.

Al Word2Vec propio le fijamos una semilla porque daba resultados distintos en cada corrida. Igual no aprendió casi nada: dos libros cualquiera tienen similitud 0,999, porque 150 sinopsis es muy poco texto.

**Partes E y F (base de datos).** La base es un proyecto de Supabase de Valentino, con la extensión pgvector y un usuario de conexión propio para el TP. Hay dos tablas, `embeddings_word2vec_propio` (100 dimensiones) y `embeddings_sbert` (512 dimensiones). Los vectores están normalizados y no quedó ninguno nulo. Cada tabla tiene un índice HNSW con `vector_cosine_ops`. La función `buscar()` resuelve la búsqueda en SQL y permite filtrar por género. En el notebook también explicamos qué pasa con el recall cuando se combina el índice con un filtro.

**Parte 5 (evaluación).** Escribimos 12 consultas antes de correr los modelos: 3 léxicas, 5 semánticas y 4 que no comparten ninguna palabra con los libros relevantes. Medimos precision@5, precision@10 y R-precision. Comparamos contra TF-IDF y contra el azar, que calculamos de dos formas: el valor esperado y una simulación de 10.000 corridas.

| Método | P@5 | P@10 | R-precision |
|---|---|---|---|
| Azar (esperado) | 0,025 | 0,025 | 0,025 |
| TF-IDF | 0,283 | 0,217 | 0,357 |
| Word2Vec propio | 0,167 | 0,125 | 0,159 |
| SBW | 0,267 | 0,208 | 0,286 |
| SBERT | 0,350 | 0,258 | 0,466 |

Esto es lo que sacamos de los resultados:

- SBERT es el mejor en promedio y en los tres tipos de consulta.
- Comparado consulta por consulta con TF-IDF, SBERT gana 5, empata 5 y pierde 2. El test de signos da p ≈ 0,45, así que con 12 consultas no podemos decir que la diferencia sea real.
- En las consultas sin palabras en común, TF-IDF saca 0 y SBERT 0,24.
- Todos los métodos superan el percentil 95 del azar (0,067).
- Verificamos que la búsqueda en SQL da lo mismo que el cálculo en numpy. La única diferencia es un empate entre las dos ediciones de *Las mil y una noches*, que tienen el mismo vector.
- El caso de falla es la consulta del gobernante atormentado (*Macbeth*, *El rey Lear*). Comprobamos que las frases que hacen relevantes a esos libros aparecen después del token 128, o sea que SBERT nunca las leyó.

**Parte 6 (RAG).** Para cada pregunta recuperamos 4 libros con SBERT y se los pasamos a un modelo de la API de NVIDIA NIM. Comparamos un prompt ingenuo con uno estricto, que exige citar cada dato y abstenerse si no hay información. Lo probamos con 9 preguntas y revisamos a mano las 18 respuestas.

- NVIDIA retiró todos los modelos Llama mientras hacíamos el TP. Por eso el código elige solo un modelo disponible; esta vez usó `google/gemma-4-31b-it`.
- No hubo alucinaciones. Todas las fallas vinieron de la recuperación: por ejemplo, *Morfina* quedó en el puesto 12 porque la palabra "morfina" aparece en el token 289.

## Cambios de organización y documentación

- El notebook se renombró a `TP2_Civetta_Frank_Fucci_Winter.ipynb`, como pide la consigna (`TP2_apellido1_apellido2.ipynb`). Reescribimos todos los textos en lenguaje simple, cada parte tiene su título (PARTE A … PARTE 6) y el código tiene comentarios cortos cada vez que aparece algo nuevo.
- El informe tiene una carátula con el logo de la FCEIA, los integrantes y los docentes, y después 3 páginas que responden las 4 preguntas obligatorias de la consigna. Su fuente editable está en `docs/informe_fuente.md`, junto con el logo.
- Reescribimos el README: ahora explica los dos TPs, la estructura, la instalación, cómo armar el `.env` (también en Colab), cómo correr cada cosa y los resultados.
- En `requirements.txt` agregamos `scipy`, `requests` e `ipykernel`.
- En `.gitignore` agregamos la guía de estudio, que es de uso interno y no se entrega.

Así quedó el repo:

```
README.md, requirements.txt, .env.example, .gitignore
queries.json, informe.pdf
data/libros.csv
src/scraper.py, src/TP2_Civetta_Frank_Fucci_Winter.ipynb
docs/TP-1.pdf, docs/TP-2.pdf, docs/diseno_extraccion.md, docs/informe_fuente.md, docs/logo_fceia.png
```

## Cómo correr el notebook en tu computadora

1. Hacé `git pull` e instalá las dependencias con `pip install -r requirements.txt`, dentro de un entorno virtual.
2. Copiá `.env.example` como `.env` en la raíz del repo y completá los dos datos:
   - `SUPABASE_DB_URL`: reemplazá `<PEDIR_AL_GRUPO>` por la contraseña de la base, que se pasa por privado y nunca por git.
   - `NVIDIA_API_KEY`: una clave personal de build.nvidia.com. Solo hace falta para la Parte 6.
3. Abrí el notebook desde la carpeta `src/` y ejecutá todo. La primera vez descarga SBW (1,1 GB) y SBERT; después la corrida completa tarda unos 10 a 20 minutos, sobre todo por el RAG.

El `.env` nunca se sube: git lo ignora. `.env.example` es solo la plantilla que muestra qué variables hacen falta.

## Material para estudiar

`docs/guia_estudio_tp2.pdf` es una guía de 13 páginas que explica desde cero todo el TP: de dónde venimos con el TP1, qué es un embedding, Word2Vec, SBERT, pgvector y HNSW, las métricas, el test de signos y el RAG. Al final tiene un glosario y una lista de preguntas que nos pueden hacer en la defensa, con respuestas cortas. Git la ignora, así que no viene con el pull: Federico la tiene que pasar por otro medio.

## Pendientes

- Revocar la clave de NVIDIA que se usó durante la sesión, porque quedó escrita en el chat. Cada uno puede sacar la suya.
- Cambiar la contraseña de la base de Supabase, porque también circuló por el chat (lo hace Valentino), y pasar la nueva por privado.
- Confirmar con los docentes que la carátula no cuenta en el límite de 3 páginas del informe.
- Que cada uno lea la guía y el informe antes de la defensa. Ojo: en el informe declaramos que usamos Claude como asistente.
