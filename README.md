# cmezabec.github.io — sitio académico de Cristian Meza

Sitio estático publicado con GitHub Pages en <https://cmezabec.github.io>.

Reemplaza a la antigua página en Google Sites (`sites.google.com/uv.cl/cmeza`).

## Cómo funciona

Todo el contenido vive en **un solo archivo**: [`data/cv.json`](data/cv.json).
El script [`build.py`](build.py) lo lee y genera todas las páginas HTML.

```
data/cv.json  ──►  build.py  ──►  index.html, research.html, projects.html,
                                  teaching.html, talks.html, cv.html, contact.html,
                                  sitemap.xml
```

**No edites los archivos `.html` a mano**: se sobrescriben en cada build.
Edita `data/cv.json` (o las plantillas dentro de `build.py`) y vuelve a construir.

## Actualizar el sitio

1. Edita `data/cv.json` (por ejemplo, agrega una publicación al inicio del arreglo
   `publications`).
2. Regenera el HTML:

```bash
cd ~/GitHub/cmezabec.github.io && python3 build.py
```

3. Revisa localmente:

```bash
cd ~/GitHub/cmezabec.github.io && python3 -m http.server 8765
```

y abre <http://localhost:8765> en el navegador. Ctrl-C para detener.

4. Publica:

```bash
cd ~/GitHub/cmezabec.github.io && git add -A && git commit -m "Actualiza publicaciones" && git push
```

GitHub Pages republica solo, en 1–2 minutos.

## Actualizar el CV en PDF

El botón "Curriculum Vitae (PDF)" apunta a `assets/CV_CristianMeza.pdf`.
Cuando recompiles `MEZA_CV_2026.tex`:

```bash
cp "$HOME/Library/CloudStorage/OneDrive-uv.cl(2)/old/CV/MEZA_CV_2026.pdf" ~/GitHub/cmezabec.github.io/assets/CV_CristianMeza.pdf
```

⚠️ Hay **dos** raíces de OneDrive sincronizadas en este Mac: `OneDrive-uv.cl` y
`OneDrive-uv.cl(2)`. Desde agosto de 2026 el CV vivo está en la de **`(2)`**; la otra
ya no lo contiene. Si el comando falla, verifica cuál tiene el `.tex` más reciente:

```bash
ls -la "$HOME/Library/CloudStorage/OneDrive-uv.cl"*/old/CV/MEZA_CV_2026.tex
```

y actualiza `person.cv_date` en `data/cv.json`.

## Estructura

```
├─ build.py               generador (solo biblioteca estándar de Python)
├─ data/cv.json           TODO el contenido del sitio
├─ assets/
│  ├─ styles.css          estilos (tema claro y oscuro automáticos)
│  ├─ CV_CristianMeza.pdf CV completo en PDF
│  └─ img/                foto, logos, favicon
├─ index.html             ┐
├─ research.html          │
├─ projects.html          │  generados — no editar a mano
├─ teaching.html          │
├─ talks.html             │
├─ cv.html                │
├─ contact.html           │
├─ sitemap.xml            ┘
└─ investigacion.html     redirecciones desde los nombres antiguos
   docencia.html
   contacto.html
```

## DOIs automáticos

Los títulos de las publicaciones se convierten en enlaces cuando el campo `doi`
está lleno. Para completarlo automáticamente desde Crossref:

```bash
cd ~/GitHub/cmezabec.github.io && python3 tools/fill_dois.py
```

Muestra lo que encontraría sin escribir nada. Para aplicar, repite con `--write`
y luego `python3 build.py`. Solo acepta coincidencias de título ≥ 0.90, así que no
va a pegar el DOI equivocado en silencio.

## Pendientes

- [ ] Reemplazar `assets/img/CM.jpg` por una foto de mayor resolución
      (la actual es de 170×169 px y se ve pixelada). Ideal: ~600×600 px.
- [ ] `assets/img/UV.png` es en realidad una copia byte a byte de `CIMFAV.png`;
      reemplazar por el logo de la UV o eliminar.
- [ ] Publicar repositorios de código y listarlos en `software` dentro de `cv.json`.
- [ ] **Corregir el CV en LaTeX**: el título del paper de Márquez et al. (2023,
      *Statistics in Medicine*) en `MEZA_CV_2026.tex` dice *"Classification in
      semiparametric nonlinear mixed models using P-Splines and the SAEM algorithm"*,
      pero el título publicado (DOI 10.1002/sim.9895) es *"Classification of
      longitudinal profiles using semi-parametric nonlinear mixed models with
      P-Splines and the SAEM algorithm"*. En el sitio ya está corregido.
