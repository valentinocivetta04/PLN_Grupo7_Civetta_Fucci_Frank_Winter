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
| `serie` | Serie a la que pertenece, si corresponde |
| `sinopsis` | Texto completo de la sinopsis |
| `url_libro` | Dirección de la ficha |
| `categoria_origen` | Categoría seleccionada por el grupo (Clásico) |
| `fecha_extraccion` | Fecha en que se obtuvo el registro |

*(Campo opcional: dirección de la portada — a evaluar su incorporación.)*

---

## 3. Localización de los datos

Análisis realizado sobre una ficha individual de ejemplo:
`https://ww3.lectulandia.com/book/un-voluntario-realista/`

| Dato | Tipo de página | Etiqueta HTML | Selector propuesto |
|---|---|---|---|
| Título | Ficha individual | `<h1>` dentro de `<div id="title">` | `#title h1` |
| Autores | Ficha individual | `<a class="dinSource">` dentro de `<div id="autor">` | `#autor a.dinSource` |
| Géneros | Ficha individual | `<a class="dinSource">` dentro de `<div id="genero">` | `#genero a.dinSource` |
| Serie | Ficha individual | `<a class="dinSource">` dentro de `<div id="serie">` (presente solo si el libro pertenece a una serie) | `#serie a.dinSource` |
| Sinopsis | Ficha individual | `<p class="description">` dentro de `<div id="sinopsis">` | `#sinopsis p.description` |

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

---

## 4. Estrategia de extracción

1. Abrir la página de la categoría "Clásico" con Playwright.
2. Recorrer las páginas de listado necesarias hasta reunir las URLs de los 150 libros propuestos.
3. Obtener el HTML de cada página de listado mediante Playwright.
4. Analizar ese HTML con BeautifulSoup para localizar los enlaces a las fichas individuales.
5. Extraer las URL de las fichas de los libros.
6. Visitar cada ficha individual con Playwright.
7. Extraer los metadatos (título, autores, géneros, serie) y la sinopsis de cada ficha con BeautifulSoup, usando los selectores definidos en la sección 3.
8. Limpiar y validar los datos (eliminar espacios y saltos de línea innecesarios, normalizar campos ausentes).
9. Eliminar libros duplicados, tomando `url_libro` como clave.
10. Guardar el resultado de forma incremental en `data/libros.csv`, incluyendo `categoria_origen` y `fecha_extraccion`.

Durante la ejecución se incorporará una pausa entre cada página/ficha visitada y se controlarán los errores de forma que no se detenga completamente el proceso ante una falla puntual.
