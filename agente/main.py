import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
from collector import collect_metrics
from sender import send_metrics
import time
import json
from datetime import datetime, UTC 
import socket
import webbrowser
import requests

device_id = socket.gethostname()
LOG_FILE = "metrics_log.jsonl"

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") # Tema principal (blue)

# Colores exactos basados en web/styles.css del sistema web
BG_COLOR = "#0A1118"
CARD_BG = "#111C29"
PRIMARY = "#3b82f6"
ACCENT = "#00b4d8"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Iniciar Sesión - RAMedio")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Ocultar temporalmente para centrar
        self.attributes("-alpha", 0)
        self.after(200, self.center_window)
        
        self.on_success = on_success
        self.token = None
        self.username = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configurar fondo general
        self.configure(fg_color=BG_COLOR)
        
        # Tarjeta principal
        self.card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=20, border_width=1, border_color="#1e293b")
        self.card.pack(fill="both", expand=True, padx=25, pady=30)
        
        # Logo y Títulos
        lbl_logo = ctk.CTkLabel(self.card, text="🩺 RAMedio", font=("Helvetica", 28, "bold"), text_color=ACCENT)
        lbl_logo.pack(pady=(30, 5))
        
        lbl_sub = ctk.CTkLabel(self.card, text="Inicia sesión para continuar", font=("Helvetica", 13), text_color=TEXT_MUTED)
        lbl_sub.pack(pady=(0, 20))
        
        # Controles
        self.ent_user = ctk.CTkEntry(self.card, placeholder_text="Usuario", font=("Helvetica", 14), 
                                     width=250, height=45, corner_radius=10, 
                                     fg_color="#1A2635", border_color="#1e293b", text_color=TEXT_MAIN)
        self.ent_user.pack(pady=10)
        
        self.ent_pass = ctk.CTkEntry(self.card, placeholder_text="Contraseña", show="*", font=("Helvetica", 14), 
                                     width=250, height=45, corner_radius=10, 
                                     fg_color="#1A2635", border_color="#1e293b", text_color=TEXT_MAIN)
        self.ent_pass.pack(pady=10)
        
        self.btn_login = ctk.CTkButton(self.card, text="Iniciar Sesión", font=("Helvetica", 14, "bold"), 
                                       width=250, height=45, corner_radius=10, fg_color=PRIMARY, hover_color="#2563eb",
                                       command=self.login)
        self.btn_login.pack(pady=(25, 10))
        
        self.btn_register = ctk.CTkButton(self.card, text="Registrarse", font=("Helvetica", 13), 
                                          width=250, height=35, fg_color="transparent", hover_color="#1e293b", 
                                          text_color=TEXT_MUTED, command=self.register)
        self.btn_register.pack()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.attributes("-alpha", 1)

    def on_close(self):
        self.destroy()

    def login(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Error", "Llenar todos los campos", parent=self)
            return
        self.btn_login.configure(state="disabled", text="Conectando...")
        
        def run():
            try:
                r = requests.post("https://ramedio.duckdns.org/api/login", json={"username": user, "password": pwd})
                if r.status_code == 200:
                    data = r.json()
                    self.token = data.get("token")
                    self.username = data.get("username")
                    self.after(0, self.destroy)
                    self.after(0, lambda: self.on_success(self.token, self.username))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", r.json().get("detail", "Error de login"), parent=self))
                    self.after(0, lambda: self.btn_login.configure(state="normal", text="Iniciar Sesión"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Fallo al conectar: {e}", parent=self))
                self.after(0, lambda: self.btn_login.configure(state="normal", text="Iniciar Sesión"))
        threading.Thread(target=run, daemon=True).start()

    def register(self):
        user = self.ent_user.get()
        pwd = self.ent_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Error", "Llenar todos los campos", parent=self)
            return
        self.btn_register.configure(state="disabled", text="Cargando...")
        
        def run():
            try:
                r = requests.post("https://ramedio.duckdns.org/api/register", json={"username": user, "password": pwd})
                if r.status_code == 200:
                    self.after(0, lambda: messagebox.showinfo("Éxito", "Registrado exitosamente. Ahora puedes iniciar sesión.", parent=self))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", r.json().get("detail", "Error de registro"), parent=self))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Fallo al conectar: {e}", parent=self))
            finally:
                self.after(0, lambda: self.btn_register.configure(state="normal", text="Registrarse"))
        threading.Thread(target=run, daemon=True).start()


class AgenteApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.root.configure(fg_color=BG_COLOR)
        
        self.auth_token = None
        self.username = None
        self.acepto_terminos = False

        self.mostrar_login()

    def mostrar_login(self):
        def on_login_success(token, username):
            self.auth_token = token
            self.username = username
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                requests.post("https://ramedio.duckdns.org/api/devices/link", json={"device_id": device_id}, headers=headers)
            except Exception:
                pass
            self.pedir_autorizacion()

        LoginDialog(self.root, on_login_success)

    def pedir_autorizacion(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Autorización RAMedio")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        
        dialog.attributes("-alpha", 0)
        
        def center_auth():
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.attributes("-alpha", 1)
            
        dialog.after(200, center_auth)
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
        dialog.configure(fg_color=BG_COLOR)
        
        card = ctk.CTkFrame(dialog, fg_color=CARD_BG, corner_radius=20, border_width=1, border_color="#1e293b")
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(card, text="🔒 Autorización Requerida", font=("Helvetica", 18, "bold"), text_color=ACCENT).pack(pady=(20, 10))
        
        txt = ("Para ejecutar el agente RAMedio necesitamos\n"
               "de tu autorización para recolectar métricas.\n\n"
               "Tu privacidad es prioridad: NO recolectamos\n"
               "archivos, contraseñas, ni historial web.")
        ctk.CTkLabel(card, text=txt, font=("Helvetica", 13), text_color=TEXT_MUTED, justify="center").pack(pady=10)
        
        var_terminos = ctk.BooleanVar(value=False)
        chk = ctk.CTkCheckBox(card, text="Acepto los términos y condiciones", variable=var_terminos, 
                              font=("Helvetica", 13), text_color=TEXT_MAIN, fg_color=PRIMARY, border_color=PRIMARY)
        chk.pack(pady=15)
        
        def mostrar_detalles():
            aviso = ("AVISO DE PRIVACIDAD\n\n"
                     "Para funcionar correctamente, recolectamos métricas de rendimiento.\n\n"
                     "NO recolectamos archivos personales.")
            messagebox.showinfo("Privacidad", aviso, parent=dialog)
            
        ctk.CTkButton(card, text="Ver Política de Privacidad", font=("Helvetica", 13), 
                      fg_color="transparent", hover_color="#1e293b", text_color=ACCENT, command=mostrar_detalles).pack(pady=5)
        
        def continuar():
            if not var_terminos.get():
                messagebox.showwarning("Atención", "Por favor, seleccione la casilla.", parent=dialog)
            else:
                self.acepto_terminos = True
                dialog.destroy()
                
        ctk.CTkButton(card, text="Continuar", font=("Helvetica", 14, "bold"), width=200, height=45, 
                      corner_radius=10, fg_color=PRIMARY, hover_color="#2563eb", command=continuar).pack(pady=15)
        
        self.root.wait_window(dialog)
        
        if not self.acepto_terminos:
            self.root.destroy()
            return
            
        self.construir_agente_ui()
        self.root.deiconify()

    def construir_agente_ui(self):
        # Dibujar UI Principal con CustomTkinter
        self.panel = ctk.CTkFrame(self.root, fg_color=CARD_BG, corner_radius=20, border_width=1, border_color="#1e293b")
        self.panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.7, relheight=0.7)
        
        ctk.CTkLabel(self.panel, text="🩺 RAMedio", font=("Helvetica", 32, "bold"), text_color=ACCENT).pack(pady=(40, 10))
        ctk.CTkLabel(self.panel, text=f"Bienvenido, {self.username}", font=("Helvetica", 18), text_color=TEXT_MAIN).pack(pady=5)
        ctk.CTkLabel(self.panel, text=f"💻 Equipo: {device_id}", font=("Helvetica", 14), text_color=TEXT_MUTED).pack(pady=5)
        
        self.lbl_estado = ctk.CTkLabel(self.panel, text="¿Qué deseas hacer a continuación?", font=("Helvetica", 14), text_color=TEXT_MAIN)
        self.lbl_estado.pack(pady=(20, 10))
        
        self.progress = ctk.CTkProgressBar(self.panel, width=500, height=15, corner_radius=10, progress_color=ACCENT, fg_color="#1A2635")
        self.progress.set(0)
        self.progress.pack(pady=20)
        
        self.btn_frame = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.btn_frame.pack(pady=20)
        
        self.btn_iniciar = ctk.CTkButton(self.btn_frame, text="Ejecutar Agente", font=("Helvetica", 15, "bold"), 
                                         width=220, height=50, corner_radius=10, fg_color=PRIMARY, hover_color="#2563eb",
                                         command=self.ejecutar_recoleccion)
        self.btn_iniciar.pack(side="left", padx=10)
        
        self.btn_formulario = ctk.CTkButton(self.btn_frame, text="Ir a Dashboard Web", font=("Helvetica", 15, "bold"), 
                                            width=220, height=50, corner_radius=10, fg_color="transparent", 
                                            border_width=2, border_color=PRIMARY, hover_color="#1e293b", text_color=PRIMARY,
                                            command=self.abrir_formulario)
        # El botón de Dashboard se muestra una vez iniciada la ejecución
        
    def ejecutar_recoleccion(self):
        self.btn_iniciar.configure(state="disabled")
        self.lbl_estado.configure(text="Recolectando métricas... Por favor espera.", text_color=ACCENT)
        self.progress.set(0)
        self.btn_formulario.pack(side="left", padx=10)
        
        def tarea():
            try:
                metrics_history = {"cpu": [], "ram": [], "disk": [], "disk_active": [], "gpu": [], "battery_pct": [], "battery_plug": []}
                
                for i in range(5):
                    self.root.after(0, lambda i=i: self.lbl_estado.configure(text=f"Recolectando métricas... Muestra {i+1} de 5"))
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
                    self.root.after(0, lambda i=i: self.progress.set((i+1)*0.2))
                    time.sleep(1.5)

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

                payload = {"device_id": device_id, "timestamp": datetime.now(UTC).isoformat(), "metrics": avg_data}

                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload) + "\n")
                
                self.root.after(0, lambda: self.lbl_estado.configure(text="Enviando métricas al servidor..."))
                send_metrics(payload)
                self.root.after(0, lambda data=avg_data: self.finalizar_exito(data))

            except Exception as e:
                self.root.after(0, lambda e=e: self.mostrar_error(e))

        threading.Thread(target=tarea, daemon=True).start()

    def finalizar_exito(self, metricas):
        self.progress.set(1.0)
        self.lbl_estado.configure(text="✅ ¡Métricas enviadas correctamente!", text_color="#10b981")
        
        bat = metricas.get('battery')
        if bat:
            bateria_texto = f"{bat['percent']}% ({'Conectado' if bat['power_plugged'] else 'Desconectado'})"
        else:
            bateria_texto = "No disponible"
            
        texto_metricas = (
            f"⏹ CPU: {metricas['cpu']}%\n"
            f"🧠 RAM: {metricas['ram']}%\n"
            f"💾 Disco: {metricas['disk']}% (Activo: {metricas['disk_active']}%)\n"
            f"⛶ GPU: {metricas['gpu']}%\n"
            f"🔋 Batería: {bateria_texto}"
        )

        lbl_metricas = ctk.CTkLabel(self.panel, text=texto_metricas, font=("Helvetica", 14, "bold"), text_color=TEXT_MAIN, justify="center")
        lbl_metricas.pack(pady=10)
        
        self.btn_iniciar.pack_forget()

    def mostrar_error(self, e):
        self.lbl_estado.configure(text="❌ Error durante la recolección.", text_color="#ef4444")
        self.btn_iniciar.configure(state="normal")
        messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

    def abrir_formulario(self):
        url_formulario = f"https://ramedio.duckdns.org/?device_id={device_id}&token={self.auth_token}"
        webbrowser.open(url_formulario)

if __name__ == "__main__":
    import ctypes
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    
    root = ctk.CTk()
    root.title("RAMedio - Agente de Diagnóstico")
    root.geometry("1100x750")
    
    # Center window
    root.update_idletasks()
    w, h = 1100, 750
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    app = AgenteApp(root)
    root.mainloop()
