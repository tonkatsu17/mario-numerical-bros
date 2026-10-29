"""Create a browser-compatible copy without altering the desktop source or numerical methods."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / 'desktop' / 'main.py').read_text(encoding='utf-8')

src = src.replace('import pygame\nimport sys\n', 'import pygame\nimport asyncio\nimport sys\n', 1)
src = src.replace('    def ejecutar(self):\n        while True:', '    async def ejecutar(self):\n        while True:', 1)
src = src.replace('                    pygame.quit()\n                    sys.exit()\n', '                    pygame.quit()\n                    return\n', 1)
src = src.replace('            RELOJ.tick(60)\n', '            RELOJ.tick(60)\n            await asyncio.sleep(0)  # Yield control to the browser event loop\n', 1)
src = src.replace('    app.ejecutar()\n', '    asyncio.run(app.ejecutar())\n', 1)

# Only the scheduling/exit mechanism differs; all calculations and rendering are preserved.
(ROOT / 'web').mkdir(exist_ok=True)
(ROOT / 'web' / 'main.py').write_text(src, encoding='utf-8')
print('Generated web/main.py. Desktop version unchanged.')
