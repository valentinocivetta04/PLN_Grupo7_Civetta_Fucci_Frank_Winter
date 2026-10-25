# TP3: qué planteamos y qué resolvimos en la sesión

Procesamiento del Lenguaje Natural, TUIA (FCEIA, UNR). Grupo 7. Sesión del 25/10/2026.

Este resumen cubre el planteo del TP3 "Recomendador personalizado de libros", el notebook que se armó hasta el paso 3 y lo que queda por hacer.

## Qué pide el TP3

El catálogo de 8747 libros que entrega la cátedra está contaminado a propósito: hay sinopsis con enlaces, mensajes promocionales y libros inventados que copian la sinopsis de otro. Si no se detectan, el recomendador termina sugiriendo spam. Por eso el trabajo tiene dos partes. Primero se audita el catálogo con varios detectores. Después se registran las preferencias de una persona del grupo y se entrenan clasificadores que ordenan los libros que todavía no valoró.

Son ocho pasos, con los mismos títulos en el notebook: cargar y revisar, auditar, registrar preferencias, separar entrenamiento y prueba, entrenar dos clasificadores (TF-IDF y embeddings), comprobar las predicciones, convertirlas en recomendaciones y recomendar del catálogo completo con resumen y perfil del lector. Los entregables son el notebook ejecutado, `sospechosos.csv`, `preferencias.csv` y un informe de hasta tres páginas con cinco preguntas.

## El plan: qué herramienta en cada paso

Se partió del enunciado, de la lista "Herramientas NLP Python" que pasó la cátedra y de lo que ya teníamos en el repo (`scraper.py` y el notebook de embeddings del TP2). El catálogo viene dado, así que este TP no necesita extracción nueva. Del scraper se tomó solo la idea de guardar cada registro apenas se procesa, que se usó en el paso 3.

| Paso | Qué se hace | Herramienta |
|---|---|---|
| 1 | Cargar, quitar vacíos y repetidos, normalizar espacios, buscar casi duplicados | pandas, `re`, Jaro-Winkler (`jellyfish`), Jaccard sobre conjuntos de palabras |
| 2.1 | Regex de URLs, correos y teléfonos | `re` |
| 2.2 | Normalizar antes de buscar (invisibles, otro alfabeto, "punto" y "barra", letras separadas) | `unicodedata`, `re` |
| 2.3 | Idioma por oración, con mínimo de palabras y umbral elegidos en desarrollo | `langdetect` |
| 2.4 | Entidades en el texto insertado frente a sinopsis limpias | spaCy `es_core_news_lg` |
| 2.5 | Clasificar oraciones con TF-IDF y con embeddings, umbral por `precision_recall_curve` | scikit-learn, sentence-transformers |
| 2.6 | Libros copiados: vecino más cercano con autores distintos | `NearestNeighbors` con coseno, Jaccard |
| 2.7 | Combinar los detectores y entregar `sospechosos.csv` | pandas |
| 3 | Registrar las preferencias del lector | `input()` con guardado incremental |
| 4 a 8 | Separar, entrenar, comprobar, precision@5, resumen extractivo, frases sustantivas y entidades | scikit-learn, spaCy, TF-IDF con coseno |

De la lista de la cátedra quedaron afuera `thefuzz`, `python-Levenshtein`, fasttext-langdetect, GLiNER y stanza. Con `jellyfish` y `langdetect` alcanzaba, y el enunciado permite spaCy o GLiNER para el NER.

## Qué se resolvió

Se creó el notebook `TP3_grupo7.ipynb` con los pasos 1, 2 y 3 desarrollados y los pasos 4 a 8 como títulos vacíos. Después la reorganización del repo lo dejó como `src/TP3_Civetta_Frank_Fucci_Winter.ipynb`, con los datos en `data/`.

### Lo que se vio en los datos

- El catálogo tiene 8747 libros. Tras la limpieza del paso 1 quedan 8593: salen 1 sin sinopsis, 98 con sinopsis repetida (cursos y series completas) y 55 casi duplicados.
- La muestra etiquetada tiene 500 libros, 100 contaminados. Se miraron los 100 fragmentos insertados y se vieron estos tipos: enlaces con `http` o `www`, dominios sueltos, correos, teléfonos, enlaces disimulados (letras cirílicas, caracteres invisibles, "punto" y "barra", letras separadas por espacios, `[.]`), mensajes en inglés y en portugués, y spam sin enlace.
- Sobre las 500 filas, usadas solo para calibrar, la regex base detecta 24 de los 100 contaminados con un falso positivo (una sinopsis real que menciona `xkcd.com`). Con normalización y dominios sueltos detecta 61 con el mismo falso positivo. Los 39 restantes son promoción sin enlace y mensajes en otro idioma, que son justo los que deben cubrir el detector de idioma y los clasificadores.

### Decisiones de diseño

- **Casi duplicados.** Se comparan solo libros del mismo autor. Se unen si el título "clave" (sin acentos, sin paréntesis de traductor o edición, sin números de tomo) tiene Jaro-Winkler de 0,95 o más, los números de tomo coinciden y la clave es idéntica o las sinopsis comparten el 95 % de las palabras. Así quedan juntos "La venganza de don Mendo (ed. ...)" y "La venganza de don Mendo", y separados "Gran escuela cartomágica Tomo I" y "Tomo II", "Exploraciones secretas en Asia" y "en África", "Mitología oriental" y "occidental".
- **División de la muestra.** Por libro y no por oración, 70 % para desarrollar y 30 % para medir, con `random_state=42` y estratificada, como pide la guía.
- **Umbral de los clasificadores.** Se elige con `precision_recall_curve` para una precisión de 0,90 y no con 0,5. Las probabilidades de desarrollo se calculan con validación cruzada por libro, para que cada libro se puntúe con un modelo que no lo vio entrenar. Si no, el umbral saldría demasiado optimista.
- **Idioma.** Se prueba una grilla de mínimo de palabras y umbral sobre desarrollo y se elige la combinación de mayor recall con precisión de al menos 0,90.
- **Copias.** Un libro se marca como copia si su sinopsis contiene completa la de otro libro de otro autor, con similitud alta y Jaccard confirmando. Las parejas parecidas que no se contienen quedan en una lista para revisar a mano y no se marcan solas.
- **Combinación.** Un libro es sospechoso si lo marca al menos un detector. El motivo guarda todos los que aplican, unidos con `+`.
- **Paso 3.** El lector responde sí, no, "no puedo decidir" o "parece contaminado" (que lo suma a sospechosos con motivo `revision_manual`). Cada respuesta se guarda en el archivo en el momento, así que se puede cortar y retomar. Un libro sin valorar queda con interés vacío y no se convierte en 0.

### Cómo se probó

- El paso 1 y las regex de 2.1 y 2.2 se corrieron con los datos reales sobre una copia temporal. El paso 1 tarda unos 2 segundos.
- En el entorno de la sesión no se pudieron instalar `langdetect`, spaCy ni `jellyfish`, y tampoco bajar los modelos. El notebook completo se corrió de punta a punta con versiones simuladas de esas librerías y con datos sintéticos, y no falló ninguna celda. Eso prueba la lógica y los archivos que se generan. No prueba los resultados reales de idioma, NER ni embeddings.
- La prueba encontró un error que ya está corregido: volver a correr el paso 2.7 después del paso 3 borraba los libros marcados como `revision_manual`. Ahora se conservan, y el catálogo limpio sale idéntico en la segunda corrida.

### Cambios en el repo

- El notebook usa ahora `RUTA = "../data/"`.
- `requirements.txt` suma `langdetect`, `jellyfish` y `spacy`. El modelo `es_core_news_lg` se baja aparte con `python -m spacy download es_core_news_lg`.
- El README incluye el TP3: descripción, estructura de carpetas, instalación, cómo correrlo, una tabla de estado y los números del paso 1.
- El informe del TP2 pasa de `informe.pdf` a `informe_tp2.pdf`, y el del TP3 se va a llamar `informe_tp3.pdf`.

## Qué falta

- Correr el notebook completo en Colab y revisar los resultados reales de 2.3 a 2.6. Los parámetros `SIM_MIN` (0,70) y `JACCARD_MIN` (0,50) del detector de copias no se pudieron calibrar con datos reales.
- Responder en el notebook las preguntas de 2.3, 2.4 y 2.5, que dependen de lo que salga en cada corrida.
- Elegir quién es el lector de referencia, y que esa persona corra el paso 3 en casa antes de ver ninguna predicción.
- Armar los pasos 4 a 8.
- Escribir el informe de hasta tres páginas con las cinco preguntas de la consigna y dos o tres líneas sobre cómo se usaron asistentes de IA (en este trabajo se usó Claude para planificar, programar y revisar el código del notebook).
- Decidir si los CSV de entrega mantienen el prefijo `grupo7_` o pasan al estilo de nombres del notebook.

## Archivos mencionados

- `docs/TP-3.pdf` (enunciado) y la lista "Herramientas NLP Python".
- `src/scraper.py` y `src/TP2_Civetta_Frank_Fucci_Winter.ipynb` como base de lo ya hecho.
- `data/catalogo_tp3.jsonl`, `data/muestra_etiquetada.csv` y los archivos de ejemplo de la cátedra.
