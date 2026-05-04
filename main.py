"""
Pemilih Persegi Panjang Tangkapan Layar + OCR + Terjemahan
Tombol Pintas: Bebas (Kustom)
Gratis, Luring (OCR), Tanpa Pendaftaran
Stack: pynput + mss + tkinter + pywin32 + docTR + translators
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
import re

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
# Ikon Base64
# ====================================================
ICON_TRANSLATE = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAADPklEQVR4nO2Y60tTYRzHfRP9D0XoROnySrq+8IXki64gWAvCMhLzUlCiqCxFp6DOLElrm5eBCa7Ekixm3qopmjov28nbNtms1KwQMz3bnPOyX5xz8izZTsnOtrMD5wtfePac3wPfz3N+5+zhBARw4sSJk18qWLJ8nidBv/KkJnDHgWJzGKMAQVJ01t3wuCVoOaMAPDrhCS+ElMNuNgMAT4peZDVAkNTUzHIAdH3fY8se1gLwMAgJmslqgPDaJdDojYC4aY3OOKvRG896BSC3exW2JOhcpaxrGJx2GwAhIGa8AoD82CABBuY2KOuSXs3TAkD0RvA4wMmnFrCT8QEfR8gtLmsPVaOg0k75F4B42IYHn7fYYdFKoJQN2ijry7rm/AcgWGqCmeVNPHTd2Bo0aNfwMTYXTLEmqv6n/wDEvF4hWwcbX292/Oa/XKGEbkU++wfACx2x41jrhFSaILTSBL9WiTZ6NrFGuU7Q+t0pGP9OFm6fARysNgFqI8LW/xV2Cwq7htW4WnuiZhnUOoYBUt5a4X+63WGlvAunBVVkaP4O7HGArmnHu59Kyi/rlABHRX3MARx7YoYN4uUDTZPOIRWGdfwaVnO81uwSYH8VCj2jBuhRjzq1SXqJGA9dLJN7p4WK+hxHh4QW5zZJbnW0V0Ev9dHiQmkb3MgRQf/IBBlQrmjHw8dm5m+b9yiAboHYfpPNDgeqXO2u4wHXLmxSAhwun8LDZtwXw9DEJLxXqSEmXYjP1Ta1+OafmK4v5UjxwILSCrgpLMHHuY9kvjtK0HVy4zRczcgjH9Yk4T1QjenYAxAmW4Ik4QMSIDGnGLqGPrIHAPOprBqIzy6E5D8tdCUjD+SKDvYAhJePwgfNOPSPaOFuaSV5N/IlNdCLjPs/QGgFCt1jn/CAGp0BZI0KuJyWi0OkFD6kB0D7y9wOXfDu27agykEN/mZqaOukBxAoNZ/1BURk3aJ3jtOeUFRc+0xE9Bv4l0Vilf8CRCcob3kiPMIUwJHE4V3nYtqsdMMjTAFgik9TPqcbHmES4Fpq395IfoudTniESQBMcalKPZ3wGne+zHlS2UXdsSLJgNvh1XrDGUYBOHHixCmASr8BibEO48fxsmAAAAAASUVORK5CYII="
ICON_COPY = "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA9ElEQVR4nO3WQQqDMBSE4bmERXrRbntGkUpPM10VRGI1Ou9FyvwQutP3GQ0FtFG0JgC9eLYmELbGfIdQXIMtMUrIMPvtRPNVD6G4RjfDpO+MEoKWmIcY0hTzDNjVbs83ozouX6KnxZVd3cQoz/43gHsQZPM1U5/9ZzHcmGcVo4RMgo+SO+YpvmZKSC/A8MAaIs7+G4DxxGvGg0sOUWBqCoVkYhgNycIwA5KBYRYkGsNMSCSGEZDa/2Z/AeEVIbUZUsgQRYYUMkSRIYUMUWRIIUMUGVLIEEWGFDJE0fKeFCwYcqKQe9KQ4xnyK0OuCmGDZQgWfQC4nQCGD5qCoAAAAABJRU5ErkJggg=="
ICON_OCR = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAADM0lEQVR4nO1ZS2gTURS9oi5E6cJFTRFM0yQ1tTWNqBvduiu4E1y4UuhOsEp9LxVMFi4U3IgUbMFl2qS11v5s04BVQ8WFUMl7WVih6cJ8aj4bURQ/T26C40zahMykSScwB84imcm599zcmfcDMGDAgAHdw+yLe/fTF+LgvRXR/PCDMD1aE6ahmGgZXs/TNBwLq9U0DceWpd8PxfKaqI0xMJbZ9+nutiRv8cW9baMJUc4AUq2u/LemLQxgTMtIojoTltG41+pPCmsgWXcD1kBSYGyLX6MJ61jium0sKZD28VRZA6ah2Gu1+th2LWUMYMx/8W2BRJ9qA/bxVM7+JCXakRMbqitcLdonNvKxMQfbeCqrQSAljj7dyNMxWX8DjslCbCTmoknA8eyz6EBOfa67gY6pQmzMQVMBUeDYNDItOmfSdTfQOZPOx8YcNBUQBTpn06JrNiO65jJ1N9A1l8nHxhw0FRAFjj8v0DmfVSdAIpeBcqEg4XfUSDjns1J8TQVEAedCVnQjgyoNUL602QBbBxC7KpXoDhZiYw6qC5gXWMiEXYs54QrlhGsxW/l7fmDlMBD2e5MB5E12plIZVygXLsTOie5gRvU4ox2Uu2VVjwJlcVkbDYLuQTBpqeqPgfLp/59ZGnrf7QXdoj9yqqhtzgPlvcpnIdIDugXhD2Tt8wX63uyDG++bgfJfsu9HQJfwLO0BwlOydglI1yh7JXsOvoKHHwDdgUR6it44F6VrlF0raqNLoDsQ7pdV/zt4Vpuka7eiZqDsj6yN5kFX8Kw2AeXfFP1PWUhBwn7I2ugnuCOHQDdwsytbDlzlSPhV0A0If6neAHsLugDhRxRTB8LXgEZObk3ZqIzsj9r1MPIOKKvL7pe+lw8WtdHtmuXlDGaWpclcKFd634cyrkjKzc6Wvjd6rqiNPpa69cRiblmazC1kwrWZThdPHXAguzC2u+xgh/Mh5T92uibT6aoWNNsAZ7ULmoZfUnY0+qLe0ejbKu2NvrFlb/StRVsg0Vfx5m4Nzgfs1W7uItpG42Snt9fb/AkPVINWX5zs1AFH60iVyVd8xFSD8wGzL+7dluQNGDBgAGqJv+qEct16RhObAAAAAElFTkSuQmCC"

# ====================================================
# Data & Kamus Bahasa
# ====================================================
# Daftar bahasa (hasil irisan dari ke-5 mesin penerjemah: Google, Bing, iCiba, ModernMT, iTranslate)
TRANS_LANGS = {
    'af': 'afrikaans', 'az': 'azerbaijani', 'be': 'belarusian', 'bg': 'bulgarian',
    'bn': 'bengali', 'bs': 'bosnian', 'ca': 'catalan', 'ceb': 'cebuano',
    'cs': 'czech', 'cy': 'welsh', 'da': 'danish', 'de': 'german',
    'el': 'greek', 'en': 'english', 'et': 'estonian', 'fi': 'finnish',
    'ga': 'irish', 'gl': 'galician', 'gu': 'gujarati', 'ha': 'hausa',
    'hi': 'hindi', 'hr': 'croatian', 'ht': 'haitian creole', 'hu': 'hungarian',
    'hy': 'armenian', 'id': 'indonesian', 'ig': 'igbo', 'is': 'icelandic',
    'it': 'italian', 'ja': 'japanese', 'ka': 'georgian', 'kk': 'kazakh',
    'km': 'khmer', 'kn': 'kannada', 'ko': 'korean', 'la': 'latin',
    'lo': 'lao', 'lt': 'lithuanian', 'lv': 'latvian', 'mg': 'malagasy',
    'mi': 'maori', 'mk': 'macedonian', 'ml': 'malayalam', 'mr': 'marathi',
    'ms': 'malay', 'mt': 'maltese', 'my': 'myanmar', 'ne': 'nepali',
    'nl': 'dutch', 'pa': 'punjabi', 'pl': 'polish', 'ro': 'romanian',
    'ru': 'russian', 'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian',
    'so': 'somali', 'sq': 'albanian', 'st': 'sesotho', 'su': 'sundanese',
    'sv': 'swedish', 'sw': 'swahili', 'ta': 'tamil', 'te': 'telugu',
    'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu',
    'vi': 'vietnamese', 'yo': 'yoruba', 'zh-cn': 'chinese (simplified)', 'zu': 'zulu'
}

TRANS_LANGS_FORMATTED = {k: v.title() for k, v in TRANS_LANGS.items()}

# Untuk source language kita pakai dictionary yang sama
SRC_LANGS_FORMATTED = TRANS_LANGS_FORMATTED.copy()
# Opsi auto detect (Hanya mendukung huruf Alfabet/Latin)
SRC_LANGS_FORMATTED['auto_latin'] = 'Auto Detect (Alfabet/Latin)'
TRANS_ENGINES = ["google", "bing", "iciba", "modernMt", "itranslate"]
TRANS_ENGINES_FORMATTED = {k: k.title() if k != "modernMt" else "ModernMT" for k in TRANS_ENGINES}

CONFIG_FILE = "config.json"

# Status Global
doctr_predictor = None

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
    global current_source_lang, current_trans_engine, current_dest_lang
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                current_source_lang = data.get("source_lang")
                current_trans_engine = data.get("trans_engine")
                current_dest_lang = data.get("dest_lang")
        except:
            pass

def save_config(src, trans_eng, dst):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "source_lang": src,
                "trans_engine": trans_eng,
                "dest_lang": dst
            }, f)
    except:
        pass

def init_reader():
    global doctr_predictor
    if doctr_predictor is None:
        from doctr.models import ocr_predictor
        doctr_predictor = ocr_predictor(pretrained=True)

# ====================================================
# Preprocessing Teks OCR
# Merapikan output OCR sebelum dikirim ke penerjemah:
# - Filter noise/artefak (karakter tunggal, UI element salah deteksi)
# - Gabung baris terpotong menjadi kalimat utuh (geometri bounding box)
# - Pisahkan header/label dari konten paragraf
# - Bersihkan spasi dan tanda baca
# ====================================================

def extract_lines_with_geometry(result):
    """
    Mengekstrak semua baris dari docTR beserta informasi geometri dan confidence.
    Geometri digunakan untuk menentukan kedekatan spasial antar baris.
    """
    all_lines = []
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                words = line.words
                if not words:
                    continue
                line_text = " ".join([w.value for w in words])
                avg_confidence = sum(w.confidence for w in words) / len(words)

                # Ambil geometri baris (koordinat relatif 0-1)
                geo = line.geometry
                y_min = geo[0][1]
                y_max = geo[1][1]
                x_min = geo[0][0]
                x_max = geo[1][0]
                line_height = y_max - y_min

                all_lines.append({
                    "text": line_text.strip(),
                    "confidence": avg_confidence,
                    "word_count": len(words),
                    "y_min": y_min,
                    "y_max": y_max,
                    "x_min": x_min,
                    "x_max": x_max,
                    "height": line_height,
                })

    # Urutkan berdasarkan posisi vertikal (atas ke bawah)
    all_lines.sort(key=lambda l: l["y_min"])
    return all_lines


def _is_noise_line(line_info):
    """
    Mendeteksi baris noise/artefak OCR.
    Noise: karakter tunggal non-angka, baris kosong, confidence sangat rendah.
    """
    text = line_info["text"].strip()
    conf = line_info["confidence"]

    # Baris kosong
    if not text:
        return True
    # Karakter tunggal yang bukan angka (kemungkinan artefak UI)
    if len(text) == 1 and text not in '0123456789':
        return True
    # Confidence sangat rendah
    if conf < 0.3:
        return True
    return False


def _is_sentence_ending(text):
    """Memeriksa apakah teks berakhir dengan tanda baca akhir kalimat."""
    text = text.rstrip()
    if not text:
        return False
    # Iterasi dari belakang, lewati kutip/bracket penutup
    for ch in reversed(text[-5:]):
        if ch in '.!?':
            return True
        if ch in '"\')]':
            continue
        break
    return False


def _is_continuation_line(text):
    """
    Memeriksa apakah baris PASTI lanjutan dari baris sebelumnya.
    Indikator kuat: dimulai dengan huruf kecil.
    """
    text = text.strip()
    if not text:
        return False
    if text[0].islower():
        return True
    return False


def _is_standalone_line(text):
    """
    Memeriksa apakah teks adalah baris mandiri (header/label/mapping)
    yang TIDAK boleh digabung dengan baris lain.
    """
    text = text.strip()
    if not text:
        return False

    words = text.split()
    word_count = len(words)

    # Baris sangat pendek (1-3 kata) tanpa tanda baca akhir = label/header
    if word_count <= 3 and not _is_sentence_ending(text):
        return True

    # Baris pendek (4-5 kata) yang terlihat seperti judul (mayoritas huruf besar awal)
    if word_count <= 5 and not _is_sentence_ending(text):
        capitalized = sum(1 for w in words if w[0].isupper() or not w[0].isalpha())
        if capitalized >= word_count * 0.7:
            return True

    # Baris dengan pola mapping/panah yang pendek
    if re.search(r'[→]', text) and word_count <= 8:
        return True

    # Baris yang dimulai dengan = atau - (item daftar)
    if text.startswith('= ') or text.startswith('- '):
        return True

    return False


def _calculate_vertical_gap(line1, line2):
    """
    Menghitung rasio jarak vertikal antara dua baris terhadap tinggi rata-rata baris.
    Nilai > 1.0 = ada jarak signifikan = kemungkinan paragraf berbeda.
    """
    gap = line2["y_min"] - line1["y_max"]
    avg_height = (line1["height"] + line2["height"]) / 2
    if avg_height == 0:
        return 0
    return gap / avg_height


def _reconstruct_smart(lines):
    """
    Merekonstruksi teks dari baris-baris OCR menjadi kalimat/paragraf utuh.

    Aturan penggabungan:
    1. Filter noise terlebih dahulu
    2. GABUNG jika: baris saat ini dimulai huruf kecil DAN gap kecil (< 0.5)
    3. GABUNG jika: baris sebelumnya berakhir koma/titik-koma DAN gap kecil
    4. GABUNG jika: baris sebelumnya TIDAK berakhir tanda baca DAN gap sangat kecil (< 0.5)
    5. PISAH jika: baris saat ini adalah item daftar atau baris mandiri
    6. PISAH jika: baris sebelumnya berakhir tanda baca akhir kalimat
    """
    if not lines:
        return ""

    # Langkah 1: Filter noise
    clean_lines = [l for l in lines if not _is_noise_line(l)]
    if not clean_lines:
        return ""

    # Langkah 2: Rekonstruksi
    result_units = []
    current_parts = [clean_lines[0]["text"]]

    for i in range(1, len(clean_lines)):
        prev_line = clean_lines[i - 1]
        curr_line = clean_lines[i]
        prev_text = prev_line["text"]
        curr_text = curr_line["text"]

        v_gap = _calculate_vertical_gap(prev_line, curr_line)

        should_merge = False

        # Kasus 1: Baris saat ini adalah item mandiri → SELALU pisahkan
        if _is_standalone_line(curr_text):
            should_merge = False

        # Kasus 2: Baris saat ini dimulai huruf kecil → GABUNG jika gap kecil
        elif _is_continuation_line(curr_text):
            if v_gap < 0.5:
                should_merge = True
            else:
                # Gap besar meski huruf kecil → kemungkinan OCR error, tetap pisahkan
                should_merge = False

        # Kasus 3: Baris sebelumnya berakhir koma/titik-koma → GABUNG jika dekat
        elif prev_text.rstrip() and prev_text.rstrip()[-1] in ',;':
            if v_gap < 0.5:
                should_merge = True

        # Kasus 4: Baris sebelumnya TIDAK berakhir tanda baca akhir kalimat
        elif not _is_sentence_ending(prev_text):
            # Hanya gabung jika baris sangat dekat
            if v_gap < 0.5:
                should_merge = True

        # Kasus 5: Baris sebelumnya berakhir tanda baca → PISAHKAN (default)

        if should_merge:
            current_parts.append(curr_text)
        else:
            result_units.append(" ".join(current_parts))
            current_parts = [curr_text]

    # Simpan sisa terakhir
    if current_parts:
        result_units.append(" ".join(current_parts))

    return "\n\n".join(result_units)


def _clean_ocr_text(text):
    """Membersihkan artefak/noise umum dari hasil OCR setelah rekonstruksi."""
    # Hapus spasi berlebihan (kecuali newline)
    text = re.sub(r'[^\S\n]{2,}', ' ', text)
    # Perbaiki spasi sebelum tanda baca akhir kalimat
    text = re.sub(r'\s+([.!?])', r'\1', text)
    # Normalisasi paragraf
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    text = '\n\n'.join(paragraphs)
    return text.strip()


def preprocess_for_translation(result):
    """
    Pipeline utama: hasil OCR docTR -> teks siap terjemah.

    Langkah:
    1. Ekstrak baris dengan geometri (posisi, confidence)
    2. Rekonstruksi cerdas (gabung kalimat terpotong, pisahkan paragraf)
    3. Bersihkan artefak teks
    """
    lines = extract_lines_with_geometry(result)
    reconstructed = _reconstruct_smart(lines)
    cleaned = _clean_ocr_text(reconstructed)
    return cleaned


# ====================================================
# Deteksi Keluarga Skrip Otomatis
# Mengklasifikasikan teks sebagai Latin-like (Latin + Cyrillic)
# atau Non-Latin (CJK, Arab, Thai, dll)
# ====================================================

def detect_script_from_text(text):
    """
    Mendeteksi keluarga skrip dominan dari teks berdasarkan analisis Unicode.
    
    Kategori:
    - "latin" : Latin + Cyrillic (visual mirip, dikategorikan sama)
    - "cjk"   : Chinese/Japanese/Korean Kanji + Kana
    - "korean" : Korean Hangul
    - "arabic" : Arabic/Hebrew
    - "thai"  : Thai
    - "devanagari" : Hindi/Sanskrit/Nepali
    - "unknown" : Tidak bisa ditentukan
    
    Return:
        dict: family, is_latin_like, confidence, distribution
    """
    if not text or not text.strip():
        return {"family": "unknown", "is_latin_like": True, "confidence": 0.0, "distribution": {}}
    
    counts = {
        "latin": 0, "cyrillic": 0, "cjk": 0, "japanese_kana": 0,
        "korean": 0, "arabic": 0, "thai": 0, "devanagari": 0, "other": 0,
    }
    total_letters = 0
    
    for char in text:
        if char.isspace() or char.isdigit():
            continue
        if char in '.,;:!\'\"()[]{}/-_=+*&^%$#@~`<>|\\':
            continue
        
        cp = ord(char)
        total_letters += 1
        
        # Latin (Basic + Extended A/B + Supplement + Extended Additional)
        if (0x0041 <= cp <= 0x007A) or (0x00C0 <= cp <= 0x024F) or (0x1E00 <= cp <= 0x1EFF):
            counts["latin"] += 1
        # Cyrillic (Basic + Supplement)
        elif 0x0400 <= cp <= 0x052F:
            counts["cyrillic"] += 1
        # CJK Unified Ideographs
        elif (0x4E00 <= cp <= 0x9FFF) or (0x3400 <= cp <= 0x4DBF) or (0x20000 <= cp <= 0x2A6DF):
            counts["cjk"] += 1
        # Hiragana + Katakana (Japanese)
        elif (0x3040 <= cp <= 0x30FF) or (0x31F0 <= cp <= 0x31FF):
            counts["japanese_kana"] += 1
        # Hangul (Korean)
        elif (0xAC00 <= cp <= 0xD7AF) or (0x1100 <= cp <= 0x11FF) or (0x3130 <= cp <= 0x318F):
            counts["korean"] += 1
        # Arabic + Hebrew
        elif (0x0590 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F):
            counts["arabic"] += 1
        # Thai
        elif 0x0E00 <= cp <= 0x0E7F:
            counts["thai"] += 1
        # Devanagari
        elif 0x0900 <= cp <= 0x097F:
            counts["devanagari"] += 1
        else:
            counts["other"] += 1
    
    if total_letters == 0:
        return {"family": "unknown", "is_latin_like": True, "confidence": 0.0, "distribution": {}}
    
    # Gabungkan Latin + Cyrillic sebagai "Latin-like"
    latin_like_count = counts["latin"] + counts["cyrillic"]
    cjk_total = counts["cjk"] + counts["japanese_kana"]
    
    # Distribusi persentase
    distribution = {}
    if counts["latin"] > 0:
        distribution["latin"] = round(counts["latin"] / total_letters * 100, 1)
    if counts["cyrillic"] > 0:
        distribution["cyrillic"] = round(counts["cyrillic"] / total_letters * 100, 1)
    if cjk_total > 0:
        distribution["cjk"] = round(cjk_total / total_letters * 100, 1)
    if counts["korean"] > 0:
        distribution["korean"] = round(counts["korean"] / total_letters * 100, 1)
    if counts["arabic"] > 0:
        distribution["arabic"] = round(counts["arabic"] / total_letters * 100, 1)
    if counts["thai"] > 0:
        distribution["thai"] = round(counts["thai"] / total_letters * 100, 1)
    if counts["devanagari"] > 0:
        distribution["devanagari"] = round(counts["devanagari"] / total_letters * 100, 1)
    if counts["other"] > 0:
        distribution["other"] = round(counts["other"] / total_letters * 100, 1)
    
    # Tentukan keluarga dominan
    candidates = {
        "latin": latin_like_count, "cjk": cjk_total,
        "korean": counts["korean"], "arabic": counts["arabic"],
        "thai": counts["thai"], "devanagari": counts["devanagari"],
    }
    
    dominant_family = max(candidates, key=candidates.get)
    dominant_count = candidates[dominant_family]
    confidence = round(dominant_count / total_letters * 100, 1)
    is_latin_like = dominant_family == "latin"
    
    return {
        "family": dominant_family,
        "is_latin_like": is_latin_like,
        "confidence": confidence,
        "distribution": distribution,
    }


def detect_script_from_ocr_confidence(result):
    """
    Mendeteksi kemungkinan teks non-Latin berdasarkan confidence OCR docTR.
    
    Logika: docTR dilatih untuk Latin. Jika teks aslinya non-Latin,
    confidence rata-rata akan jauh lebih rendah.
    
    Kalibrasi:
    - Latin terendah (Cyrillic): avg_conf ~0.647
    - Non-Latin tertinggi (JP/AR): avg_conf ~0.509/0.532
    - Threshold: 0.60
    
    Return:
        dict: likely_non_latin, avg_confidence, metrics
    """
    all_confidences = []
    short_word_count = 0
    total_word_count = 0
    
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    all_confidences.append(word.confidence)
                    total_word_count += 1
                    if len(word.value) <= 2:
                        short_word_count += 1
    
    if not all_confidences:
        return {"likely_non_latin": False, "avg_confidence": 0.0, "metrics": {}}
    
    avg_conf = sum(all_confidences) / len(all_confidences)
    short_ratio = short_word_count / total_word_count if total_word_count > 0 else 0
    
    metrics = {
        "avg_confidence": round(avg_conf, 3),
        "short_word_ratio": round(short_ratio, 3),
        "total_words": total_word_count,
    }
    
    # Heuristik: confidence rendah = kemungkinan teks non-Latin
    # Threshold 0.60 memisahkan Latin (>=0.647) dari Non-Latin (<=0.532)
    likely_non_latin = avg_conf < 0.60 or (avg_conf < 0.70 and short_ratio > 0.4)
    
    return {
        "likely_non_latin": likely_non_latin,
        "avg_confidence": round(avg_conf, 3),
        "metrics": metrics,
    }

# ====================================================
# Komponen UI
# ====================================================

class ResultOverlay:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Screen Translator")
        self.window.attributes('-topmost', True)
        
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook untuk sistem Tab
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # --- Tab 1: Source Text ---
        self.source_frame = tk.Frame(self.notebook)
        self.notebook.add(self.source_frame, text="Source Text")
        
        src_text_frame = tk.Frame(self.source_frame)
        src_text_frame.pack(fill=tk.BOTH, expand=True)
        
        source_scroll = tk.Scrollbar(src_text_frame)
        source_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.source_widget = tk.Text(src_text_frame, font=('Arial', 12), wrap=tk.WORD, yscrollcommand=source_scroll.set, borderwidth=1, relief="solid", width=50, height=5)
        self.source_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        source_scroll.config(command=self.source_widget.yview)
        
        # --- Tab 2: Translation Result ---
        self.trans_frame = tk.Frame(self.notebook)
        self.notebook.add(self.trans_frame, text="Translation Result")
        
        trans_text_frame = tk.Frame(self.trans_frame)
        trans_text_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scroll = tk.Scrollbar(trans_text_frame)
        trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_widget = tk.Text(trans_text_frame, font=('Arial', 12), wrap=tk.WORD, yscrollcommand=trans_scroll.set, borderwidth=1, relief="solid", width=50, height=5)
        self.trans_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll.config(command=self.trans_widget.yview)
        
        self.source_text = ""
        self.translated_text = ""
        
        # State Awal: OCR Loading
        self._set_text(self.source_widget, "Sedang mendeteksi gambar...")
        self._set_text(self.trans_widget, "Menunggu teks sumber...")
        
        # Fokus ke tab Source Text awal mula
        self.notebook.select(self.source_frame)

    def _resize_window(self, text):
        # Menghitung jumlah baris berdasarkan panjang karakter, max 20 baris
        lines = sum(len(line) // 50 + 1 for line in text.split('\n'))
        num_lines = min(max(lines, 3), 20)
        self.source_widget.config(height=num_lines)
        self.trans_widget.config(height=num_lines)
        # Update tampilan window agar secara otomatis beradaptasi dengan height yang baru
        self.window.update_idletasks()

    def _set_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)
        
    def set_ocr_result(self, source_text):
        self.source_text = source_text if source_text else "Tidak ada teks yang terdeteksi."
        self._set_text(self.source_widget, self.source_text)
        self._set_text(self.trans_widget, "Sedang diproses (menerjemahkan teks)..." if source_text else "Terjemahan dibatalkan.")
        
        if source_text:
            self._resize_window(self.source_text)
            
        self.notebook.select(self.source_frame)

    def set_translation_result(self, translated_text):
        self.translated_text = translated_text if translated_text else "Terjemahan gagal atau kosong."
        self._set_text(self.trans_widget, self.translated_text)
        
        if self.translated_text:
            self._resize_window(self.translated_text)
            
        self.notebook.select(self.trans_frame)

class RectangleSelector:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.3)
        self.window.configure(bg='black')
        self.window.overrideredirect(True)
        
        # Paksa overlay agar selalu berada di posisi paling atas
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
            
            # Simpan gambar ke parent (App)
            self.parent.last_image = img
            
            # Tampilkan UI Skeleton langsung setelah lepas mouse
            self.parent.event_generate("<<StartOCR>>", when="tail")
            
            # Panggil fungsi processing di App
            if hasattr(self.parent, 'app_instance'):
                threading.Thread(target=self.parent.app_instance.process_ocr_and_translate, args=(img,), daemon=True).start()
        else:
            self.on_escape()
            
    def on_escape(self, event=None):
        self.window.destroy()
        
# ====================================================
# Aplikasi Utama
# ====================================================

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Translator - Settings")
        self.root.geometry("480x450")
        self.root.app_instance = self
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Binding Event Custom
        self.root.bind("<<TriggerHotkey>>", self.on_hotkey_triggered)
        self.root.bind("<<StartOCR>>", self.on_start_ocr)
        self.root.bind("<<ShowOCRResult>>", self.on_show_ocr_result)
        self.root.bind("<<UpdateTranslation>>", self.on_update_translation)
        self.root.bind("<<ReRunTrans>>", self.on_rerun_trans)
        
        tk.Label(self.root, text="Global Application Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Peta Balik untuk ID
        self.src_map = {name: code for code, name in SRC_LANGS_FORMATTED.items()}
        self.dst_map = {name: code for code, name in TRANS_LANGS_FORMATTED.items()}
        self.trans_eng_map = {name: code for code, name in TRANS_ENGINES_FORMATTED.items()}
        
        # --- 1. Bahasa Sumber (OCR) ---
        tk.Label(self.root, text="1. Source Language:").pack(anchor='w', padx=25)
        self.src_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.src_combo.pack(padx=25, pady=(0, 10))
        # Urutkan: bahasa biasa dulu (alphabetical), lalu opsi Auto di bawah
        auto_options = ['Auto Detect (Alfabet/Latin)']
        regular_langs = sorted([k for k in self.src_map.keys() if k not in auto_options])
        self.src_combo['values'] = regular_langs + auto_options
        default_src_name = SRC_LANGS_FORMATTED.get(current_source_lang, "English")
        if default_src_name in self.src_combo['values']:
            self.src_combo.set(default_src_name)
            
        # --- 2. Mesin Penerjemah ---
        tk.Label(self.root, text="2. Translation Engine:").pack(anchor='w', padx=25)
        self.trans_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.trans_combo.pack(padx=25, pady=(0, 10))
        self.trans_combo['values'] = sorted(list(self.trans_eng_map.keys()))
        default_trans_name = TRANS_ENGINES_FORMATTED.get(current_trans_engine, "Google")
        if default_trans_name in self.trans_combo['values']:
            self.trans_combo.set(default_trans_name)
            
        # --- 3. Bahasa Tujuan (Terjemahan) ---
        tk.Label(self.root, text="3. Target Language:").pack(anchor='w', padx=25)
        self.dst_combo = ttk.Combobox(self.root, state="readonly", width=50)
        self.dst_combo.pack(padx=25, pady=(0, 10))
        
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
        
        # State awal
        self.root.last_ocr_text = ""
        self.root.last_translation = ""
        self.root.last_image = None
        self.root.requested_ocr_engine = ""
        self.root.requested_trans_engine = ""
        self.is_loading = False

    def refresh_ui_from_config(self):
        """Memperbarui nilai di UI setelah config dimuat dari file"""
        src_name = SRC_LANGS_FORMATTED.get(current_source_lang)
        if src_name in self.src_combo['values']:
            self.src_combo.set(src_name)
            
        trans_name = TRANS_ENGINES_FORMATTED.get(current_trans_engine)
        if trans_name in self.trans_combo['values']:
            self.trans_combo.set(trans_name)
            
        dst_name = TRANS_LANGS_FORMATTED.get(current_dest_lang)
        if dst_name in self.dst_combo['values']:
            self.dst_combo.set(dst_name)

    def on_closing(self):
        self.root.destroy()
        os._exit(0)

    def load_model_initial(self):
        self.is_loading = True
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Loading OCR Model... Please wait.", fg="blue")
        
        def _bg_load():
            try:
                init_reader()
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
        global current_source_lang, current_trans_engine, current_dest_lang
        
        src_name = self.src_combo.get()
        trans_eng_name = self.trans_combo.get()
        dst_name = self.dst_combo.get()

        if not all([src_name, trans_eng_name, dst_name]):
            messagebox.showwarning("Warning", "Please select all options before saving!")
            return

        src_code = self.src_map[src_name]
        trans_eng_code = self.trans_eng_map[trans_eng_name]
        dst_code = self.dst_map[dst_name]
        
        save_config(src_code, trans_eng_code, dst_code)
        
        current_trans_engine = trans_eng_code
        current_dest_lang = dst_code
        
        # docTR reload / config refresh
        if src_code != current_source_lang:
            self.is_loading = True
            self.save_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Saving settings...", fg="blue")
            
            def _bg_apply():
                try:
                    global current_source_lang
                    current_source_lang = src_code
                    # OCR reload no longer needed since docTR is lang-agnostic
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

    def on_start_ocr(self, event=None):
        if hasattr(self, 'result_overlay') and self.result_overlay.window.winfo_exists():
            self.result_overlay.window.destroy()
        self.result_overlay = ResultOverlay(self.root)

    def on_show_ocr_result(self, event=None):
        if hasattr(self, 'result_overlay') and self.result_overlay.window.winfo_exists():
            self.result_overlay.set_ocr_result(self.root.last_ocr_text)

    def process_ocr_and_translate(self, img):
        global current_ocr_engine, current_source_lang, current_trans_engine, current_dest_lang
        try:
            import translators as ts
            
            ocr_text = ""
            script_warning = ""
            
            # 1. Memproses OCR
            if doctr_predictor:
                import io
                from doctr.io import DocumentFile
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                doc = DocumentFile.from_images(img_bytes)
                result = doctr_predictor(doc)
                ocr_text = preprocess_for_translation(result)
                
                # 1b. Deteksi skrip otomatis jika mode auto
                if current_source_lang == 'auto_latin':
                    script_check = detect_script_from_ocr_confidence(result)
                    is_non_latin = script_check["likely_non_latin"]
                    avg_c = script_check['avg_confidence']
                    
                    # Peringatan jika skrip terdeteksi Non-Latin (docTR tidak optimal untuk ini)
                    if is_non_latin:
                        script_warning = (
                            f"[Peringatan] Teks terdeteksi Non-Latin (confidence OCR: {avg_c:.0%}).\n"
                            f"Model OCR docTR saat ini hanya optimal untuk huruf Latin.\n"
                            f"Hasil pembacaan kemungkinan besar tidak akurat.\n\n"
                        )
            
            # Tampilkan hasil OCR ke UI segera (dengan peringatan jika ada)
            self.root.last_ocr_text = script_warning + ocr_text
            self.root.event_generate("<<ShowOCRResult>>", when="tail")
            
            # 2. Menerjemahkan Teks (gunakan teks tanpa peringatan)
            translated_text = ""
            if ocr_text.strip():
                try:
                    # Untuk mode auto, kirim 'auto' ke mesin penerjemah
                    if current_source_lang == 'auto_latin':
                        src = 'auto'
                    else:
                        src = current_source_lang
                    translated_text = ts.translate_text(
                        query_text=ocr_text, 
                        translator=current_trans_engine,
                        from_language=src, 
                        to_language=current_dest_lang
                    )
                    # Tambahkan peringatan skrip ke terjemahan juga
                    if script_warning:
                        translated_text = script_warning + translated_text
                except Exception as e:
                    translated_text = f"Terjemahan gagal menggunakan {current_trans_engine}:\n{e}"
            else:
                translated_text = "Tidak ada teks yang terdeteksi oleh mesin OCR."
            
            # Memperbarui UI dengan hasil terjemahan
            self.root.last_translation = translated_text
            self.root.event_generate("<<UpdateTranslation>>", when="tail")
            
        except Exception as e:
            print(f"Error pada processing: {e}")

    def on_rerun_ocr(self, event=None):
        new_eng = self.root.requested_ocr_engine
        if not new_eng or not self.root.last_image: return
        
        if hasattr(self, 'result_overlay') and self.result_overlay.window.winfo_exists():
            self.result_overlay._set_text(self.result_overlay.source_widget, f"Memuat {new_eng} dan membaca ulang gambar...")
            self.result_overlay.notebook.select(self.result_overlay.source_frame)
            self.result_overlay.ocr_btn.config(state=tk.DISABLED)
            
        def _bg_rerun():
            try:
                init_reader(new_eng, current_source_lang)
                global current_ocr_engine
                current_ocr_engine = new_eng
                
                # Update combobox secara diam-diam
                if new_eng in self.ocr_combo['values']:
                    self.ocr_combo.set(new_eng)
                
                self.process_ocr_and_translate(self.root.last_image)
            except Exception as e:
                print("Error rerun OCR:", e)
                
        threading.Thread(target=_bg_rerun, daemon=True).start()

    def on_rerun_trans(self, event=None):
        new_trans = self.root.requested_trans_engine
        if not new_trans or not self.root.last_ocr_text: return
        
        if hasattr(self, 'result_overlay') and self.result_overlay.window.winfo_exists():
            self.result_overlay._set_text(self.result_overlay.trans_widget, f"Menerjemahkan ulang menggunakan {TRANS_ENGINES_FORMATTED.get(new_trans, new_trans)}...")
            self.result_overlay.notebook.select(self.result_overlay.trans_frame)
            self.result_overlay.trans_btn.config(state=tk.DISABLED)
            
        def _bg_rerun_trans():
            try:
                import translators as ts
                global current_trans_engine
                current_trans_engine = new_trans
                
                trans_name = TRANS_ENGINES_FORMATTED.get(new_trans)
                if trans_name in self.trans_combo['values']:
                    self.trans_combo.set(trans_name)
                    
                src = 'auto' if current_source_lang in ('auto_latin', 'auto_nonlatin') else current_source_lang
                translated_text = ts.translate_text(
                    query_text=self.root.last_ocr_text, 
                    translator=current_trans_engine,
                    from_language=src, 
                    to_language=current_dest_lang
                )
                self.root.last_translation = translated_text
                self.root.event_generate("<<UpdateTranslation>>", when="tail")
            except Exception as e:
                self.root.last_translation = f"Terjemahan gagal:\n{e}"
                self.root.event_generate("<<UpdateTranslation>>", when="tail")
                
        threading.Thread(target=_bg_rerun_trans, daemon=True).start()

    def on_update_translation(self, event=None):
        if hasattr(self, 'result_overlay') and self.result_overlay.window.winfo_exists():
            self.result_overlay.set_translation_result(self.root.last_translation)

# ====================================================
# Pendengar Hotkey Global
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
