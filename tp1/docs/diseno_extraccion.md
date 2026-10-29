# Diseño de la extracción — TP1 NLP (TUIA)

**Comisión:** 2 (TUIA) — Grupo: Civetta/Fucci

**Integrantes:**
- Civetta Valentino — Legajo: 45948755
- Fucci Milagros — Legajo: 47076861
- Winter Federico — Legajo: 44101265
- Frank Maximiliano — Legajo: 38726401

**Docentes:** GEARY, Alan — MANSON, Juan Pablo

---

## 1. Categoría seleccionada

- **Nombre de la categoría:** Clásico
- **URL de la categoría:** https://ww3.lectulandia.co/genero/clasico/
- **Cantidad de libros que se propone extraer:** 150 (los primeros 150 de la categoría)
- **Criterio utilizado para seleccionar la categoría:** se eligió por la gran cantidad de libros disponibles para extraer y la variedad de los mismos, además de que contiene títulos reconocidos mundialmente.

---

## 2. Datos que se extraerán

| Campo | Descripción |
|---|---|
| `titulo` | Título del libro |
| `autores` | Autor o autores |
| `generos` | Género o géneros |
| `serie` | Serie a la que pertenece, si corresponde (`N/A` si no pertenece a ninguna) |
| `numero_serie` | Número de orden del libro dentro de la serie, si corresponde (`N/A` si no pertenece a ninguna) |
| `sinopsis` | Texto completo de la sinopsis |
| `url_libro` | Dirección de la ficha |
| `categoria_origen` | Categoría seleccionada por el grupo (Clásico) |
| `fecha_extraccion` | Fecha y hora en que se obtuvo el registro |

*(Campo opcional: dirección de la portada — a evaluar su incorporación.)*

---

## 3. Localización de los datos

Análisis realizado sobre una ficha individual de ejemplo:
`https://ww3.lectulandia.com/book/un-voluntario-realista/`

| Dato | Tipo de página | Etiqueta HTML | Selector propuesto |
|---|---|---|---|
| Título | Ficha individual | `<h1>` dentro de `<div id="title">` | `#title h1` |
| Autores | Ficha individual | `<a class="dinSource">` dentro de `<div id="autor">` | `#autor a` |
| Géneros | Ficha individual | `<a class="dinSource">` dentro de `<div id="genero">` | `#genero a` |
| Serie | Ficha individual | `<a class="dinSource">` dentro de `<div id="serie">` (presente solo si el libro pertenece a una serie) | `#serie a.dinSource` |
| Número de serie | Ficha individual | Texto plano dentro de `<span class="tagTitle">` (ej. "Libro 8 de: "), no está en una etiqueta aparte | Se extrae con la expresión regular `Libro\s+(\d+)\s+de` sobre el texto de `#serie span.tagTitle` |
| Sinopsis | Ficha individual | `<div id="sinopsis">` (el texto puede estar directo dentro del div, o dentro de un `<p class="description">` anidado, según la ficha) | `#sinopsis` |

**Ejemplos de HTML inspeccionado:**

```html
<!-- Título -->
<div id="title">
  <h1>Un voluntario realista</h1>
</div>

<!-- Autor -->
<div id="autor" class="realign">
  <span class="tagTitle">Autor: </span>
  <a class="dinSource" href="/autor/benito-perez-galdos/" rel="tag">Benito Pérez Galdós</a>
</div>

<!-- Géneros -->
<div id="genero" class="realign">
  <span class="tagTitle">Generos: </span>
  <a class="dinSource" href="/genero/clasico/" rel="tag">Clásico</a>
  <a class="dinSource" href="/genero/historico/" rel="tag">Histórico</a>
</div>

<!-- Serie -->
<div id="serie" class="realign">
  <span class="tagTitle">Libro 8 de: </span>
  <a class="dinSource" href="/serie/episodios-nacionales-segunda-serie/" rel="tag">Episodios Nacionales - Segunda serie</a>
</div>

<!-- Sinopsis -->
<div id="sinopsis" class="realign">
  <p class="description">El gran friso narrativo de los Episodios Nacionales sirvió de vehículo a Benito Pérez Galdós...</p>
</div>
```

Los selectores fueron obtenidos inspeccionando el HTML real del sitio mediante las herramientas de desarrollo del navegador.

**Nota:** se detectó que la estructura interna de `#sinopsis` varía entre fichas — algunas envuelven el texto en un `<p class="description">`, mientras que otras lo dejan como texto directo dentro del div (sin `<p>` intermedio). Por eso se optó por el selector genérico `#sinopsis`, que funciona en ambos casos.

---

## 4. Estrategia de extracción

1. Abrir la página de la categoría "Clásico" con Playwright.
   *Implementación:* en `main()` se lanza un Chromium headless (`p.chromium.launch(headless=True)`) y se navega con `page.goto(f"{URL_CATEGORIA}{pagina_actual}", wait_until="domcontentloaded")`.
2. Recorrer las páginas de listado necesarias hasta reunir las URLs de los 150 libros propuestos.
   *Implementación:* bucle `while total_extraidos < LIBROS_OBJETIVO`, que incrementa `pagina_actual` en cada vuelta hasta llegar al objetivo o quedarse sin páginas.
3. Obtener el HTML de cada página de listado mediante Playwright.
   *Implementación:* `html_cat = await page.content()` sobre la página de listado ya cargada.
4. Analizar ese HTML con BeautifulSoup para localizar los enlaces a las fichas individuales.
   *Implementación:* `soup_cat = BeautifulSoup(html_cat, 'html.parser')` y `enlaces_libros = soup_cat.select('article.card a.title')`.
5. Extraer las URL de las fichas de los libros.
   *Implementación:* por cada enlace, `url_libro = URL_BASE + enlace.get('href')`, ya que el `href` viene como ruta relativa.
6. Visitar cada ficha individual con Playwright.
   *Implementación:* dentro de `extraer_datos_ficha()`, se reutiliza la misma pestaña con `await page.goto(url_libro, wait_until="domcontentloaded")`.
7. Extraer los metadatos (título, autores, géneros, serie) y la sinopsis de cada ficha con BeautifulSoup, usando los selectores definidos en la sección 3.
   *Implementación:* todo el cuerpo de `extraer_datos_ficha()`; el número de serie es la excepción a los selectores de la sección 3, ya que se obtiene con una expresión regular sobre el texto de `span.tagTitle`.
8. Limpiar y validar los datos (eliminar espacios y saltos de línea innecesarios, normalizar campos ausentes).
   *Implementación:* `get_text(strip=True)` en los campos de texto, `serie`/`numero_serie` normalizados a `"N/A"` cuando no hay serie, y solo se guarda el libro si tiene `titulo` (`if datos_libro and datos_libro["titulo"]`).
9. Eliminar libros duplicados, tomando `url_libro` como clave.
   *Implementación:* el set `urls_visitadas` guarda las URL ya procesadas; si `url_libro` ya está ahí, se saltea con `continue` sin volver a visitarla.
10. Guardar el resultado de forma incremental en `data/libros.csv`, incluyendo `categoria_origen` y `fecha_extraccion`.
    *Implementación:* cada libro se convierte en un `DataFrame` de una fila (`pd.DataFrame([datos_libro])`) y se escribe con `to_csv(..., mode='a')`, agregando el encabezado solo la primera vez que se crea el archivo.

Durante la ejecución se incorporará una pausa entre cada página/ficha visitada y se controlarán los errores de forma que no se detenga completamente el proceso ante una falla puntual.

*Implementación:* `await asyncio.sleep(2)` después de procesar cada ficha, y bloques `try/except` tanto en `extraer_datos_ficha()` (por ficha) como en el bucle principal de `main()` (por página de listado), que informan el error por consola y continúan con el siguiente elemento en vez de detener todo el script.
