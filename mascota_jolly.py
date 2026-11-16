import tkinter as tk
import threading
import json
import urllib.request
import random
import subprocess

# --- CONFIGURACIÓN ---
N8N_WEBHOOK_URL = "http://localhost:6789/webhook/jolly"
COLOR_CHROMA = "#010101"


class MascotaTkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("Jolly")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=COLOR_CHROMA)
        self.root.wm_attributes("-transparentcolor", COLOR_CHROMA)

        # Estado del personaje
        self.emocion = "feliz"
        self.emocion_previa = "feliz"
        self.parpadeando = False
        self.acariciando = False
        self.voz_activa = True
        self.offset_y = 0
        self.direccion = 1
        self.drag_x = 0
        self.drag_y = 0
        self.ultimo_mensaje_usuario = ""
        self.chat_visible = True

        # Posición inicial en esquina inferior derecha
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        self.root.geometry(f"310x380+{ancho_pantalla - 340}+{alto_pantalla - 440}")

        # --- GLOBO DE DIÁLOGO ESTILIZADO ---
        self.globo = tk.Label(
            self.root,
            text="¡Hola! Ya tengo nuevo look y voz. Escríbeme algo abajo.",
            wraplength=250,
            justify="left",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#f8fafc",
            padx=14,
            pady=10,
            bd=1,
            relief="solid"
        )
        self.globo.pack(pady=(5, 2))

        # --- LIENZO DEL AVATAR (180x180) ---
        self.canvas = tk.Canvas(
            self.root,
            width=180,
            height=180,
            bg=COLOR_CHROMA,
            highlightthickness=0
        )
        self.canvas.pack()

        # Eventos de arrastre y caricias
        for widget in (self.canvas, self.globo):
            widget.bind("<Button-1>", self.iniciar_arrastre)
            widget.bind("<B1-Motion>", self.mover_ventana)
            widget.bind("<Button-3>", self.mostrar_menu)

        self.canvas.bind("<Enter>", self.al_entrar_mouse)
        self.canvas.bind("<Leave>", self.al_salir_mouse)

        # --- CAJA DE TEXTO ---
        self.entrada = tk.Entry(
            self.root,
            font=("Segoe UI", 10),
            bg="#1e293b",
            fg="#ffffff",
            insertbackground="#38bdf8",
            relief="flat",
            width=30
        )
        self.entrada.pack(pady=(4, 10), ipady=6)
        self.entrada.bind("<Return>", self.enviar_mensaje)
        self.entrada.focus_set()

        # --- MENÚ CONTEXTUAL (CLIC DERECHO) ---
        self.menu = tk.Menu(
            self.root, tearoff=0, bg="#0f172a", fg="#f8fafc",
            activebackground="#38bdf8", activeforeground="#0f172a"
        )
        self.menu.add_command(label="💬 Ocultar / Mostrar chat", command=self.alternar_chat)
        self.menu.add_command(label="🔊 Silenciar / Activar voz", command=self.alternar_voz)
        self.menu.add_command(label="✨ Cambiar ánimo (Probar)", command=self.ciclar_emocion)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Cerrar a Jolly", command=self.root.destroy)

        # Iniciar bucles de animación y parpadeo
        self.animar()
        self.programar_parpadeo()

    def mostrar_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def alternar_voz(self):
        self.voz_activa = not self.voz_activa
        estado = "activada" if self.voz_activa else "silenciada"
        self.globo.config(text=f"Voz {estado}.")

    def alternar_chat(self):
        if self.chat_visible:
            self.entrada.pack_forget()
            self.globo.pack_forget()
            self.chat_visible = False
        else:
            self.globo.pack(before=self.canvas, pady=(5, 2))
            self.entrada.pack(after=self.canvas, pady=(4, 10), ipady=6)
            self.entrada.focus_set()
            self.chat_visible = True

    def ciclar_emocion(self):
        lista = ["feliz", "pensando", "sorprendido", "cansado", "neutral"]
        idx = (lista.index(self.emocion) + 1) % len(lista) if self.emocion in lista else 0
        self.emocion = lista[idx]
        self.globo.config(text=f"Modo de prueba: {self.emocion.upper()}")

    def al_entrar_mouse(self, event):
        if self.emocion != "pensando":
            self.emocion_previa = self.emocion
            self.acariciando = True

    def al_salir_mouse(self, event):
        self.acariciando = False

    def iniciar_arrastre(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def mover_ventana(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")

    def programar_parpadeo(self):
        espera = random.randint(2500, 5000)
        self.root.after(espera, self.ejecutar_parpadeo)

    def ejecutar_parpadeo(self):
        self.parpadeando = True
        self.root.after(140, self.terminar_parpadeo)

    def terminar_parpadeo(self):
        self.parpadeando = False
        self.programar_parpadeo()

    def dibujar_avatar(self):
        self.canvas.delete("all")

        paleta = {
            "feliz": ("#38bdf8", "#0284c7", "#7dd3fc"),
            "pensando": ("#a855f7", "#7e22ce", "#d8b4fe"),
            "sorprendido": ("#f59e0b", "#b45309", "#fde68a"),
            "cansado": ("#64748b", "#334155", "#94a3b8"),
            "neutral": ("#10b981", "#047857", "#6ee7b7")
        }
        estado_actual = "feliz" if self.acariciando else self.emocion
        color_principal, color_sombra, color_brillo = paleta.get(estado_actual, paleta["neutral"])

        y = 32 + self.offset_y

        # 1. Sombra flotante en el suelo
        escala_sombra = int(self.offset_y * 1.2)
        self.canvas.create_oval(
            52 + escala_sombra, 162, 128 - escala_sombra, 174,
            fill="#1e293b", outline=""
        )

        # 2. Antena superior articulada
        punta_x = 90 + (self.offset_y * 0.8)
        self.canvas.create_line(90, y + 4, punta_x, y - 16, fill="#cbd5e1", width=3, capstyle="round")
        self.canvas.create_oval(punta_x - 6, y - 22, punta_x + 6, y - 10, fill=color_principal, outline="#ffffff", width=2)

        # 3. Auriculares / Orejas laterales
        self.canvas.create_oval(24, y + 36, 44, y + 72, fill=color_sombra, outline="#ffffff", width=2)
        self.canvas.create_oval(136, y + 36, 156, y + 72, fill=color_sombra, outline="#ffffff", width=2)

        # 4. Manitas flotantes laterales
        mano_y = y + 78 - (self.offset_y * 0.6)
        self.canvas.create_oval(20, mano_y, 36, mano_y + 18, fill="#f8fafc", outline=color_principal, width=2)
        self.canvas.create_oval(144, mano_y, 160, mano_y + 18, fill="#f8fafc", outline=color_principal, width=2)

        # 5. Cabeza / Cuerpo principal
        self.canvas.create_oval(34, y, 146, y + 108, fill="#f8fafc", outline=color_principal, width=4)
        self.canvas.create_oval(39, y + 5, 141, y + 103, fill="#e2e8f0", outline="")

        # 6. Visor facial oscuro
        self.canvas.create_oval(46, y + 24, 134, y + 84, fill="#0f172a", outline=color_sombra, width=2)
        self.canvas.create_arc(56, y + 28, 124, y + 50, start=20, extent=140, style="arc", outline="#334155", width=2)

        # 7. Mejillas sonrojadas
        if estado_actual == "feliz" or self.acariciando:
            self.canvas.create_oval(52, y + 58, 66, y + 66, fill="#f43f5e", outline="")
            self.canvas.create_oval(114, y + 58, 128, y + 66, fill="#f43f5e", outline="")

        # 8. Ojos expresivos + Parpadeo
        if self.parpadeando and estado_actual != "pensando":
            self.canvas.create_line(58, y + 50, 78, y + 50, fill=color_brillo, width=3, capstyle="round")
            self.canvas.create_line(102, y + 50, 122, y + 50, fill=color_brillo, width=3, capstyle="round")
        elif estado_actual == "feliz":
            self.canvas.create_arc(58, y + 38, 80, y + 60, start=0, extent=180, style="arc", outline=color_brillo, width=4)
            self.canvas.create_arc(100, y + 38, 122, y + 60, start=0, extent=180, style="arc", outline=color_brillo, width=4)
            self.canvas.create_arc(82, y + 56, 98, y + 68, start=190, extent=160, style="arc", outline=color_brillo, width=3)
        elif estado_actual == "sorprendido":
            self.canvas.create_oval(60, y + 36, 78, y + 58, fill=color_brillo, outline="")
            self.canvas.create_oval(102, y + 36, 120, y + 58, fill=color_brillo, outline="")
            self.canvas.create_oval(85, y + 62, 95, y + 72, outline=color_brillo, width=2)
        elif estado_actual == "pensando":
            self.canvas.create_line(58, y + 48, 78, y + 48, fill=color_brillo, width=4, capstyle="round")
            self.canvas.create_oval(104, y + 34, 120, y + 50, fill=color_brillo, outline="")
            self.canvas.create_oval(108, y + 37, 113, y + 42, fill="#ffffff", outline="")
        elif estado_actual == "cansado":
            self.canvas.create_line(58, y + 46, 78, y + 52, fill=color_brillo, width=4, capstyle="round")
            self.canvas.create_line(102, y + 52, 122, y + 46, fill=color_brillo, width=4, capstyle="round")
        else:
            self.canvas.create_oval(61, y + 38, 77, y + 58, fill=color_brillo, outline="")
            self.canvas.create_oval(103, y + 38, 119, y + 58, fill=color_brillo, outline="")
            self.canvas.create_oval(65, y + 41, 70, y + 46, fill="#ffffff", outline="")
            self.canvas.create_oval(107, y + 41, 112, y + 46, fill="#ffffff", outline="")

    def animar(self):
        limite = 7 if (self.emocion in ("feliz", "sorprendido") or self.acariciando) else 3
        self.offset_y += self.direccion
        if abs(self.offset_y) >= limite:
            self.direccion *= -1
        self.dibujar_avatar()
        self.root.after(55, self.animar)

    def enviar_mensaje(self, event=None):
        texto_usuario = self.entrada.get().strip()
        if not texto_usuario:
            return

        self.ultimo_mensaje_usuario = texto_usuario
        self.entrada.delete(0, tk.END)
        self.entrada.config(state="disabled")
        self.emocion = "pensando"
        self.globo.config(text="Pensando...")

        threading.Thread(target=self.consultar_cerebro, daemon=True).start()

    def consultar_cerebro(self):
        payload = {"mensaje": self.ultimo_mensaje_usuario}
        try:
            req = urllib.request.Request(
                N8N_WEBHOOK_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as res:
                contenido = json.loads(res.read().decode("utf-8"))
                texto = contenido.get("texto", "...")
                emocion = contenido.get("emocion", "neutral").lower()
        except Exception as e:
            texto = f"Error con n8n: {e}"
            emocion = "cansado"

        self.root.after(0, self.actualizar_ui, texto, emocion)

    def hablar(self, texto):
        if not self.voz_activa:
            return

        def _ejecutar_voz():
            texto_limpio = texto.replace('"', '').replace("'", "").replace("\n", " ")
            comando_ps = (
                'Add-Type -AssemblyName System.Speech; '
                '$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                '$synth.Rate = 1; '
                f'$synth.Speak("{texto_limpio}");'
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", comando_ps],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        threading.Thread(target=_ejecutar_voz, daemon=True).start()

    def actualizar_ui(self, texto, emocion):
        self.globo.config(text=texto)
        self.emocion = emocion
        self.entrada.config(state="normal")
        self.entrada.focus_set()
        self.hablar(texto)


if __name__ == "__main__":
    root = tk.Tk()
    app = MascotaTkinter(root)
    root.mainloop()