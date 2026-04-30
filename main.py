"""
Pemilih Persegi Panjang Tangkapan Layar + OCR + Terjemahan
Tombol Pintas: Bebas (Kustom)
Gratis, Luring (OCR), Tanpa Pendaftaran
Stack: pynput + mss + tkinter + pywin32 + EasyOCR + RapidOCR + translators
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
from PIL import Image
import win32gui as gw
import win32con as gc

# Modul berat akan di-import secara lazy (saat dibutuhkan) untuk mempercepat startup GUI
# import easyocr
# import numpy as np
# from rapidocr_onnxruntime import RapidOCR
# import translators as ts

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

TRANS_LANGS = {
    'af': 'afrikaans', 'sq': 'albanian', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani',
    'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian',
    'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech',
    'da': 'danish', 'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian',
    'tl': 'filipino', 'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician',
    'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole',
    'ha': 'hausa', 'haw': 'hawaiian', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong',
    'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish',
    'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh',
    'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish', 'ky': 'kyrgyz', 'lo': 'lao',
    'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian',
    'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori',
    'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar', 'ne': 'nepali', 'no': 'norwegian',
    'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi',
    'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian',
    'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian',
    'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili', 'sv': 'swedish',
    'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian',
    'ur': 'urdu', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish',
    'yo': 'yoruba', 'zu': 'zulu'
}

TRANS_LANGS_FORMATTED = {k: v.title() for k, v in TRANS_LANGS.items()}

# Untuk source language kita pakai dictionary yang sama
SRC_LANGS_FORMATTED = TRANS_LANGS_FORMATTED.copy()
# Tambahkan opsi auto untuk source language
SRC_LANGS_FORMATTED['auto'] = 'Auto Detect'

OCR_ENGINES = ["EasyOCR", "RapidOCR"]
TRANS_ENGINES = ["google", "bing", "yandex", "papago", "argos", "caiyun", "itranslate", "lara", "sysTran", "youdao"]
TRANS_ENGINES_FORMATTED = {k: k.title() for k in TRANS_ENGINES}

# Kamus bahasa yang didukung oleh masing-masing mesin (hasil pengujian langsung)
ENGINE_SUPPORTED_LANGS = {
    'google': ['af', 'sq', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'haw', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'],
    'bing': ['af', 'sq', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'he', 'hi', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'kn', 'kk', 'km', 'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'my', 'ne', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'cy', 'xh', 'yo', 'zu'],

    'yandex': ['sq', 'hy', 'az', 'be', 'bg', 'ca', 'zh-cn', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'de', 'el', 'hu', 'it', 'lv', 'lt', 'mk', 'no', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sv', 'tr', 'uk'],
    'papago': ['ar', 'zh-cn', 'zh-tw', 'en', 'fr', 'de', 'hi', 'id', 'it', 'ja', 'ko', 'pt', 'ru', 'es', 'th', 'vi'],
    'argos': ['ar', 'az', 'bg', 'bn', 'ca', 'cs', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gl', 'he', 'hi', 'hu', 'id', 'it', 'ja', 'ko', 'ky', 'lt', 'lv', 'ms', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sq', 'sr', 'sv', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw'],
    'caiyun': ['ar', 'de', 'el', 'en', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'pl', 'pt', 'ru', 'sw', 'th', 'tr', 'vi', 'zh-cn', 'zh-tw'],
    'itranslate': ['af', 'ar', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'ceb', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gl', 'gu', 'ha', 'he', 'hi', 'hmn', 'hr', 'ht', 'hu', 'hy', 'id', 'ig', 'is', 'it', 'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'la', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'ny', 'pa', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'so', 'sq', 'sr', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tl', 'tr', 'uk', 'ur', 'uz', 'vi', 'yi', 'yo', 'zh-cn', 'zh-tw', 'zu'],
    'lara': ['af', 'ar', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'ceb', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gd', 'gl', 'gu', 'ha', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'ig', 'is', 'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'ny', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sd', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tl', 'tr', 'uk', 'ur', 'uz', 'vi', 'xh', 'yo', 'zh-cn', 'zh-tw', 'zu'],
    'sysTran': ['af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'ga', 'ha', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'ko', 'ku', 'lt', 'lv', 'mk', 'mn', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sk', 'sl', 'sq', 'sr', 'sv', 'sw', 'ta', 'tg', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn'],
    'youdao': ['ar', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'ceb', 'co', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'fy', 'ga', 'gd', 'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hmn', 'hr', 'ht', 'hu', 'hy', 'id', 'ig', 'is', 'it', 'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'ny', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sd', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tl', 'tr', 'uk', 'ur', 'uz', 'vi', 'xh', 'yi', 'yo', 'zh-cn', 'zh-tw', 'zu']
}

CONFIG_FILE = "config.json"

# State Global
easyocr_reader = None
rapidocr_engine = None

current_ocr_engine = None
current_source_lang = None
current_trans_engine = None
current_dest_lang = None

def get_default_os_lang():
    try:
        os_lang = locale.getdefaultlocale()[0].split('_')[0]
        if os_lang in TRANS_LANGS:
            return os_lang
    except:
        pass
    return 'id'

def load_config():
    global current_ocr_engine, current_source_lang, current_trans_engine, current_dest_lang
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                current_ocr_engine = data.get("ocr_engine")
                current_source_lang = data.get("source_lang")
                current_trans_engine = data.get("trans_engine")
                current_dest_lang = data.get("dest_lang")
        except:
            pass

def save_config(ocr_eng, src, trans_eng, dst):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "ocr_engine": ocr_eng,
                "source_lang": src,
                "trans_engine": trans_eng,
                "dest_lang": dst
            }, f)
    except:
        pass

def init_reader(ocr_eng, src_lang):
    global easyocr_reader, rapidocr_engine
    
    # Lazy import di dalam fungsi agar startup instan
    import easyocr
    
    if ocr_eng == "EasyOCR":
        # Konversi kode bahasa ke format EasyOCR jika perlu
        easyocr_code = src_lang
        if src_lang == 'zh-cn': easyocr_code = 'ch_sim'
        elif src_lang == 'zh-tw': easyocr_code = 'ch_tra'
        elif src_lang == 'auto': easyocr_code = 'en' # Fallback
        
        langs = ['en', easyocr_code] if easyocr_code not in ['en', 'auto'] else ['en']
        try:
            easyocr_reader = easyocr.Reader(langs, gpu=False, verbose=False)
        except Exception as e:
            # Jika bahasa tidak didukung EasyOCR, fallback ke English
            print(f"Bahasa {easyocr_code} tidak didukung EasyOCR, fallback ke en. Error: {e}")
            easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            
        rapidocr_engine = None
    elif ocr_eng == "RapidOCR":
        from rapidocr_onnxruntime import RapidOCR
        rapidocr_engine = RapidOCR()
        easyocr_reader = None

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
            
            # Lakukan OCR dan Translate di background thread agar Main UI tidak freeze
            threading.Thread(target=self.process_ocr_and_translate, args=(img,), daemon=True).start()
        else:
            self.on_escape()
            
    def on_escape(self, event=None):
        self.window.destroy()
        
    def process_ocr_and_translate(self, img):
        global current_ocr_engine, current_source_lang, current_trans_engine, current_dest_lang
        try:
            import numpy as np
            import translators as ts
            
            img_np = np.array(img)
            ocr_text = ""
            
            # 1. Memproses OCR
            if current_ocr_engine == "EasyOCR" and easyocr_reader:
                ocr_results = easyocr_reader.readtext(img_np)
                ocr_text = ' '.join([res[1] for res in ocr_results])
            elif current_ocr_engine == "RapidOCR" and rapidocr_engine:
                ocr_results, _ = rapidocr_engine(img_np)
                if ocr_results:
                    ocr_text = ' '.join([res[1] for res in ocr_results])
            
            # 2. Menerjemahkan Teks
            translated_text = ""
            if ocr_text.strip():
                try:
                    # Parameter 'auto' disesuaikan untuk modul translators
                    src = current_source_lang if current_source_lang != 'auto' else 'auto'
                    translated_text = ts.translate_text(
                        query_text=ocr_text, 
                        translator=current_trans_engine,
                        from_language=src, 
                        to_language=current_dest_lang
                    )
                except Exception as e:
                    translated_text = f"Translation failed using {current_trans_engine}:\n{e}"
            else:
                translated_text = "No text detected by OCR engine."
            
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
        self.root.geometry("480x450")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        tk.Label(self.root, text="Global Application Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Peta Balik untuk ID
        self.src_map = {name: code for code, name in SRC_LANGS_FORMATTED.items()}
        self.dst_map = {name: code for code, name in TRANS_LANGS_FORMATTED.items()}
        self.trans_eng_map = {name: code for code, name in TRANS_ENGINES_FORMATTED.items()}
        
        # --- 1. OCR Engine ---
        tk.Label(self.root, text="1. OCR Engine (Text Reader):").pack(anchor='w', padx=25)
        self.ocr_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.ocr_combo.pack(padx=25, pady=(0, 10))
        self.ocr_combo['values'] = OCR_ENGINES
        if current_ocr_engine in OCR_ENGINES:
            self.ocr_combo.set(current_ocr_engine)
            
        # --- 2. Bahasa Sumber (OCR) ---
        tk.Label(self.root, text="2. Source Language:").pack(anchor='w', padx=25)
        self.src_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.src_combo.pack(padx=25, pady=(0, 10))
        self.src_combo['values'] = sorted(list(self.src_map.keys()))
        default_src_name = SRC_LANGS_FORMATTED.get(current_source_lang, "English")
        if default_src_name in self.src_combo['values']:
            self.src_combo.set(default_src_name)
            
        # --- 3. Mesin Penerjemah ---
        tk.Label(self.root, text="3. Translation Engine:").pack(anchor='w', padx=25)
        self.trans_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.trans_combo.pack(padx=25, pady=(0, 10))
        self.trans_combo['values'] = sorted(list(self.trans_eng_map.keys()))
        default_trans_name = TRANS_ENGINES_FORMATTED.get(current_trans_engine, "Google")
        if default_trans_name in self.trans_combo['values']:
            self.trans_combo.set(default_trans_name)
            
        # --- 4. Bahasa Tujuan (Terjemahan) ---
        tk.Label(self.root, text="4. Target Language:").pack(anchor='w', padx=25)
        self.dst_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.dst_combo.pack(padx=25, pady=(0, 10))
        
        self.trans_combo.bind("<<ComboboxSelected>>", self.on_trans_engine_changed)
        self._update_target_langs_logic(show_warning=False)
        
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

    def refresh_ui_from_config(self):
        """Memperbarui nilai di UI setelah config dimuat dari file"""
        if current_ocr_engine in OCR_ENGINES:
            self.ocr_combo.set(current_ocr_engine)
        
        src_name = SRC_LANGS_FORMATTED.get(current_source_lang)
        if src_name in self.src_combo['values']:
            self.src_combo.set(src_name)
            
        trans_name = TRANS_ENGINES_FORMATTED.get(current_trans_engine)
        if trans_name in self.trans_combo['values']:
            self.trans_combo.set(trans_name)
            
        # Update target languages berdasarkan engine yang baru dimuat
        self._update_target_langs_logic(show_warning=False)
        
        dst_name = TRANS_LANGS_FORMATTED.get(current_dest_lang)
        if dst_name in self.dst_combo['values']:
            self.dst_combo.set(dst_name)

    def on_trans_engine_changed(self, event=None):
        self._update_target_langs_logic(show_warning=True)

    def _update_target_langs_logic(self, show_warning=False):
        selected_engine_name = self.trans_combo.get()
        if not selected_engine_name:
            return
            
        engine_code = self.trans_eng_map.get(selected_engine_name, "google")
        supported_codes = ENGINE_SUPPORTED_LANGS.get(engine_code, list(self.dst_map.values()))
        
        supported_names = sorted([name for name, code in self.dst_map.items() if code in supported_codes])
        self.dst_combo['values'] = supported_names
        
        current_dst_name = self.dst_combo.get()
        if current_dst_name and current_dst_name not in supported_names:
            self.dst_combo.set('')
            if show_warning:
                messagebox.showinfo("Informasi Bahasa", f"Bahasa '{current_dst_name}' tidak didukung oleh mesin {selected_engine_name}.\nKolom target telah dikosongkan.")

    def on_closing(self):
        self.root.destroy()
        os._exit(0)

    def load_model_initial(self):
        if current_ocr_engine is None:
            self.status_label.config(text="Status: Please configure settings", fg="orange")
            return

        self.is_loading = True
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Loading OCR Model... Please wait.", fg="blue")
        
        def _bg_load():
            try:
                init_reader(current_ocr_engine, current_source_lang)
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
        global current_ocr_engine, current_source_lang, current_trans_engine, current_dest_lang
        
        ocr_eng = self.ocr_combo.get()
        src_name = self.src_combo.get()
        trans_eng_name = self.trans_combo.get()
        dst_name = self.dst_combo.get()

        if not all([ocr_eng, src_name, trans_eng_name, dst_name]):
            messagebox.showwarning("Warning", "Please select all options before saving!")
            return

        src_code = self.src_map[src_name]
        trans_eng_code = self.trans_eng_map[trans_eng_name]
        dst_code = self.dst_map[dst_name]
        
        save_config(ocr_eng, src_code, trans_eng_code, dst_code)
        
        current_trans_engine = trans_eng_code
        current_dest_lang = dst_code
        
        # Update OCR Model jika diperlukan (misalnya mesin atau bahasa sumber berubah)
        if ocr_eng != current_ocr_engine or src_code != current_source_lang:
            self.is_loading = True
            self.save_btn.config(state=tk.DISABLED)
            self.status_label.config(text=f"Status: Loading {ocr_eng} model...", fg="blue")
            
            def _bg_apply():
                try:
                    init_reader(ocr_eng, src_code)
                    global current_ocr_engine, current_source_lang
                    current_ocr_engine = ocr_eng
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
        messagebox.showinfo("Success", "Settings saved. Engine successfully updated!")
        
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
        app_instance.root.event_generate("<<TriggerHotkey>>", when="tail")

if __name__ == '__main__':
    # Jalankan GUI secepat mungkin
    app_instance = App()
    
    # Update tampilan agar window langsung muncul sebelum listener dimulai
    app_instance.root.update()
    
    load_config()
    
    # Refresh UI setelah config dimuat
    app_instance.refresh_ui_from_config()
    
    # Listener Keyboard Latar Belakang (non-blocking)
    hotkey_listener = keyboard.GlobalHotKeys({'<ctrl>+<shift>+<alt>+z': on_hotkey})
    hotkey_listener.start()
    
    # Pemuatan model awal (background)
    app_instance.load_model_initial()
    
    app_instance.root.mainloop()