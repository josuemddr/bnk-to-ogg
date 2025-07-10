import os
import shutil
import subprocess
import time
import urllib.request
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# --- URLs dependencias ---
URLS_NORMALES = {
    "revorb.exe": "https://github.com/ItsBranK/ReVorb/releases/download/v1.0/ReVorb.exe",
    "bnkextr.exe": "https://github.com/eXpl0it3r/bnkextr/releases/download/2.0/bnkextr.exe",
}

URLS_ZIP = {
    "ww2ogg.zip": {
        "url": "https://github.com/hcs64/ww2ogg/releases/download/0.24/ww2ogg024.zip"
    }
}

def agregar_log(texto):
    if texto.startswith(("❌", "⚠️")):
        log_error.insert(tk.END, texto + "\n")
        log_error.see(tk.END)
    else:
        log_exito.insert(tk.END, texto + "\n")
        log_exito.see(tk.END)
    ventana.update()

def descargar_archivo(nombre_archivo, url):
    carpeta_destino = os.path.dirname(os.path.abspath(__file__))
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
    try:
        agregar_log(f"⬇️ Descargando {nombre_archivo}...")
        urllib.request.urlretrieve(url, ruta_destino)
        agregar_log(f"✅ Descargado {nombre_archivo}")
        return True
    except Exception as e:
        agregar_log(f"❌ Error descargando {nombre_archivo}: {e}")
        return False

def descargar_y_extraer_zip(nombre_zip, url):
    carpeta_destino = os.path.dirname(os.path.abspath(__file__))
    ruta_zip = os.path.join(carpeta_destino, nombre_zip)
    try:
        agregar_log(f"⬇️ Descargando {nombre_zip}...")
        urllib.request.urlretrieve(url, ruta_zip)
        agregar_log(f"✅ Descargado {nombre_zip}")

        with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
            agregar_log(f"✅ Extraído todo el contenido de {nombre_zip} en {carpeta_destino}")

        # No eliminamos el archivo zip
        return True

    except Exception as e:
        agregar_log(f"❌ Error descargando o extrayendo {nombre_zip}: {e}")
        return False

def verificar_y_descargar_dependencias():
    faltantes = []
    carpeta_script = os.path.dirname(os.path.abspath(__file__))

    # Verificar ejecutables normales
    for archivo, url in URLS_NORMALES.items():
        ruta = os.path.join(carpeta_script, archivo)
        if not os.path.isfile(ruta):
            faltantes.append((archivo, url))

    # Verificar ww2ogg.exe
    if not os.path.isfile(os.path.join(carpeta_script, "ww2ogg.exe")):
        faltantes.append(("ww2ogg.zip", URLS_ZIP["ww2ogg.zip"]["url"]))

    if not faltantes:
        agregar_log("✅ Todas las dependencias están presentes.")
        return True

    respuesta = messagebox.askyesno("Dependencias faltantes",
                                    "Faltan algunos archivos necesarios:\n" +
                                    "\n".join([f[0] for f in faltantes]) +
                                    "\n¿Quieres descargarlos ahora?")

    if not respuesta:
        agregar_log("⚠️ Dependencias faltantes no descargadas.")
        return False

    todos_descargados = True
    for archivo, url in faltantes:
        if archivo == "ww2ogg.zip":
            exito = descargar_y_extraer_zip(archivo, url)
        else:
            exito = descargar_archivo(archivo, url)
        if not exito:
            todos_descargados = False

    if todos_descargados:
        messagebox.showinfo("Descarga completada", "Todas las dependencias se descargaron correctamente.")
    else:
        messagebox.showwarning("Descarga incompleta", "Algunas dependencias no se pudieron descargar.")

    return todos_descargados

def seleccionar_entrada():
    carpeta = filedialog.askdirectory()
    if carpeta:
        entrada_var.set(carpeta)

def seleccionar_salida():
    carpeta = filedialog.askdirectory()
    if carpeta:
        salida_var.set(carpeta)

def buscar_todos_wem(carpeta):
    archivos = []
    for root, dirs, files in os.walk(carpeta):
        for f in files:
            if f.lower().endswith(".wem"):
                archivos.append(os.path.join(root, f))
    return archivos

def es_ogg_valido(ruta_ogg):
    try:
        resultado = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', ruta_ogg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        duracion = resultado.stdout.decode().strip()
        return float(duracion) > 0
    except Exception:
        return False

def convertir_wem_a_ogg(carpeta_salida, ruta_wem, nombre_base):
    archivo_ogg_temp = os.path.join(os.getcwd(), f"{nombre_base}.ogg")
    archivo_ogg_final = os.path.join(carpeta_salida, f"{nombre_base}.ogg")

    try:
        resultado = subprocess.run([ww2ogg_path, ruta_wem, "--pcb", bin_path],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(archivo_ogg_temp):
            agregar_log(f"❌ ww2ogg falló para {nombre_base}.wem")
            return

        if not es_ogg_valido(archivo_ogg_temp):
            os.remove(archivo_ogg_temp)
            agregar_log(f"❌ Archivo .ogg inválido generado por ww2ogg: {nombre_base}.ogg")
            return

        subprocess.run([revorb_path, archivo_ogg_temp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(archivo_ogg_temp):
            os.replace(archivo_ogg_temp, archivo_ogg_final)
            agregar_log(f"✅ {nombre_base}.wem → .ogg")
        else:
            agregar_log(f"❌ revorb falló para {nombre_base}.ogg")

    except Exception as e:
        if os.path.exists(archivo_ogg_temp):
            os.remove(archivo_ogg_temp)
        agregar_log(f"❌ Error al convertir {nombre_base}: {e}")

def extraer_bnk(carpeta_entrada):
    archivos_bnk = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith(".bnk")]
    if not archivos_bnk:
        agregar_log("⚠️ No se encontraron archivos .bnk.")
        return
    agregar_log(f"📦 {len(archivos_bnk)} archivos .bnk encontrados.")
    for archivo_bnk in archivos_bnk:
        ruta_bnk = os.path.join(carpeta_entrada, archivo_bnk)
        agregar_log(f"⏳ Extrayendo {archivo_bnk}...")
        try:
            subprocess.run([bnkextr_path, ruta_bnk], cwd=carpeta_entrada, check=True)
            agregar_log(f"✅ {archivo_bnk} extraído.")
        except Exception as e:
            agregar_log(f"❌ Error extrayendo {archivo_bnk}: {e}")

def esperar_estabilidad_wem(carpeta_entrada, espera=3, max_intentos=10):
    agregar_log("🕒 Esperando estabilidad de .wem...")
    prev = -1
    intentos = 0
    while intentos < max_intentos:
        actuales = buscar_todos_wem(carpeta_entrada)
        if len(actuales) == prev:
            agregar_log(f"🔒 Estable: {len(actuales)} archivos .wem.")
            return
        prev = len(actuales)
        intentos += 1
        time.sleep(espera)
    agregar_log("⚠️ Continuando sin estabilidad.")

def procesar_conversion(carpeta_entrada, carpeta_salida):
    archivos_wem = buscar_todos_wem(carpeta_entrada)
    total = len(archivos_wem)
    if total == 0:
        agregar_log("⚠️ No se encontraron archivos .wem.")
        etiqueta_progreso.config(text="")
        return
    agregar_log(f"🎧 Convirtiendo {total} archivos .wem...")
    progreso['value'] = 0
    progreso['maximum'] = total
    for i, ruta_wem in enumerate(archivos_wem, start=1):
        nombre_base = os.path.splitext(os.path.basename(ruta_wem))[0]
        convertir_wem_a_ogg(carpeta_salida, ruta_wem, nombre_base)
        actualizar_barra(i, total)

def mover_carpetas_y_borrar_wem(origen, destino):
    carpetas = [d for d in os.listdir(origen) if os.path.isdir(os.path.join(origen, d))]
    for carpeta in carpetas:
        ruta_origen = os.path.join(origen, carpeta)
        ruta_destino = os.path.join(destino, carpeta)
        try:
            shutil.move(ruta_origen, ruta_destino)
            agregar_log(f"📁 Movida: {carpeta}")
        except Exception as e:
            agregar_log(f"❌ Error al mover {carpeta}: {e}")
            continue

        if eliminar_wem_var.get():
            for root, _, files in os.walk(ruta_destino):
                for archivo in files:
                    if archivo.lower().endswith(".wem"):
                        try:
                            os.remove(os.path.join(root, archivo))
                            agregar_log(f"🗑️ .wem borrado: {archivo}")
                        except Exception as e:
                            agregar_log(f"❌ No se pudo borrar {archivo}: {e}")

def verificar_ogg_en_salida(carpeta_salida):
    if not verificar_ogg_var.get():
        agregar_log("ℹ️ Verificación con ffprobe desactivada.")
        return

    if not eliminar_ogg_corrupto_var.get():
        agregar_log("ℹ️ Eliminación de .ogg corruptos desactivada.")
        return

    agregar_log("🔍 Verificando .ogg corruptos...")
    eliminados = 0
    for root, _, files in os.walk(carpeta_salida):
        for archivo in files:
            if archivo.lower().endswith(".ogg"):
                ruta_ogg = os.path.join(root, archivo)
                if not es_ogg_valido(ruta_ogg):
                    try:
                        os.remove(ruta_ogg)
                        agregar_log(f"🗑️ .ogg corrupto eliminado: {archivo}")
                        eliminados += 1
                    except Exception as e:
                        agregar_log(f"❌ Error eliminando {archivo}: {e}")
    if eliminados == 0:
        agregar_log("✅ Todos los .ogg son válidos.")
    else:
        agregar_log(f"⚠️ Se eliminaron {eliminados} .ogg corruptos.")

def actualizar_barra(valor, maximo):
    progreso['value'] = valor
    progreso['maximum'] = maximo
    etiqueta_progreso.config(text=f"Archivo {valor} / {maximo}")
    ventana.update()

def procesar():
    carpeta_entrada = entrada_var.get()
    carpeta_salida = salida_var.get()
    if not carpeta_entrada or not carpeta_salida:
        messagebox.showerror("Error", "Selecciona carpetas de entrada y salida.")
        return

    global bnkextr_path, ww2ogg_path, revorb_path, bin_path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bnkextr_path = os.path.join(script_dir, "bnkextr.exe")
    ww2ogg_path = os.path.join(script_dir, "ww2ogg.exe")
    revorb_path = os.path.join(script_dir, "revorb.exe")
    bin_path = os.path.join(script_dir, "packed_codebooks_aoTuV_603.bin")

    # Verificar y descargar dependencias
    if not verificar_y_descargar_dependencias():
        agregar_log("❌ No se tienen todas las dependencias necesarias. Abortando.")
        return

    # Verificar que existen los archivos después de la posible descarga
    if not all(os.path.isfile(p) for p in [ww2ogg_path, revorb_path, bnkextr_path]):
        messagebox.showerror("Error", "Faltan ejecutables necesarios tras descarga.")
        return

    # Nota: el .bin viene incluido en ww2ogg, no se necesita comprobarlo separado

    log_exito.delete("1.0", tk.END)
    log_error.delete("1.0", tk.END)

    extraer_bnk(carpeta_entrada)
    esperar_estabilidad_wem(carpeta_entrada)
    procesar_conversion(carpeta_entrada, carpeta_salida)
    mover_carpetas_y_borrar_wem(carpeta_entrada, carpeta_salida)
    verificar_ogg_en_salida(carpeta_salida)

ventana = tk.Tk()
ventana.title("Conversor BNK/WEM → OGG")
ventana.geometry("900x600")
ventana.configure(bg="#222")

entrada_var = tk.StringVar()
salida_var = tk.StringVar()
eliminar_wem_var = tk.BooleanVar(value=True)
eliminar_ogg_corrupto_var = tk.BooleanVar(value=True)
verificar_ogg_var = tk.BooleanVar(value=True)

frame = tk.Frame(ventana, bg="#222")
frame.pack(pady=10)

tk.Label(frame, text="📁 Carpeta raíz de entrada (.bnk):", fg="white", bg="#222").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=entrada_var, width=50).grid(row=1, column=0)
tk.Button(frame, text="Seleccionar", command=seleccionar_entrada).grid(row=1, column=1)

tk.Label(frame, text="💾 Carpeta raíz de salida (.ogg):", fg="white", bg="#222").grid(row=2, column=0, sticky="w", pady=(10, 0))
tk.Entry(frame, textvariable=salida_var, width=50).grid(row=3, column=0)
tk.Button(frame, text="Seleccionar", command=seleccionar_salida).grid(row=3, column=1)

panel_derecho = tk.Frame(frame, bg="#222")
panel_derecho.grid(row=0, column=2, rowspan=6, padx=(20, 0), sticky="n")

def on_verificar_ogg_toggle():
    if verificar_ogg_var.get():
        eliminar_ogg_corrupto_cb.config(state="normal")
    else:
        eliminar_ogg_corrupto_var.set(False)
        eliminar_ogg_corrupto_cb.config(state="disabled")

eliminar_wem_cb = tk.Checkbutton(panel_derecho, text="Eliminar .wem", variable=eliminar_wem_var,
               bg="#222", fg="white", selectcolor="#333")
eliminar_wem_cb.pack(anchor="w", pady=(5, 2))

eliminar_ogg_corrupto_cb = tk.Checkbutton(panel_derecho, text="Eliminar .ogg corruptos", variable=eliminar_ogg_corrupto_var,
               bg="#222", fg="white", selectcolor="#333")
eliminar_ogg_corrupto_cb.pack(anchor="w", pady=(0, 5))

verificar_ogg_cb = tk.Checkbutton(panel_derecho, text="Verificar .ogg con ffprobe", variable=verificar_ogg_var,
               bg="#222", fg="white", selectcolor="#333", command=on_verificar_ogg_toggle)
verificar_ogg_cb.pack(anchor="w", pady=(0, 5))

# Inicializar el estado correcto al iniciar la app
on_verificar_ogg_toggle()

tk.Button(ventana, text="▶️ Iniciar proceso", command=procesar, bg="#4caf50", fg="white", font=("Arial", 11)).pack(pady=10)

panel_logs = tk.Frame(ventana, bg="#222")
panel_logs.pack(padx=10, pady=(0, 10), fill="both", expand=True)

log_exito = scrolledtext.ScrolledText(panel_logs, width=60, height=20, bg="#111", fg="lime", font=("Consolas", 9))
log_exito.pack(side="left", fill="both", expand=True, padx=(0, 5))

log_error = scrolledtext.ScrolledText(panel_logs, width=60, height=20, bg="#111", fg="red", font=("Consolas", 9))
log_error.pack(side="right", fill="both", expand=True)

progreso = ttk.Progressbar(ventana, orient="horizontal", length=800, mode="determinate")
progreso.pack()

etiqueta_progreso = tk.Label(ventana, text="", bg="#222", fg="white", font=("Consolas", 11))
etiqueta_progreso.pack(pady=(5, 15))

ventana.mainloop()
