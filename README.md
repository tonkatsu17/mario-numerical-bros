# Mario Numerical Bros 🎮📐

**Laboratorio interactivo de Métodos Numéricos I** creado con Python y Pygame. Una simulación del salto de Mario que permite modificar la velocidad inicial, la resistencia horizontal y la gravedad, mientras se observan los valores de la simulación en una tabla.

## Qué métodos utiliza

| Método | Dónde aparece | Qué calcula |
|---|---|---|
| Taylor de grado 2 | `PersonajeMario.actualizar_fisica` | Actualización de `x` y `y` a partir de velocidad y aceleración |
| Euler explícito | `PersonajeMario.actualizar_fisica` | Actualización de `vx` y `vy` |
| Suma de Riemann (extremo derecho) | `PersonajeMario.actualizar_fisica` | Aproximación a la distancia vertical acumulada mediante `abs(vy)*dt` |

> **Nota académica:** las barras dibujadas sobre la escena representan alturas del personaje, no los rectángulos de la integral de rapidez contra tiempo. El factor `/20` es una escala de visualización y la simulación no está calibrada en unidades SI.

## Ejecutar en computadora

Necesitas Python 3.10+.

```bash
python -m pip install -r requirements.txt
python desktop/main.py
```

Controles: **espacio** para saltar; **flechas izquierda/derecha** para moverse; o usa los botones y deslizadores de la interfaz.

## Versión web (Pygbag + Vercel)

Un programa de escritorio Pygame **no corre directamente en Vercel**. Para publicarlo en navegador usamos [Pygbag](https://pygame-web.github.io/wiki/pygbag/), que ejecuta Python/Pygame mediante WebAssembly, y Vercel sirve la salida estática. **Se mantienen las fórmulas y la lógica del original**; la versión web solo adapta el bucle a `asyncio` para ceder el control al navegador.

### Compilar en tu computadora

```bash
python -m pip install -r requirements-build.txt
bash scripts/build_web.sh
```

El resultado estará en `public/`. Para probarlo localmente usa un servidor HTTP, no abras el archivo directamente:

```bash
python -m http.server 8000 --directory public
```

Abre <http://localhost:8000>.

### Publicarlo con GitHub + Vercel

1. Crea un repositorio en GitHub y sube este proyecto a la rama `main`.
2. En **GitHub Actions**, ejecuta el workflow **Build browser edition for Vercel**. El workflow instala Pygbag, crea la copia web y guarda el sitio estático generado en `public/`, con un commit automático.
3. Conecta el repositorio a Vercel. Selecciona **Framework Preset: Other** y **Output Directory: public**. El archivo `vercel.json` incluye esa configuración.
4. Cuando GitHub Actions termine correctamente y el commit de `public/` llegue a Vercel, el dominio del despliegue servirá el juego.

**Importante:** para que el workflow pueda hacer commit, en GitHub configura `Settings → Actions → General → Workflow permissions → Read and write permissions`. Si esa opción está bloqueada por la organización, compila localmente y sube manualmente `public/`.

### Limitaciones y comprobaciones pendientes

- La salida web **no se ha probado aquí en un navegador**: conviene validar consola, tipografías, eventos de teclado, arrastre de deslizadores y el renderizado de emojis después del primer deploy.
- El diseño original está pensado para pantallas de ~1280×720 y teclado. En móvil puede requerir ajustes de interfaz para controles táctiles y tablas pequeñas. No se modificó esa lógica para conservar la presentación existente.
- El paso numérico fijo de `0.05` se mantiene incluso cuando la tasa real de cuadros varía.
- La primera carga puede tardar por la descarga del entorno de Python/WebAssembly.
- No hay servicios de backend, cuentas, ni almacenamiento de datos de usuarios.

## Estructura

```text
mario-numerical-bros/
├── desktop/main.py            # Código original de escritorio
├── web/main.py                # Copia web generada automáticamente
├── scripts/prepare_web.py     # Únicos ajustes: asyncio/retorno
├── scripts/build_web.sh       # Genera el sitio estático
├── public/                    # Sitio para Vercel (inicialmente página de aviso)
├── .github/workflows/build-web.yml
├── requirements.txt
├── requirements-build.txt
├── vercel.json
└── README.md
```

## Autores

- Horiuchi Jurado Kenji
- López García Zoran
- Caballero Salcedo Suleima Angelina
- Martinez Arteaga Ines Rosalia

Proyecto académico de Métodos Numéricos I.

## Licencia

Este repositorio no incluye archivos gráficos de Nintendo ni recursos de terceros. Se recomienda definir una licencia de software con autorización de los cuatro integrantes antes de publicarlo como código abierto.
