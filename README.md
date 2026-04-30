<div align="center">
  <h1>🌐 Screen Translator OCR</h1>
  <p>Alat terjemahan layar berbasis Python yang tangkas, gratis, dan mudah digunakan. Mendukung pemilihan area layar kustom, OCR luring (offline), dan terjemahan langsung dengan multi-engine.</p>
  <p><b>⚠️ KHUSUS WINDOWS ⚠️</b></p>
</div>

---

## 📖 Deskripsi
**Screen Translator OCR** adalah aplikasi utilitas desktop yang dirancang **khusus untuk sistem operasi Windows**. Aplikasi ini memungkinkan Anda menerjemahkan teks apa pun di layar komputer Anda secara instan. Cukup tekan tombol pintas (hotkey) global, seret kotak seleksi pada area layar yang berisi teks, dan aplikasi akan secara otomatis mengekstrak teks menggunakan teknologi OCR dan menerjemahkannya menggunakan berbagai pilihan mesin penerjemah gratis.

Aplikasi ini sangat cocok untuk menerjemahkan komik, game, dokumen gambar, atau aplikasi perangkat lunak yang tidak mendukung penyalinan teks secara langsung.

## ✨ Fitur Utama
- **Pemilihan Area Layar Kustom**: Seret dan pilih area manapun di layar Anda secara bebas.
- **Dukungan Dual OCR Engine**:
  - **EasyOCR**: Akurasi tinggi untuk berbagai bahasa.
  - **RapidOCR**: Sangat cepat dan ringan.
- **10+ Mesin Penerjemah Gratis**: Pilih mesin favorit Anda seperti Google, Bing, Yandex, Papago, Argos, Caiyun, iTranslate, Lara, SysTran, dan Youdao.
- **Dynamic Language Filtering**: Daftar bahasa target otomatis menyesuaikan dengan kemampuan mesin penerjemah yang dipilih.
- **Startup Instan**: Menggunakan teknik *Lazy Loading* sehingga aplikasi muncul seketika saat dijalankan tanpa menunggu modul berat dimuat.
- **Hotkey Global**: Cukup tekan `Ctrl + Shift + Alt + Z` di mana saja untuk memulai seleksi layar.
- **Antarmuka Minimalis (GUI)**: Pengaturan yang mudah digunakan melalui antarmuka Tkinter dengan status real-time.
- **Ringan dan Cepat**: Menggunakan Multi-threading agar aplikasi tetap responsif saat memproses data.

## 🛠️ Prasyarat
Sebelum menginstal aplikasi ini, pastikan sistem Anda telah terinstal:
- **Python 3.8** atau yang lebih baru.
- **Sistem Operasi Windows (Wajib)**: Mengandalkan modul API Windows (`pywin32`) untuk transparansi *overlay*.

## 🚀 Cara Instalasi

1. **Kloning Repositori**
   ```bash
   git clone https://github.com/username/screen-translator-ocr.git
   cd screen-translator-ocr
   ```

2. **Instal Dependensi**
   Instal semua pustaka yang dibutuhkan melalui `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *Catatan:* Pada saat pertama kali dijalankan, mesin OCR mungkin akan mengunduh model bahasa yang diperlukan.

## 💻 Cara Penggunaan

1. **Jalankan Aplikasi**
   ```bash
   python main.py
   ```
2. **Atur Konfigurasi**
   - Jendela pengaturan akan muncul secara instan.
   - Pilih **OCR Engine** yang ingin digunakan.
   - Pilih **Source Language** (bahasa teks di layar).
   - Pilih **Translation Engine**.
   - Pilih **Target Language** (daftar akan otomatis memfilter bahasa yang didukung mesin tersebut).
   - Klik **Save & Apply Settings**. Tunggu hingga status menunjukkan **"Model Ready"**.
3. **Mulai Menerjemahkan**
   - Tekan tombol pintas global: `Ctrl + Shift + Alt + Z`.
   - Klik dan seret *mouse* untuk membuat kotak seleksi pada teks.
   - Lepaskan klik *mouse*, dan jendela hasil terjemahan akan muncul!

## 📚 Teknologi yang Digunakan
- [pynput](https://pypi.org/project/pynput/) - Menangani *hotkey* global.
- [mss](https://pypi.org/project/mss/) - Tangkapan layar super cepat.
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) & [RapidOCR](https://github.com/RapidAI/RapidOCR) - Mesin OCR luring.
- [translators](https://github.com/UlionTse/translators) - Integrasi berbagai API penerjemah gratis.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Antarmuka pengguna.

## 🤝 Kontribusi
Kontribusi sangat dipersilakan! Silakan buka *issue* atau kirimkan *pull request*.

## 📝 Lisensi
Proyek ini dilisensikan di bawah lisensi MIT.
