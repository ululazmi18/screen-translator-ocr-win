"""
Pemilih Persegi Panjang Tangkapan Layar + OCR + Terjemahan
Tombol Pintas: Bebas (Kustom)
Gratis, Luring, Tanpa Pendaftaran
Stack: pynput + mss + tkinter + pywin32 + EasyOCR + googletrans
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import locale
import ctypes
import os
import sys
import warnings

from pynput import keyboard
from mss import MSS
from PIL import Image, ImageTk
import win32gui as gw
import win32con as gc
import easyocr
import numpy as np
from googletrans import Translator, LANGUAGES

# Menyembunyikan peringatan CPU dari easyocr dan peringatan PyTorch
warnings.filterwarnings("ignore", category=UserWarning)

# Mengatasi masalah scaling DPI pada Windows agar koordinat seleksi akurat
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ====================================================
# Data & Kamus Bahasa
# ====================================================

TRANS_LANGS = LANGUAGES
TRANS_LANGS_FORMATTED = {k: v.title() for k, v in TRANS_LANGS.items()}

EASYOCR_CODES = ['af', 'az', 'bs', 'cs', 'cy', 'da', 'de', 'en', 'es', 'et', 'fr', 'ga', 'hr', 'hu', 'id', 'is', 'it', 'ku', 'la', 'lt', 'lv', 'mi', 'ms', 'mt', 'nl', 'no', 'oc', 'pi', 'pl', 'pt', 'ro', 'rs_latin', 'sk', 'sl', 'sq', 'sv', 'sw', 'tl', 'tr', 'uz', 'vi', 'ar', 'fa', 'ug', 'ur', 'ru', 'rs_cyrillic', 'be', 'bg', 'uk', 'mn', 'abq', 'ady', 'kbd', 'ava', 'dar', 'inh', 'che', 'lbe', 'lez', 'tab', 'tjk', 'hi', 'mr', 'ne', 'bh', 'mai', 'ang', 'bho', 'mah', 'sck', 'new', 'gom', 'sa', 'bgc', 'bn', 'as', 'mni', 'th', 'ch_sim', 'ch_tra', 'ja', 'ko', 'ta', 'te', 'kn']

EASYOCR_LANGS = {}
for code in EASYOCR_CODES:
    if code in TRANS_LANGS:
        EASYOCR_LANGS[code] = TRANS_LANGS[code].title()
    elif code == 'ch_sim': EASYOCR_LANGS[code] = 'Chinese (Simplified)'
    elif code == 'ch_tra': EASYOCR_LANGS[code] = 'Chinese (Traditional)'
    elif code == 'rs_latin': EASYOCR_LANGS[code] = 'Serbian (Latin)'
    elif code == 'rs_cyrillic': EASYOCR_LANGS[code] = 'Serbian (Cyrillic)'
    else: EASYOCR_LANGS[code] = code.title()

CONFIG_FILE = "config.json"

# State Global
reader = None
translator = Translator()
current_source_lang = "en"
current_dest_lang = "id"

def get_default_os_lang():
    try:
        os_lang = locale.getdefaultlocale()[0].split('_')[0]
        if os_lang in TRANS_LANGS:
            return os_lang
    except:
        pass
    return 'id'

def load_config():
    global current_source_lang, current_dest_lang
    default_config = {
        "source_lang": "en",
        "dest_lang": get_default_os_lang()
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                default_config.update(data)
        except:
            pass
            
    current_source_lang = default_config["source_lang"]
    current_dest_lang = default_config["dest_lang"]

def save_config(src, dst):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"source_lang": src, "dest_lang": dst}, f)
    except:
        pass

def init_reader(src_lang):
    global reader
    # Kombinasikan dengan 'en' jika bukan 'en' (Sangat direkomendasikan EasyOCR)
    langs = ['en', src_lang] if src_lang != 'en' else ['en']
    reader = easyocr.Reader(langs, gpu=False, verbose=False)

# ====================================================
# UI Components
# ====================================================

class ResultOverlay:
    def __init__(self, parent, source_text, translated_text):
        self.window = tk.Toplevel(parent)
        self.window.title("Translation Result")
        self.window.attributes('-topmost', True)
        
        self.source_text = source_text if source_text else ""
        self.translated_text = translated_text if translated_text else "No translatable text found"
        
        # Kalkulasi tinggi window dinamis (min 3 baris, maks 15 baris)
        lines_by_length = sum(len(line) // 45 + 1 for line in self.translated_text.split('\n'))
        num_lines = min(max(lines_by_length, 3), 15)
        
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Translation Result:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, font=('Arial', 12), wrap=tk.WORD, yscrollcommand=scrollbar.set, borderwidth=0, bg=self.window.cget('bg'), width=45, height=num_lines)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        text_widget.insert(tk.END, self.translated_text)
        text_widget.config(state=tk.DISABLED)
        
        # Frame untuk Tombol Copy
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(btn_frame, text="Copy Source", command=self.copy_source, bg="#e0e0e0").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(btn_frame, text="Copy Translation", command=self.copy_translation, bg="#e0e0e0").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
    def copy_source(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.source_text)
        
    def copy_translation(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.translated_text)

class RectangleSelector:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.3)
        self.window.configure(bg='black')
        self.window.overrideredirect(True)
        
        # Force overlay topmost
        self.window.update()
        hwnd = gw.GetParent(self.window.winfo_id())
        ex_style = gw.GetWindowLong(hwnd, gc.GWL_EXSTYLE)
        gw.SetWindowLong(hwnd, gc.GWL_EXSTYLE, ex_style | gc.WS_EX_LAYERED | gc.WS_EX_TOPMOST)
        gw.SetLayeredWindowAttributes(hwnd, 0, 100, gc.LWA_ALPHA)
        
        self.canvas = tk.Canvas(self.window, highlightthickness=0, bg='black', cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.rect_id = None
        self.start_x = self.start_y = 0
        self.bind_events()
        self.window.focus_force()
    
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", self.on_escape)
    
    def on_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.canvas.delete("selector")
    
    def on_drag(self, event):
        self.canvas.delete("selector")
        x, y = event.x_root, event.y_root
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, x, y,
            outline="lime", width=3, fill="", 
            tags="selector", dash=(5, 5)
        )
        self.window.update()
    
    def on_release(self, event):
        x2, y2 = event.x_root, event.y_root
        region = {
            "top": int(min(self.start_y, y2)),
            "left": int(min(self.start_x, x2)),
            "width": int(abs(x2 - self.start_x)),
            "height": int(abs(y2 - self.start_y))
        }
        if region['width'] > 10 and region['height'] > 10:  # Seleksi valid
            self.window.withdraw() # Sembunyikan window secara instan
            self.window.update()   # Paksa pembaruan layar agar overlay bersih
            time.sleep(0.1)      # Jeda sejenak untuk transisi window
            
            with MSS() as sct:
                screenshot = sct.grab(region)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                
            self.window.destroy() # Hancurkan UI selector
            
            # Lakukan OCR dan Translate di background thread agar Main UI tidak freeze "Not Responding"
            threading.Thread(target=self.process_ocr_and_translate, args=(img,), daemon=True).start()
        else:
            self.on_escape()
            
    def on_escape(self, event=None):
        self.window.destroy()
        
    def process_ocr_and_translate(self, img):
        global translator
        try:
            # Memproses OCR
            ocr_results = reader.readtext(np.array(img))
            ocr_text = ' '.join([res[1] for res in ocr_results])
            
            # Menerjemahkan Teks
            translated_text = ""
            if ocr_text.strip():
                try:
                    # Instansiasi ulang translator untuk menghindari session timeout / bug API Google
                    translator = Translator()
                    trans = translator.translate(ocr_text, dest=current_dest_lang)
                    translated_text = trans.text
                except Exception as e:
                    translated_text = f"Translation failed: {e}"
            
            # Meneruskan hasil ke UI di main thread
            self.parent.last_ocr_text = ocr_text
            self.parent.last_translation = translated_text
            self.parent.event_generate("<<ShowResult>>", when="tail")
            
        except Exception as e:
            print(f"Error pada processing: {e}")


# ====================================================
# Main Application
# ====================================================

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Translator - Settings")
        self.root.geometry("480x350")
        
        # Jika di-close oleh tombol X
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        tk.Label(self.root, text="Global Language Settings", font=('Arial', 14, 'bold')).pack(pady=15)
        
        # Peta Balik untuk ID
        self.src_map = {name: code for code, name in EASYOCR_LANGS.items()}
        self.dst_map = {name: code for code, name in TRANS_LANGS_FORMATTED.items()}
        
        # --- Bahasa Sumber (OCR) ---
        tk.Label(self.root, text="Screen Text Language (OCR):").pack(anchor='w', padx=25)
        self.src_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.src_combo.pack(padx=25, pady=5)
        self.src_combo['values'] = sorted(list(self.src_map.keys()))
        
        default_src_name = EASYOCR_LANGS.get(current_source_lang, "English")
        if default_src_name in self.src_combo['values']:
            self.src_combo.set(default_src_name)
            
        # --- Bahasa Tujuan (Terjemahan) ---
        tk.Label(self.root, text="Translate To:").pack(anchor='w', padx=25, pady=(15,0))
        self.dst_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.dst_combo.pack(padx=25, pady=5)
        self.dst_combo['values'] = sorted(list(self.dst_map.keys()))
        
        default_dst_name = TRANS_LANGS_FORMATTED.get(current_dest_lang, "Indonesian")
        if default_dst_name in self.dst_combo['values']:
            self.dst_combo.set(default_dst_name)
            
        # --- Tombol Simpan ---
        self.save_btn = tk.Button(self.root, text="Save & Apply Settings", command=self.apply_settings, bg="lime", font=('Arial', 10, 'bold'))
        self.save_btn.pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="", fg="blue", font=('Arial', 9, 'italic'))
        self.status_label.pack()
        
        self.info_label = tk.Label(self.root, text="Leave this window open or minimize it.\nPress Ctrl+Shift+Alt+Z anywhere to capture the screen.", fg="gray", justify="center")
        self.info_label.pack(pady=(5,0))
        
        # Events
        self.root.bind("<<TriggerHotkey>>", self.on_hotkey_triggered)
        self.root.bind("<<ShowResult>>", self.on_show_result)
        self.root.last_ocr_text = ""
        self.root.last_translation = ""
        self.is_loading = False
        
        # Load Model Awal
        self.load_model_initial()

    def on_closing(self):
        # Keluar dari aplikasi seluruhnya
        self.root.destroy()
        os._exit(0)

    def load_model_initial(self):
        self.is_loading = True
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Loading OCR Model... Please wait.", fg="blue")
        
        def _bg_load():
            try:
                init_reader(current_source_lang)
                self.root.after(0, self._on_model_loaded_success)
            except Exception as e:
                self.root.after(0, lambda err=e: self._on_model_loaded_error(err))
                
        threading.Thread(target=_bg_load, daemon=True).start()

    def _on_model_loaded_success(self):
        self.is_loading = False
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Model Ready", fg="green")
        
    def _on_model_loaded_error(self, e):
        self.is_loading = False
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Failed to load model", fg="red")
        messagebox.showerror("Error", f"Failed to load initial model: {e}")

    def apply_settings(self):
        global current_source_lang, current_dest_lang
        
        # Validasi Bahasa
        src_code = self.src_map[self.src_combo.get()]
        dst_code = self.dst_map[self.dst_combo.get()]
        
        save_config(src_code, dst_code)
        current_dest_lang = dst_code
        
        # Update OCR Model
        if src_code != current_source_lang:
            self.is_loading = True
            self.save_btn.config(state=tk.DISABLED)
            self.status_label.config(text=f"Status: Downloading/Loading {self.src_combo.get()} model...", fg="blue")
            
            def _bg_apply():
                try:
                    init_reader(src_code)
                    global current_source_lang
                    current_source_lang = src_code
                    self.root.after(0, self._on_apply_success)
                except Exception as e:
                    self.root.after(0, lambda err=e: self._on_apply_error(err))
                    
            threading.Thread(target=_bg_apply, daemon=True).start()
        else:
            messagebox.showinfo("Saved", "Settings saved successfully!")
            
    def _on_apply_success(self):
        self.is_loading = False
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Model Ready", fg="green")
        messagebox.showinfo("Success", "Settings saved. Language model successfully downloaded and updated!")
        
    def _on_apply_error(self, e):
        self.is_loading = False
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Failed to load model", fg="red")
        messagebox.showerror("Error", f"Failed to load OCR model: {e}")
            
    def on_hotkey_triggered(self, event=None):
        if getattr(self, 'is_loading', False):
            messagebox.showwarning("Wait", "The OCR model is still loading. Please wait until 'Model Ready'.")
            return
            
        # Mencegah spawn berlipat ganda
        if not hasattr(self, 'selector') or not self.selector.window.winfo_exists():
            self.selector = RectangleSelector(self.root)

    def on_show_result(self, event=None):
        ResultOverlay(self.root, self.root.last_ocr_text, self.root.last_translation)

# ====================================================
# Global Hotkey Listener
# ====================================================
app_instance = None

def on_hotkey():
    if app_instance and app_instance.root:
        # Panggil virtual event yang dijalankan di main GUI thread
        app_instance.root.event_generate("<<TriggerHotkey>>", when="tail")

if __name__ == '__main__':
    load_config()
    
    # Listener Keyboard Latar Belakang
    hotkey_listener = keyboard.GlobalHotKeys({'<ctrl>+<shift>+<alt>+z': on_hotkey})
    hotkey_listener.start()
    
    # Jalankan Aplikasi GUI
    app_instance = App()
    app_instance.root.mainloop()