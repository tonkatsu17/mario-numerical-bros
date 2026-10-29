"""
Laboratorio Interactivo de Métodos Numéricos I: Mario Taylor & Riemann
Versión Ajustada: Salto Potente, Bloques Interactivos y Tabla Amplia
"""
import pygame
import asyncio
import sys

pygame.init()

ANCHO_INIT, ALTO_INIT = 1280, 720
VENTANA = pygame.display.set_mode((ANCHO_INIT, ALTO_INIT), pygame.RESIZABLE)
pygame.display.set_caption("Mario Numerical Bros - Métodos de Taylor y Riemann")

# Paleta de Colores
CIELO = (90, 140, 255)
SUELO = (210, 85, 20)
BLOQUE = (235, 155, 30)
MARIO_RED = (230, 40, 40)
MARIO_BLUE = (30, 70, 210)
PANEL_BG = (22, 27, 42)
PANEL_MATH_BG = (12, 16, 26)
BORDES = (55, 70, 105)
TEXTO_BLANCO = (245, 245, 255)
TEXTO_SEC = (170, 185, 215)
DESTACADO_AZUL = (0, 215, 255)
DESTACADO_AMARILLO = (255, 215, 0)
BOTON_BG = (50, 115, 230)
BOTON_HOVER = (80, 145, 255)
SLIDER_BG = (45, 58, 80)
SLIDER_HANDLE = (255, 205, 50)

RELOJ = pygame.time.Clock()

def obtener_fuentes(alto_v):
    factor = max(0.9, min(1.3, alto_v / 720.0))
    return {
        "titulo": pygame.font.SysFont("Trebuchet MS", int(19 * factor), bold=True),
        "subtitulo": pygame.font.SysFont("Trebuchet MS", int(15 * factor), bold=True),
        "texto": pygame.font.SysFont("Consolas", int(14 * factor), bold=True),
        "tabla": pygame.font.SysFont("Consolas", int(13 * factor), bold=True)
    }

# ---------------------------------------------------------
# COMPONENTES DE INTERFAZ GRÁFICA
# ---------------------------------------------------------
class Boton:
    def __init__(self, x, y, ancho, alto, texto, callback):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.callback = callback

    def actualizar_pos(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)

    def dibujar(self, superficie, fuentes):
        mouse_pos = pygame.mouse.get_pos()
        color = BOTON_HOVER if self.rect.collidepoint(mouse_pos) else BOTON_BG
        pygame.draw.rect(superficie, color, self.rect, border_radius=8)
        pygame.draw.rect(superficie, BORDES, self.rect, 2, border_radius=8)
        txt = fuentes["subtitulo"].render(self.texto, True, TEXTO_BLANCO)
        superficie.blit(txt, txt.get_rect(center=self.rect.center))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.callback()

class Slider:
    def __init__(self, x, y, ancho, min_val, max_val, val_inicial, etiqueta, formato="%.2f"):
        self.rect = pygame.Rect(x, y, ancho, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.valor = val_inicial
        self.etiqueta = etiqueta
        self.formato = formato
        self.arrastrando = False
        self._actualizar_handle(x, ancho)

    def _actualizar_handle(self, x, ancho):
        porcentaje = (self.valor - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = x + porcentaje * ancho

    def actualizar_pos(self, x, y, ancho):
        self.rect = pygame.Rect(x, y, ancho, 10)
        self._actualizar_handle(x, ancho)

    def dibujar(self, superficie, fuentes):
        txt_etiqueta = fuentes["subtitulo"].render(self.etiqueta, True, DESTACADO_AMARILLO)
        txt_valor = fuentes["texto"].render(self.formato % self.valor, True, TEXTO_BLANCO)

        superficie.blit(txt_etiqueta, (self.rect.x, self.rect.y - 24))
        superficie.blit(txt_valor, (self.rect.x + self.rect.width - 55, self.rect.y - 24))

        pygame.draw.rect(superficie, SLIDER_BG, self.rect, border_radius=5)
        pygame.draw.circle(superficie, SLIDER_HANDLE, (int(self.handle_x), self.rect.centery), 10)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            dist = ((evento.pos[0] - self.handle_x)**2 + (evento.pos[1] - self.rect.centery)**2)**0.5
            if dist <= 16 or self.rect.collidepoint(evento.pos):
                self.arrastrando = True
                self._actualizar_val(evento.pos[0])
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
            self._actualizar_val(evento.pos[0])

    def _actualizar_val(self, pos_x):
        self.handle_x = max(self.rect.x, min(pos_x, self.rect.x + self.rect.width))
        porcentaje = (self.handle_x - self.rect.x) / self.rect.width
        self.valor = self.min_val + porcentaje * (self.max_val - self.min_val)

# ---------------------------------------------------------
# MARIO Y FÍSICA DE TAYLOR & RIEMANN
# ---------------------------------------------------------
class PersonajeMario:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 80.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.ancho = 42
        self.alto = 60
        self.en_suelo = True

        self.iteraciones = []
        self.area_riemann = 0.0
        self.paso_tiempo = 0.05
        self.paso_actual = 0

    def saltar(self, fuerza_salto):
        if self.en_suelo:
            self.vy = -fuerza_salto   # Fuerza ajustada
            self.en_suelo = False
            self.iteraciones = []
            self.area_riemann = 0.0
            self.paso_actual = 0

    def actualizar_fisica(self, viento, gravedad, suelo_y, bloques, max_x_cancha):
        dt = self.paso_tiempo

        ax = -viento * self.vx if not self.en_suelo else -0.25 * self.vx
        ay = gravedad if not self.en_suelo else 0.0

        # --- TAYLOR (Grado 2) ---
        term_pos_y = self.vy * dt
        term_acc_y = 0.5 * ay * (dt ** 2)

        self.x += self.vx * dt + 0.5 * ax * (dt ** 2)
        self.y += term_pos_y + term_acc_y

        self.vx += ax * dt
        self.vy += ay * dt

        # --- RIEMANN ---
        if not self.en_suelo:
            self.paso_actual += 1
            v_inst = abs(self.vy)
            area_paso = v_inst * dt
            self.area_riemann += area_paso

            altura_m = max(0.0, (suelo_y - self.y) / 20.0)

            self.iteraciones.append({
                "i": self.paso_actual,
                "t": self.paso_actual * dt,
                "y": altura_m,
                "vy": -self.vy,
                "taylor_term": (term_pos_y + term_acc_y) / 20.0,
                "riemann_area": self.area_riemann / 20.0,
                "rx": int(self.x + self.ancho // 2),
                "ry": int(self.y),
                "rh": int(suelo_y - self.y)
            })

        # Colisión con bloques (piedritas)
        mario_rect = pygame.Rect(int(self.x), int(self.y - self.alto), self.ancho, self.alto)
        piso_actual = suelo_y

        for b in bloques:
            if mario_rect.colliderect(b) and self.vy >= 0:
                # Si cae sobre el bloque
                if self.y - self.vy * dt <= b.top + 10:
                    piso_actual = float(b.top)
                    break

        # Colisión con el piso o bloque
        if self.y >= piso_actual:
            self.y = piso_actual
            self.vy = 0.0
            self.en_suelo = True

        self.x = max(20.0, min(self.x, max_x_cancha - self.ancho))

    def dibujar(self, superficie, suelo_y):
        # 1. Rectángulos de Riemann en la pantalla
        for it in self.iteraciones:
            rx, ry, rh = it["rx"], it["ry"], it["rh"]
            if rh > 0:
                s = pygame.Surface((12, rh), pygame.SRCALPHA)
                s.fill((0, 215, 255, 60))
                superficie.blit(s, (rx, ry))
                pygame.draw.rect(superficie, DESTACADO_AZUL, (rx, ry, 12, rh), 1)

        # 2. Dibujar personaje de Mario
        rect_cuerpo = pygame.Rect(int(self.x), int(self.y - self.alto), self.ancho, self.alto)
        rect_gorra = pygame.Rect(int(self.x - 3), int(self.y - self.alto), self.ancho + 6, 16)
        rect_ojos = pygame.Rect(int(self.x + self.ancho - 12), int(self.y - self.alto + 16), 8, 8)

        pygame.draw.rect(superficie, MARIO_BLUE, rect_cuerpo, border_radius=5)
        pygame.draw.rect(superficie, MARIO_RED, rect_gorra, border_radius=4)
        pygame.draw.rect(superficie, TEXTO_BLANCO, rect_ojos, border_radius=2)

# ---------------------------------------------------------
# APLICACIÓN PRINCIPAL
# ---------------------------------------------------------
class LaboratorioTaylorRiemann:
    def __init__(self):
        self.mario = PersonajeMario()

        # Fuerza de salto aumentada (de 15.0 a 45.0) para que salte alto
        self.slider_salto = Slider(0, 0, 100, 20.0, 50.0, 32.0, "Fuerza de Salto")
        self.slider_viento = Slider(0, 0, 100, 0.0, 0.5, 0.05, "Resistencia Viento (c)", formato="%.2f")
        self.slider_g = Slider(0, 0, 100, 2.0, 25.0, 9.81, "Gravedad (g)", formato="%.2f")

        self.btn_saltar = Boton(0, 0, 100, 48, "🦘 LANZAR SALTO", self.hacer_salto)
        self.btn_izq = Boton(0, 0, 100, 42, "⬅️ IZQ", self.mover_izq)
        self.btn_der = Boton(0, 0, 100, 42, "➡️ DER", self.mover_der)

        self.sliders = [self.slider_salto, self.slider_viento, self.slider_g]

    def hacer_salto(self):
        self.mario.saltar(self.slider_salto.valor)

    def mover_izq(self):
        self.mario.vx = -10.0

    def mover_der(self):
        self.mario.vx = 10.0

    def recalcular_layout(self, ancho, alto):
        ancho_panel = max(380, int(ancho * 0.32))
        px = ancho - ancho_panel + 30
        ancho_ctrl = ancho_panel - 60

        start_y = int(alto * 0.08)
        paso_y = max(60, int(alto * 0.09))

        for i, s in enumerate(self.sliders):
            s.actualizar_pos(px, start_y + i * paso_y, ancho_ctrl)

        btn_y = start_y + len(self.sliders) * paso_y + 15
        self.btn_saltar.actualizar_pos(px, btn_y, ancho_ctrl, 48)

        w_half = (ancho_ctrl - 12) // 2
        self.btn_izq.actualizar_pos(px, btn_y + 60, w_half, 42)
        self.btn_der.actualizar_pos(px + w_half + 12, btn_y + 60, w_half, 42)

        return ancho_panel

    async def ejecutar(self):
        while True:
            ancho_v, alto_v = VENTANA.get_size()
            fuentes = obtener_fuentes(alto_v)
            ancho_panel = self.recalcular_layout(ancho_v, alto_v)

            ancho_cancha = ancho_v - ancho_panel
            suelo_y = int(alto_v * 0.48)  # Suelo a buena altura para ver el salto

            if self.mario.en_suelo and self.mario.y == 0.0:
                self.mario.y = suelo_y

            # Crear bloques / piedritas interactivas
            bloques = [
                pygame.Rect(220, int(suelo_y - 80), 80, 25),
                pygame.Rect(450, int(suelo_y - 140), 90, 25),
                pygame.Rect(680, int(suelo_y - 80), 80, 25)
            ]

            VENTANA.fill(CIELO)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return

                for s in self.sliders:
                    s.manejar_evento(evento)
                self.btn_saltar.manejar_evento(evento)
                self.btn_izq.manejar_evento(evento)
                self.btn_der.manejar_evento(evento)

            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_RIGHT]:
                self.mario.vx = 10.0
            elif teclas[pygame.K_LEFT]:
                self.mario.vx = -10.0
            if teclas[pygame.K_SPACE]:
                self.hacer_salto()

            self.mario.actualizar_fisica(self.slider_viento.valor, self.slider_g.valor, suelo_y, bloques, ancho_cancha)

            # --- ESCENARIO ---
            pygame.draw.rect(VENTANA, SUELO, (0, suelo_y, ancho_cancha, alto_v - suelo_y))

            # Dibujar Bloques
            for b in bloques:
                pygame.draw.rect(VENTANA, BLOQUE, b, border_radius=4)
                pygame.draw.rect(VENTANA, (180, 110, 20), b, 2, border_radius=4)

            self.mario.dibujar(VENTANA, suelo_y)

            # --- TABLA DE ITERACIONES AMPLIA (ABAJO A LA IZQUIERDA) ---
            panel_tabla_rect = pygame.Rect(0, suelo_y + 35, ancho_cancha, alto_v - (suelo_y + 35))
            pygame.draw.rect(VENTANA, PANEL_MATH_BG, panel_tabla_rect)
            pygame.draw.line(VENTANA, BORDES, (0, suelo_y + 35), (ancho_cancha, suelo_y + 35), 3)

            txt_t_title = fuentes["titulo"].render("📋 TABLA DE PASOS EN TIEMPO REAL (Métodos Numéricos)", True, DESTACADO_AZUL)
            VENTANA.blit(txt_t_title, (20, suelo_y + 45))

            # Encabezado formateado
            headers = f"{'Paso (i)':<10}{'Tiempo (t)':<12}{'Altura Y (m)':<15}{'Vel Y (m/s)':<15}{'Paso Taylor ΔY':<18}{'Área Riemann':<20}"
            VENTANA.blit(fuentes["texto"].render(headers, True, DESTACADO_AMARILLO), (20, suelo_y + 75))
            pygame.draw.line(VENTANA, BORDES, (20, suelo_y + 95), (ancho_cancha - 20, suelo_y + 95), 1)

            # Mostrar las últimas iteraciones
            ultimas_it = self.mario.iteraciones[-6:]
            for idx, it in enumerate(ultimas_it):
                fila = f"{it['i']:<10}{it['t']:<12.2f}{it['y']:<15.2f}{it['vy']:<15.2f}{it['taylor_term']:<18.3f}{it['riemann_area']:<20.3f}"
                VENTANA.blit(fuentes["tabla"].render(fila, True, TEXTO_BLANCO), (20, suelo_y + 105 + idx * 22))

            # --- PANEL DERECHO ---
            panel_ctrl = pygame.Rect(ancho_cancha, 0, ancho_panel, alto_v)
            pygame.draw.rect(VENTANA, PANEL_BG, panel_ctrl)
            pygame.draw.line(VENTANA, BORDES, (ancho_cancha, 0), (ancho_cancha, alto_v), 3)

            px_texto = ancho_cancha + 30
            VENTANA.blit(fuentes["titulo"].render("⚙️ CONTROLES", True, TEXTO_BLANCO), (px_texto, 20))

            for s in self.sliders:
                s.dibujar(VENTANA, fuentes)

            self.btn_saltar.dibujar(VENTANA, fuentes)
            self.btn_izq.dibujar(VENTANA, fuentes)
            self.btn_der.dibujar(VENTANA, fuentes)

            start_info_y = int(alto_v * 0.58)
            step_info_y = max(22, int(alto_v * 0.035))

            info_textos = [
                "📐 CONCEPTO A EXPLICAR:",
                "-----------------------------------",
                "• TAYLOR (Grado 2):",
                "  Calcula el salto cuadro a cuadro.",
                "• RIEMANN (Área):",
                "  Suma la altura de cada rectángulo.",
                "-----------------------------------",
                f"Rectángulos Procesados: {len(self.mario.iteraciones)}",
                f"Área Total Salto: {self.mario.area_riemann / 20.0:.2f} m"
            ]

            for i, line in enumerate(info_textos):
                col = DESTACADO_AZUL if "📐" in line or "•" in line else TEXTO_SEC
                if "Área Total" in line:
                    col = DESTACADO_AMARILLO
                VENTANA.blit(fuentes["subtitulo"].render(line, True, col), (px_texto, start_info_y + i * step_info_y))

            pygame.display.flip()
            RELOJ.tick(60)
            await asyncio.sleep(0)  # Yield control to the browser event loop

if __name__ == "__main__":
    app = LaboratorioTaylorRiemann()
    asyncio.run(app.ejecutar())
