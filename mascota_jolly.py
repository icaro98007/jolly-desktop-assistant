import tkinter as tk
import requests
import threading
import subprocess
import math
import time
import random

# ==========================================
# CONFIGURACIÓN PRINCIPAL
# ==========================================
WEBHOOK_URL = "http://localhost:6789/webhook/jolly"
SESSION_ID = "jolly_desktop"
COLOR_FONDO_TRANSPARENTE = "#010101"

# Paletas Cyber-Neón por emoción
TEMAS_EMOCION = {
    "feliz": {
        "neon": "#00F5D4",
        "secundario": "#00BBF9",
        "visor": "#071318",
        "chasis": "#121824",
        "estado": "● EN LÍNEA"
    },
    "pensando": {
        "neon": "#FBBF24",
        "secundario": "#F59E0B",
        "visor": "#161208",
        "chasis": "#1A1822",
        "estado": "◌ PROCESANDO..."
    },
    "sorprendido": {
        "neon": "#FF2A85",
        "secundario": "#9B5DE5",
        "visor": "#180814",
        "chasis": "#1E1424",
        "estado": "⚡ ALERTA"
    },
    "cansado": {
        "neon": "#64748B",
        "secundario": "#475569",
        "visor": "#0B0E14",
        "chasis": "#11141C",
        "estado": "☾ REPOSO"
    },
    "neutral": {
        "neon": "#38BDF8",
        "secundario": "#818CF8",
        "visor": "#09111E",
        "chasis": "#131926",
        "estado": "● ACTIVO"
    }
}


class JollyCyberPet:
    def __init__(self, root):
        self.root = root
        self.root.title("Jolly Cyber-Pet")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", COLOR_FONDO_TRANSPARENTE)
        self.root.configure(bg=COLOR_FONDO_TRANSPARENTE)

        # Posición inicial (esquina inferior derecha)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.win_w = 340
        self.win_h = 410
        pos_x = screen_w - self.win_w - 35
        pos_y = screen_h - self.win_h - 65
        self.root.geometry(f"{self.win_w}x{self.win_h}+{pos_x}+{pos_y}")

        # Variables de estado y animación
        self.emocion = "feliz"
        self.hablando = False
        self.voz_activa = True
        self.tiempo = 0.0
        self.parpadeo = False
        self.proximo_parpadeo = time.time() + 3.0
        self.drag_x = 0
        self.drag_y = 0

        # Canvas principal transparente
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=220,
            bg=COLOR_FONDO_TRANSPARENTE,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.TOP)

        # Eventos de arrastre y menú contextual
        self.canvas.bind("<ButtonPress-1>", self.iniciar_arrastre)
        self.canvas.bind("<B1-Motion>", self.mover_ventana)
        self.canvas.bind("<Button-3>", self.mostrar_menu)

        # Panel HUD de diálogo y entrada
        self.construir_hud()

        # Saludo inicial
        self.mostrar_respuesta("¡Sistemas en línea! ¿Qué misión tenemos hoy?", "feliz", hablar=False)

        # Bucle de animación a ~30 FPS
        self.animar()

    def construir_hud(self):
        # Contenedor principal del globo HUD
        self.hud_frame = tk.Frame(
            self.root,
            bg="#0B101B",
            highlightbackground="#00F5D4",
            highlightthickness=2,
            padx=10,
            pady=8
        )
        self.hud_frame.pack(fill=tk.X, padx=12, pady=(0, 6))

        # Barra superior del HUD (Nombre + Estado)
        top_bar = tk.Frame(self.hud_frame, bg="#0B101B")
        top_bar.pack(fill=tk.X, pady=(0, 4))

        self.lbl_nombre = tk.Label(
            top_bar,
            text="JOLLY // AI-CORE",
            font=("Consolas", 8, "bold"),
            fg="#94A3B8",
            bg="#0B101B"
        )
        self.lbl_nombre.pack(side=tk.LEFT)

        self.lbl_estado = tk.Label(
            top_bar,
            text="● EN LÍNEA",
            font=("Consolas", 8, "bold"),
            fg="#00F5D4",
            bg="#0B101B"
        )
        self.lbl_estado.pack(side=tk.RIGHT)

        # Texto de respuesta
        self.lbl_texto = tk.Label(
            self.hud_frame,
            text="",
            font=("Segoe UI", 9),
            fg="#F1F5F9",
            bg="#0B101B",
            wraplength=285,
            justify=tk.LEFT,
            anchor="w"
        )
        self.lbl_texto.pack(fill=tk.X, pady=(2, 8))

        # Caja de entrada + Botón enviar
        input_row = tk.Frame(self.hud_frame, bg="#151E2E", padx=4, pady=3)
        input_row.pack(fill=tk.X)

        self.entry = tk.Entry(
            input_row,
            font=("Segoe UI", 9),
            bg="#151E2E",
            fg="#FFFFFF",
            insertbackground="#00F5D4",
            relief=tk.FLAT,
            borderwidth=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        self.entry.bind("<Return>", self.enviar_mensaje)

        self.btn_enviar = tk.Button(
            input_row,
            text="➤",
            font=("Segoe UI", 9, "bold"),
            bg="#00F5D4",
            fg="#061018",
            activebackground="#00BBF9",
            relief=tk.FLAT,
            cursor="hand2",
            padx=8,
            command=self.enviar_mensaje
        )
        self.btn_enviar.pack(side=tk.RIGHT)

    def iniciar_arrastre(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def mover_ventana(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")

    def mostrar_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg="#0F172A", fg="#F8FAFC", activebackground="#00F5D4", activeforeground="#061018")
        estado_voz = "Silenciar voz" if self.voz_activa else "Activar voz"
        menu.add_command(label=f"🔊 {estado_voz}", command=self.alternar_voz)
        menu.add_separator()
        menu.add_command(label="❌ Cerrar a Jolly", command=self.root.destroy)
        menu.tk_popup(event.x_root, event.y_root)

    def alternar_voz(self):
        self.voz_activa = not self.voz_activa

    def calcular_mirada(self, cx, cy):
        try:
            mx = self.root.winfo_pointerx() - self.root.winfo_rootx()
            my = self.root.winfo_pointery() - self.root.winfo_rooty()
            dx = max(-6.0, min(6.0, (mx - cx) * 0.03))
            dy = max(-4.0, min(4.0, (my - cy) * 0.03))
            return dx, dy
        except Exception:
            return 0.0, 0.0

    def dibujar_robot(self):
        self.canvas.delete("all")
        tema = TEMAS_EMOCION.get(self.emocion, TEMAS_EMOCION["neutral"])
        neon = tema["neon"]
        sec = tema["secundario"]
        visor_bg = tema["visor"]
        chasis = tema["chasis"]

        cx = self.win_w // 2
        # Flotación sinusoidal suave
        flote_y = math.sin(self.tiempo * 2.4) * 6.5
        cy = 115 + flote_y

        # 1. Sombra holográfica en la base
        sombra_escala = 1.0 - (flote_y / 40.0)
        sw = 52 * sombra_escala
        self.canvas.create_oval(
            cx - sw, 198, cx + sw, 208,
            fill="#0A121E", outline=neon, width=1
        )

        # 2. Aura exterior pulsante
        pulso = math.sin(self.tiempo * 3.5) * 4
        r_aura = 74 + pulso
        self.canvas.create_oval(
            cx - r_aura, cy - r_aura, cx + r_aura, cy + r_aura,
            outline=sec, width=1, dash=(4, 4)
        )

        # 3. Propulsor inferior luminoso
        llama_h = 10 + abs(math.sin(self.tiempo * 12)) * 7
        self.canvas.create_polygon(
            cx - 16, cy + 56,
            cx + 16, cy + 56,
            cx, cy + 56 + llama_h,
            fill=neon, outline=""
        )

        # 4. Antenas / Orejas Cyber-Tácticas laterales
        inclinacion = -6 if self.emocion == "feliz" else (8 if self.emocion == "cansado" else 0)
        # Izquierda
        self.canvas.create_polygon(
            cx - 58, cy - 18,
            cx - 76, cy - 46 + inclinacion,
            cx - 42, cy - 42,
            fill=chasis, outline=neon, width=2
        )
        # Derecha
        self.canvas.create_polygon(
            cx + 58, cy - 18,
            cx + 76, cy - 46 + inclinacion,
            cx + 42, cy - 42,
            fill=chasis, outline=neon, width=2
        )

        # 5. Antena superior con nodo energético
        self.canvas.create_line(cx, cy - 58, cx, cy - 82, fill=neon, width=2.5)
        self.canvas.create_oval(cx - 6, cy - 90, cx + 6, cy - 78, fill=neon, outline="#FFFFFF", width=1)

        # 6. Casco / Cuerpo principal (Hexágono suavizado / Cápsula)
        self.canvas.create_oval(
            cx - 64, cy - 58, cx + 64, cy + 58,
            fill=chasis, outline=neon, width=2.5
        )
        # Detalle lateral de auriculares
        self.canvas.create_rectangle(cx - 70, cy - 14, cx - 60, cy + 16, fill=sec, outline=neon, width=1.5)
        self.canvas.create_rectangle(cx + 60, cy - 14, cx + 70, cy + 16, fill=sec, outline=neon, width=1.5)

        # 7. Visor LED Frontal
        self.canvas.create_oval(
            cx - 50, cy - 36, cx + 50, cy + 36,
            fill=visor_bg, outline=sec, width=2
        )
        # Reflejo cristal en esquina superior izquierda del visor
        self.canvas.create_arc(
            cx - 42, cy - 28, cx + 10, cy + 10,
            start=110, extent=55, style=tk.ARC, outline="#FFFFFF", width=1.5
        )

        # 8. Ojos LED Expresivos (con seguimiento del ratón)
        dx, dy = self.calcular_mirada(cx, cy)
        ojo_izq_x = cx - 20 + dx
        ojo_der_x = cx + 20 + dx
        ojo_y = cy - 4 + dy

        if self.parpadeo or self.emocion == "cansado":
            # Líneas horizontales cerradas / relajadas
            self.canvas.create_line(ojo_izq_x - 10, ojo_y, ojo_izq_x + 10, ojo_y, fill=neon, width=3, capstyle=tk.ROUND)
            self.canvas.create_line(ojo_der_x - 10, ojo_y, ojo_der_x + 10, ojo_y, fill=neon, width=3, capstyle=tk.ROUND)
        elif self.emocion == "feliz":
            # Arcos LED sonrientes (^ ^)
            self.canvas.create_arc(ojo_izq_x - 11, ojo_y - 8, ojo_izq_x + 11, ojo_y + 10, start=0, extent=180, style=tk.ARC, outline=neon, width=3.5)
            self.canvas.create_arc(ojo_der_x - 11, ojo_y - 8, ojo_der_x + 11, ojo_y + 10, start=0, extent=180, style=tk.ARC, outline=neon, width=3.5)
        elif self.emocion == "sorprendido":
            # Ojos LED grandes con núcleo brillante
            self.canvas.create_oval(ojo_izq_x - 11, ojo_y - 11, ojo_izq_x + 11, ojo_y + 11, outline=neon, width=3)
            self.canvas.create_oval(ojo_izq_x - 4, ojo_y - 4, ojo_izq_x + 4, ojo_y + 4, fill="#FFFFFF", outline="")
            self.canvas.create_oval(ojo_der_x - 11, ojo_y - 11, ojo_der_x + 11, ojo_y + 11, outline=neon, width=3)
            self.canvas.create_oval(ojo_der_x - 4, ojo_y - 4, ojo_der_x + 4, ojo_y + 4, fill="#FFFFFF", outline="")
        elif self.emocion == "pensando":
            # Un ojo enfocado y otro escaneando
            self.canvas.create_oval(ojo_izq_x - 8, ojo_y - 8, ojo_izq_x + 8, ojo_y + 8, fill=neon, outline="")
            self.canvas.create_rectangle(ojo_der_x - 10, ojo_y - 3, ojo_der_x + 10, ojo_y + 3, fill=neon, outline="")
        else:
            # Neutral: Ojos digitales redondeados con brillo
            self.canvas.create_oval(ojo_izq_x - 9, ojo_y - 11, ojo_izq_x + 9, ojo_y + 11, fill=neon, outline="")
            self.canvas.create_oval(ojo_izq_x - 3, ojo_y - 6, ojo_izq_x + 2, ojo_y - 1, fill="#FFFFFF", outline="")
            self.canvas.create_oval(ojo_der_x - 9, ojo_y - 11, ojo_der_x + 9, ojo_y + 11, fill=neon, outline="")
            self.canvas.create_oval(ojo_der_x - 3, ojo_y - 6, ojo_der_x + 2, ojo_y - 1, fill="#FFFFFF", outline="")

        # Mejillas holográficas en estado feliz
        if self.emocion == "feliz":
            self.canvas.create_oval(cx - 38, cy + 8, cx - 26, cy + 14, fill=sec, outline="")
            self.canvas.create_oval(cx + 26, cy + 8, cx + 38, cy + 14, fill=sec, outline="")

        # 9. Boca / Ecualizador de voz LED
        boca_y = cy + 18 + dy * 0.5
        if self.hablando:
            # Barras de ecualizador animadas al hablar
            for i, offset_x in enumerate([-12, -6, 0, 6, 12]):
                amp = abs(math.sin(self.tiempo * 18 + i * 1.3)) * 8 + 2
                self.canvas.create_line(
                    cx + offset_x, boca_y - amp,
                    cx + offset_x, boca_y + amp,
                    fill=neon, width=2.5, capstyle=tk.ROUND
                )
        elif self.emocion == "feliz":
            self.canvas.create_arc(cx - 12, boca_y - 6, cx + 12, boca_y + 8, start=190, extent=160, style=tk.ARC, outline=neon, width=2.5)
        elif self.emocion == "sorprendido":
            self.canvas.create_oval(cx - 6, boca_y - 5, cx + 6, boca_y + 7, outline=neon, width=2.5)
        else:
            self.canvas.create_line(cx - 10, boca_y, cx + 10, boca_y, fill=neon, width=2.5, capstyle=tk.ROUND)

        # 10. Partículas orbitales cuando está pensando
        if self.emocion == "pensando":
            for i in range(3):
                ang = self.tiempo * 4 + (i * 2.09)
                px = cx + math.cos(ang) * 84
                py = cy + math.sin(ang) * 28
                self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill=neon, outline="#FFFFFF", width=1)

    def animar(self):
        self.tiempo += 0.05
        ahora = time.time()

        # Lógica de parpadeo natural
        if not self.parpadeo and ahora >= self.proximo_parpadeo:
            self.parpadeo = True
            self.fin_parpadeo = ahora + 0.14
        elif self.parpadeo and ahora >= self.fin_parpadeo:
            self.parpadeo = False
            self.proximo_parpadeo = ahora + random.uniform(2.5, 5.5)

        self.dibujar_robot()
        self.root.after(33, self.animar)

    def aplicar_tema_hud(self, emocion, estado_custom=None):
        tema = TEMAS_EMOCION.get(emocion, TEMAS_EMOCION["neutral"])
        self.hud_frame.configure(highlightbackground=tema["neon"])
        self.lbl_estado.configure(
            text=estado_custom or tema["estado"],
            fg=tema["neon"]
        )
        self.btn_enviar.configure(bg=tema["neon"])

    def enviar_mensaje(self, event=None):
        mensaje = self.entry.get().strip()
        if not mensaje:
            return

        self.entry.delete(0, tk.END)
        self.emocion = "pensando"
        self.aplicar_tema_hud("pensando")
        self.lbl_texto.configure(text="Procesando solicitud en el núcleo local...")

        hilo = threading.Thread(target=self.consultar_n8n, args=(mensaje,), daemon=True)
        hilo.start()

    def consultar_n8n(self, mensaje):
        try:
            payload = {"mensaje": mensaje, "sessionId": SESSION_ID}
            resp = requests.post(WEBHOOK_URL, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            texto = data.get("texto", "Listo.")
            emocion = data.get("emocion", "feliz").lower()
            if emocion not in TEMAS_EMOCION:
                emocion = "feliz"

            self.root.after(0, lambda: self.mostrar_respuesta(texto, emocion, hablar=True))
        except Exception as e:
            err_msg = f"Error de enlace con n8n: {str(e)[:60]}"
            self.root.after(0, lambda: self.mostrar_respuesta(err_msg, "sorprendido", hablar=False))

    def mostrar_respuesta(self, texto, emocion, hablar=True):
        self.emocion = emocion
        self.lbl_texto.configure(text=texto)
        self.aplicar_tema_hud(emocion)

        if hablar and self.voz_activa:
            threading.Thread(target=self.hablar_texto, args=(texto,), daemon=True).start()

    def hablar_texto(self, texto):
        self.hablando = True
        self.root.after(0, lambda: self.aplicar_tema_hud(self.emocion, "🔊 HABLANDO"))
        try:
            texto_limpio = texto.replace('"', "'").replace("\n", " ")
            cmd = (
                f'Add-Type -AssemblyName System.Speech; '
                f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                f'$s.Rate = 1; '
                f'$s.Speak("{texto_limpio}")'
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass
        finally:
            self.hablando = False
            self.root.after(0, lambda: self.aplicar_tema_hud(self.emocion))


if __name__ == "__main__":
    root = tk.Tk()
    app = JollyCyberPet(root)
    root.mainloop()