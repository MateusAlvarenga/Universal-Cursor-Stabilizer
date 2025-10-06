import tkinter as tk
from tkinter import ttk
from pynput import mouse
import pyautogui
import threading
import keyboard  # pip install keyboard

# Variáveis globais
alpha = 0.2
last_x, last_y = None, None
running = False
listener = None
overlay_enabled = True
overlay = None


# --- Função de suavização ---
def smooth(x, y, last_x, last_y, alpha):
    if last_x is None or last_y is None:
        return x, y
    new_x = last_x + alpha * (x - last_x)
    new_y = last_y + alpha * (y - last_y)
    return new_x, new_y


# --- Overlay ---
def create_overlay(root):
    global overlay
    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)  # remove borda
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.6)  # transparência da janela
    overlay.wm_attributes("-transparentcolor", "white")
    canvas = tk.Canvas(overlay, width=20, height=20, highlightthickness=0, bg="white") 
    canvas.pack()
    canvas.create_oval(2, 2, 18, 18, fill="red")
    overlay.geometry("+0+0")  # inicializa no canto
    return overlay



def move_overlay(x, y):
    if overlay and overlay_enabled:
        overlay.geometry(f"+{int(x)}+{int(y)}")


# --- Callback do mouse ---
def on_move(x, y):
    global last_x, last_y, alpha
    if not running:
        return
    new_x, new_y = smooth(x, y, last_x, last_y, alpha)
    last_x, last_y = new_x, new_y
    pyautogui.moveTo(new_x, new_y)
    move_overlay(new_x, new_y)


# --- Controle do listener ---
def start_listener():
    global listener, running
    if running:
        return
    running = True
    listener = mouse.Listener(on_move=on_move)
    listener.start()
    print("✔ Estabilizador ATIVADO")


def stop_listener():
    global listener, running
    running = False
    if listener:
        listener.stop()
        listener = None
    print("✖ Estabilizador DESATIVADO")


def toggle_listener():
    if running:
        stop_listener()
    else:
        start_listener()


# Thread separada para ouvir atalho
def hotkey_thread():
    keyboard.add_hotkey("ctrl+shift+s", toggle_listener)
    keyboard.wait()  # mantém escutando


# --- GUI ---
def launch_gui():
    def update_alpha(val):
        global alpha
        alpha = float(val)

    def toggle_overlay():
        global overlay_enabled
        overlay_enabled = not overlay_enabled
        if not overlay_enabled and overlay:
            overlay.withdraw()
        elif overlay_enabled and overlay:
            overlay.deiconify()

    root = tk.Tk()
    root.title("Estabilizador de Traço")

    ttk.Label(root, text="Alpha (0.01 = suave, 1.0 = sem suavização):").pack(pady=5)
    slider = ttk.Scale(root, from_=0.01, to=1.0, value=alpha, command=update_alpha)
    slider.pack(fill="x", padx=20)

    btn_start = ttk.Button(root, text="Ativar", command=start_listener)
    btn_start.pack(pady=5)

    btn_stop = ttk.Button(root, text="Desativar", command=stop_listener)
    btn_stop.pack(pady=5)

    btn_overlay = ttk.Button(root, text="Mostrar/Esconder Cursor Fantasma", command=toggle_overlay)
    btn_overlay.pack(pady=5)

    ttk.Label(root, text="Atalho: Ctrl+Shift+S").pack(pady=10)

    # Criar overlay
    create_overlay(root)

    root.mainloop()


if __name__ == "__main__":
    # Thread para capturar atalho global
    threading.Thread(target=hotkey_thread, daemon=True).start()
    launch_gui()
