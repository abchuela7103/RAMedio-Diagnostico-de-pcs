import tkinter as tk
from tkinter import ttk, messagebox
import threading
from collector import collect_metrics
from sender import send_metrics
import time
import json
from datetime import datetime, UTC 
import socket
import webbrowser
import requests

# Identificador del equipo
device_id = socket.gethostname()

# Archivo donde guardaremos los datos recolectados del agente
LOG_FILE = "metrics_log.jsonl"

# --- Colores basados en el CSS web ---
BG_COLOR = "#0f172a"
PANEL_COLOR = "#1e293b"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"
BTN_PRIMARY = "#3b82f6"
BTN_PRIMARY_HOVER = "#2563eb"
BTN_ACCENT = "#8b5cf6"
BTN_ACCENT_HOVER = "#7c3aed"
SUCCESS_COLOR = "#10b981"
ERROR_COLOR = "#ef4444"
# -------------------------------------

def recolectar_metricas(app):
    app.btn_iniciar.config(state=tk.DISABLED, bg="#334155", fg=TEXT_MUTED)
    app.btn_iniciar.unbind("<Enter>")
    app.btn_iniciar.unbind("<Leave>")
    
    app.lbl_estado.config(text="Recolectando métricas... Por favor espera.", fg=TEXT_MAIN)
    app.progress.config(value=0)
    
    # Mostrar el botón Web Inmediatamente - Flujo de Sistemas Distribuidos
    app.root.after(0, lambda: app.btn_formulario.pack(pady=15))
    
    # Ejecutamos la recolección en un hilo separado
    def tarea():
        try:
            metrics_history = {"cpu": [], "ram": [], "disk": [], "disk_active": [], "gpu": [], "battery_pct": [], "battery_plug": []}
            
            for i in range(5):
                app.root.after(0, lambda i=i: app.lbl_estado.config(text=f"Recolectando métricas... Muestra {i+1} de 5"))
                # Subir progreso justo antes de tomar la muestra, o después de un tramo, en incrementos de 20
                
                data = collect_metrics()
                
                metrics_history["cpu"].append(data.get("cpu", 0.0) or 0.0)
                metrics_history["ram"].append(data.get("ram", 0.0) or 0.0)
                metrics_history["disk"].append(data.get("disk", 0.0) or 0.0)
                metrics_history["disk_active"].append(data.get("disk_active", 0.0) or 0.0)
                metrics_history["gpu"].append(data.get("gpu", 0.0) or 0.0)
                
                bat = data.get("battery")
                if bat:
                    metrics_history["battery_pct"].append(bat.get("percent", 0.0) or 0.0)
                    metrics_history["battery_plug"].append(bat.get("power_plugged", False))
                
                # Actualizar barra de progreso al terminar la muestra actual
                app.root.after(0, lambda i=i: app.progress.config(value=(i+1)*20))
                time.sleep(1.5)

            # Promedios
            avg_data = {
                "cpu": round(sum(metrics_history["cpu"]) / 5, 2),
                "ram": round(sum(metrics_history["ram"]) / 5, 2),
                "disk": round(sum(metrics_history["disk"]) / 5, 2),
                "disk_active": round(sum(metrics_history["disk_active"]) / 5, 2),
                "gpu": round(sum(metrics_history["gpu"]) / 5, 2),
                "battery": None
            }
            
            if metrics_history["battery_pct"]:
                avg_data["battery"] = {
                    "percent": round(sum(metrics_history["battery_pct"]) / len(metrics_history["battery_pct"]), 2),
                    "power_plugged": metrics_history["battery_plug"][-1]
                }

            payload = {
                "device_id": device_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "metrics": avg_data
            }

            # Guardar en archivo (modo append)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
            
            # Enviar al servidor
            app.root.after(0, lambda: app.lbl_estado.config(text="Enviando métricas al servidor..."))
            send_metrics(payload)
            
            # Finalizado con exito
            app.root.after(0, lambda data=avg_data: app.finalizar_exito(data))

        except Exception as e:
            app.root.after(0, lambda e=e: app.mostrar_error(e))

    threading.Thread(target=tarea, daemon=True).start()


class LoginDialog:
    def __init__(self, parent, on_success):
        self.top = tk.Toplevel(parent)
        self.top.title("Iniciar Sesión - RAMedio")
        self.top.geometry("400x500")
        self.top.resizable(False, False)
        self.top.configure(bg=BG_COLOR)
        
        # Center the window
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.top.winfo_screenheight() // 2) - (500 // 2)
        self.top.geometry(f"+{x}+{y}")
        
        self.on_success = on_success
        self.token = None
        self.username = None
        
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # UI Elements
        tk.Label(self.top, text="RAMedio Login", font=("Helvetica", 18, "bold"), bg=BG_COLOR, fg=TEXT_MAIN).pack(pady=(40, 30))
        
        tk.Label(self.top, text="Usuario:", bg=BG_COLOR, fg=TEXT_MAIN, font=("Helvetica", 11)).pack()
        self.ent_user = tk.Entry(self.top, font=("Helvetica", 12), justify="center")
        self.ent_user.pack(pady=5)
        
        tk.Label(self.top, text="Contraseña:", bg=BG_COLOR, fg=TEXT_MAIN, font=("Helvetica", 11)).pack(pady=(10,0))
        self.ent_pass = tk.Entry(self.top, font=("Helvetica", 12), show="*", justify="center")
        self.ent_pass.pack(pady=5)
        
        self.btn_login = tk.Button(self.top, text="Iniciar Sesión", bg=BTN_PRIMARY, fg="white", font=("Helvetica", 12, "bold"), command=self.login, padx=30, pady=8, bd=0, cursor="hand2")
        self.btn_login.pack(pady=(30, 10))
        
        self.btn_register = tk.Button(self.top, text="Registrarse", bg=PANEL_COLOR, fg=TEXT_MAIN, font=("Helvetica", 10), command=self.register, padx=20, pady=5, bd=0, cursor="hand2")
        self.btn_register.pack()

    def on_close(self):
        self.top.destroy()
        
    def login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Error", "Llenar todos los campos", parent=self.top)
            return
        try:
            r = requests.post("http://40.233.30.180/api/login", json={"username": user, "password": pwd})
            if r.status_code == 200:
                data = r.json()
                self.token = data.get("token")
                self.username = data.get("username")
                self.top.destroy()
                self.on_success(self.token, self.username)
            else:
                messagebox.showerror("Error", r.json().get("detail", "Error de login"), parent=self.top)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al conectar: {e}", parent=self.top)

    def register(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Error", "Llenar todos los campos", parent=self.top)
            return
        try:
            r = requests.post("http://40.233.30.180/api/register", json={"username": user, "password": pwd})
            if r.status_code == 200:
                messagebox.showinfo("Éxito", "Registrado exitosamente. Ahora puedes iniciar sesión.", parent=self.top)
            else:
                messagebox.showerror("Error", r.json().get("detail", "Error de registro"), parent=self.top)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al conectar: {e}", parent=self.top)

class AgenteApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Ocultar ventana principal momentáneamente
        
        self.auth_token = None
        self.username = None
        self.acepto_terminos = False

        # Primero mostramos el Login
        self.mostrar_login()

    def mostrar_login(self):
        def on_login_success(token, username):
            self.auth_token = token
            self.username = username
            
            # Intentar vincular este device_id al usuario (silenciosamente)
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                requests.post("http://40.233.30.180/api/devices/link", json={"device_id": device_id}, headers=headers)
            except Exception:
                pass # Continue even if link fails

            self.pedir_autorizacion()

        LoginDialog(self.root, on_login_success)

    def pedir_autorizacion(self):
        # --- VENTANA DE DIÁLOGO PREVIA ---
        dialog = tk.Toplevel(self.root)
        dialog.title("Autorización RAMedio")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        # Centrar la ventana en la pantalla (aproximado)
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Si el usuario cierra el popup en la 'X', destruimos toda la aplicación
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
        
        tk.Label(
            dialog, 
            text="Para ejecutar el agente RAMedio necesitamos de tu autorización para la recolección de métricas.", 
            font=("Helvetica", 11), wraplength=400, justify="center"
        ).pack(pady=20)
        
        var_terminos = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(dialog, text="Acepto los términos y condiciones de privacidad", variable=var_terminos, font=("Helvetica", 10))
        chk.pack(pady=5)
        
        def mostrar_detalles():
            aviso_privacidad = (
                "AVISO DE PRIVACIDAD Y TÉRMINOS DE USO\n\n"
                "Para funcionar correctamente, el Agente RAMedio necesita recolectar métricas de rendimiento "
                "de hardware de tu computadora (porcentajes de uso de CPU, RAM, Disco Activo, GPU y estado de batería).\n\n"
                "Estos datos serán enviados de forma temporal a nuestros algoritmos en la nube para generar un diagnóstico "
                "inteligente automatizado.\n\n"
                "Tu privacidad es prioridad: NO recolectamos archivos personales, documentos, contraseñas, "
                "registros de teclado ni historial de navegación web; la extracción de datos es estrictamente instrumental."
            )
            messagebox.showinfo("Aviso de Privacidad - Detalles", aviso_privacidad, parent=dialog)
            
        btn_detalles = tk.Button(dialog, text="Ver más detalles", command=mostrar_detalles, fg="#2563eb", cursor="hand2", relief=tk.FLAT, font=("Helvetica", 9, "underline"))
        btn_detalles.pack(pady=5)
        
        def continuar():
            if not var_terminos.get():
                messagebox.showwarning("Atención", "Por favor, seleccione la casilla de aceptación para poder usar el agente.", parent=dialog)
            else:
                self.acepto_terminos = True
                dialog.destroy()
                
        btn_continuar = tk.Button(dialog, text="Continuar", command=continuar, bg="#3b82f6", fg="white", font=("Helvetica", 10, "bold"), padx=20, pady=5)
        btn_continuar.pack(pady=15)
        
        # Pausar la ejecución aquí hasta que la ventana secundaria 'dialog' se destruya
        self.root.wait_window(dialog)
        
        # Si la ventana se destruyó y no aceptó (ej. clickeó la X de cerrar), abortamos
        if not self.acepto_terminos:
            self.root.destroy()
            return
            
        self.root.deiconify() # Mostrar la ventana principal de nuevo
        # ---------------------------------
        
        self.root.title("RAMedio - Agente de Diagnóstico")
        
        # Tamaño de ventana (no fullscreen pero grande)
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_COLOR)

        # Por seguridad y UX, permitir salir con Escape
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Fondo animado
        self.bg_canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)

        # Crear orbes animados en el fondo
        self.orbs = []
        self.crear_orbes()

        # Main Panel
        self.panel = tk.Frame(self.bg_canvas, bg=PANEL_COLOR, bd=0, highlightthickness=2, highlightbackground=BTN_PRIMARY)
        self.panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=450)
        
        self.root.title("RAMedio - Agente de Diagnóstico")
        
        # Tamaño de ventana (no fullscreen pero grande)
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_COLOR)

        # Por seguridad y UX, permitir salir con Escape
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Fondo animado
        self.bg_canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)

        # Crear orbes animados en el fondo
        self.orbs = []
        self.crear_orbes()

        # Main Panel
        self.panel = tk.Frame(self.bg_canvas, bg=PANEL_COLOR, bd=0, highlightthickness=2, highlightbackground=BTN_PRIMARY)
        self.panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=450)

        # Título formales como en main
        lbl_titulo = tk.Label(self.panel, text=f"RAMedio - Bienvenido, {self.username}", font=("Helvetica", 20, "bold"), bg=PANEL_COLOR, fg=TEXT_MAIN)
        lbl_titulo.pack(pady=(40, 10))

        # ID de equipo formal
        lbl_device = tk.Label(self.panel, text=f"Equipo: {device_id}", font=("Helvetica", 12), bg=PANEL_COLOR, fg=TEXT_MUTED)
        lbl_device.pack(pady=(0, 25))

        # Estado formal
        self.lbl_estado = tk.Label(self.panel, text="¿Qué deseas hacer a continuación?", font=("Helvetica", 13), bg=PANEL_COLOR, fg=TEXT_MAIN)
        self.lbl_estado.pack(pady=(0, 25))

        # Progress bar configuration
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", thickness=15, background=BTN_PRIMARY, troughcolor=BG_COLOR, bordercolor=PANEL_COLOR, lightcolor=BTN_PRIMARY, darkcolor=BTN_PRIMARY)
        
        self.progress = ttk.Progressbar(self.panel, mode="determinate", length=500, style="TProgressbar", maximum=100)
        self.progress.pack(pady=(0, 40))
        self.progress.config(value=0)

        # Frame contenedor de botones
        self.btn_frame = tk.Frame(self.panel, bg=PANEL_COLOR)
        self.btn_frame.pack()

        # Botón Iniciar formal
        self.btn_iniciar = tk.Button(
            self.btn_frame, text="Ejecutar Agente", 
            font=("Helvetica", 12, "bold"), bg=BTN_PRIMARY, fg="white", 
            activebackground=BTN_PRIMARY_HOVER, activeforeground="white",
            relief=tk.FLAT, cursor="hand2", padx=30, pady=15, bd=0,
            command=lambda: recolectar_metricas(self)
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)

        # Botón Ir al formulario formal (renombrado a Ver Historial)
        self.btn_formulario = tk.Button(
            self.btn_frame, text="Ver Historial", 
            font=("Helvetica", 12, "bold"), bg=BTN_ACCENT, fg="white", 
            activebackground=BTN_ACCENT_HOVER, activeforeground="white",
            relief=tk.FLAT, cursor="hand2", padx=30, pady=15, bd=0,
            command=self.abrir_formulario
        )
        self.btn_formulario.pack(side=tk.LEFT, padx=10)

        # Custom Hover effects
        self.bind_hovers(self.btn_iniciar, BTN_PRIMARY, BTN_PRIMARY_HOVER)
        self.bind_hovers(self.btn_formulario, BTN_ACCENT, BTN_ACCENT_HOVER)
        
        # Iniciar animación
        self.animar_fondo()

    def crear_orbes(self):
        import random
        colores = ["#1e3a8a", "#312e81", "#4c1d95", "#2563eb", "#1e1b4b"]
        for _ in range(8):
            r = random.randint(50, 200)
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            dx = random.choice([-2, -1, 1, 2])
            dy = random.choice([-2, -1, 1, 2])
            color = random.choice(colores)
            
            orb = self.bg_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="", stipple="gray50")
            self.orbs.append([orb, dx, dy])

    def animar_fondo(self):
        for orb_data in self.orbs:
            orb, dx, dy = orb_data
            self.bg_canvas.move(orb, dx, dy)
            coords = self.bg_canvas.coords(orb)
            if not coords:
                continue
            x1, y1, x2, y2 = coords
            
            if x1 < -300 or x2 > 2500:
                orb_data[1] = -dx
            if y1 < -300 or y2 > 1500:
                orb_data[2] = -dy
                
        self.root.after(40, self.animar_fondo)

    def bind_hovers(self, widget, color_normal, color_hover):
        widget.bind("<Enter>", lambda e: widget.config(bg=color_hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=color_normal))

    def finalizar_exito(self, metricas):
        self.progress.config(value=100)
        self.lbl_estado.config(text="¡Métricas enviadas correctamente!", fg=SUCCESS_COLOR)
        
        # Formatear texto de métricas
        bat = metricas.get('battery')
        if bat:
            bateria_texto = f"{bat['percent']}% ({'Conectado' if bat['power_plugged'] else 'Desconectado'})"
        else:
            bateria_texto = "No disponible"
            
        texto_metricas = (
            f"📊 CPU: {metricas['cpu']}%\n"
            f"🧠 RAM: {metricas['ram']}%\n"
            f"💾 Disco: {metricas['disk']}% (Uso Activo: {metricas['disk_active']}%)\n"
            f"🎮 GPU: {metricas['gpu']}%\n"
            f"🔋 Batería: {bateria_texto}"
        )

        lbl_metricas = tk.Label(
            self.panel, text=texto_metricas, font=("Helvetica", 11, "bold"), 
            bg=BG_COLOR, fg=TEXT_MAIN, justify=tk.CENTER, padx=15, pady=8
        )
        lbl_metricas.pack(before=self.btn_frame, pady=(0, 20))
        
        self.btn_iniciar.pack_forget() 
        self.btn_formulario.pack(pady=0) 

    def mostrar_error(self, e):
        self.lbl_estado.config(text="Error durante la recolección.", fg=ERROR_COLOR)
        self.btn_iniciar.config(state=tk.NORMAL, bg=BTN_PRIMARY, fg="white")
        self.bind_hovers(self.btn_iniciar, BTN_PRIMARY, BTN_PRIMARY_HOVER)
        messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

    def abrir_formulario(self):
        # Envía el token al navegador para que éste auto inicie sesión si lo soporta.
        # En caso de que no tenga sesión web, lo iniciará con el token.
        url_formulario = f"http://40.233.30.180/?device_id={device_id}&token={self.auth_token}"
        webbrowser.open(url_formulario)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgenteApp(root)
    root.mainloop()
