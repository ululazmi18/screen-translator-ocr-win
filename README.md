<div align="center">
  <h1>🌐 Screen Translator OCR</h1>
  <p>Alat terjemahan layar berbasis Python yang tangkas, gratis, dan mudah digunakan. Mendukung pemilihan area layar kustom, OCR luring (offline), dan terjemahan langsung.</p>
  <p><b>⚠️ KHUSUS WINDOWS ⚠️</b></p>
</div>

---

## 📖 Deskripsi
**Screen Translator OCR** adalah aplikasi utilitas desktop yang dirancang **khusus untuk sistem operasi Windows**. Aplikasi ini memungkinkan Anda menerjemahkan teks apa pun di layar komputer Anda secara instan. Cukup tekan tombol pintas (hotkey) global, seret kotak seleksi pada area layar yang berisi teks, dan aplikasi akan secara otomatis mengekstrak teks menggunakan teknologi *Optical Character Recognition* (OCR) dari EasyOCR dan menerjemahkannya menggunakan Google Translate.

Aplikasi ini sangat cocok untuk menerjemahkan komik, game, dokumen gambar, atau aplikasi perangkat lunak yang tidak mendukung penyalinan teks secara langsung.

## ✨ Fitur Utama
- **Pemilihan Area Layar Kustom**: Seret dan pilih area manapun di layar Anda secara bebas.
- **OCR Luring (Offline)**: Ekstraksi teks menggunakan EasyOCR yang memproses gambar secara lokal sehingga lebih privat.
- **Terjemahan Instan**: Menggunakan Google Translate API untuk menerjemahkan teks ke ratusan bahasa secara instan.
- **Hotkey Global**: Cukup tekan `Ctrl + Shift + Alt + Z` di mana saja untuk memulai seleksi layar tanpa harus membuka jendela aplikasi secara manual.
- **Antarmuka Minimalis (GUI)**: Pengaturan bahasa sumber (OCR) dan bahasa target (Terjemahan) yang mudah melalui antarmuka Tkinter.
- **Ringan dan Cepat**: Menggunakan Multi-threading agar aplikasi tidak *freeze* atau *Not Responding* saat memproses terjemahan.

## 🛠️ Prasyarat
Sebelum menginstal aplikasi ini, pastikan sistem Anda telah terinstal:
- **Python 3.8** atau yang lebih baru.
- **Sistem Operasi Windows (Wajib)**: Aplikasi ini dirancang **khusus dan eksklusif untuk Windows**. Karena mengandalkan modul API Windows (`pywin32`) untuk transparansi *overlay* dan penanganan antarmuka, aplikasi ini **TIDAK** dapat berjalan di sistem operasi macOS maupun Linux.

## 🚀 Cara Instalasi

1. **Kloning Repositori**
   Buka terminal atau command prompt Anda, lalu jalankan:
   ```bash
   git clone https://github.com/username/screen-translator-ocr.git
   cd screen-translator-ocr
   ```

2. **Buat Virtual Environment (Opsional namun disarankan)**
   ```bash
   python -m venv venv
   # Aktivasi di Windows:
   venv\Scripts\activate
   ```

3. **Instal Dependensi**
   Instal semua pustaka yang dibutuhkan melalui `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *Catatan:* Pada saat pertama kali dijalankan, EasyOCR mungkin akan mengunduh model bahasa yang dipilih. Pastikan koneksi internet stabil.

## 💻 Cara Penggunaan

1. **Jalankan Aplikasi**
   Jalankan file utama menggunakan Python:
   ```bash
   python main.py
   ```
2. **Atur Bahasa**
   - Jendela pengaturan ("Screen Translator - Settings") akan muncul.
   - Pilih **Screen Text Language (OCR)** (bahasa dari teks yang ada di gambar/layar).
   - Pilih **Translate To** (bahasa target terjemahan).
   - Klik **Save & Apply Settings**. Tunggu hingga status di bawah tombol menunjukkan **"Model Ready"**.
3. **Mulai Menerjemahkan**
   - Biarkan aplikasi tetap berjalan di latar belakang (Anda bisa *minimize* jendela pengaturannya).
   - Tekan tombol pintas global: `Ctrl + Shift + Alt + Z`.
   - Layar akan sedikit meredup. Klik dan seret (drag) *mouse* Anda untuk membuat kotak seleksi pada teks yang ingin diterjemahkan.
   - Lepaskan klik *mouse*, dan jendela hasil ("Translation Result") akan muncul menampilkan teks asli beserta terjemahannya!
   - Terdapat tombol untuk menyalin teks asli maupun hasil terjemahan secara praktis.

## 📚 Teknologi yang Digunakan
- [pynput](https://pypi.org/project/pynput/) - Mendengarkan dan menangkap *hotkey* global.
- [mss](https://pypi.org/project/mss/) - Modul tangkapan layar (screenshot) lintas platform yang sangat cepat.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI bawaan Python untuk antarmuka pengguna.
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Mesin OCR yang tangguh dan mendukung banyak bahasa.
- [googletrans](https://pypi.org/project/googletrans/) - API Python tidak resmi untuk Google Translate.

## 🤝 Kontribusi
Kontribusi, isu, dan permintaan fitur sangat dipersilakan! Jangan ragu untuk memeriksa [halaman issues](https://github.com/username/screen-translator-ocr/issues) jika Anda ingin berkontribusi.

1. *Fork* proyek ini.
2. Buat *branch* fitur Anda (`git checkout -b feature/FiturKeren`).
3. *Commit* perubahan Anda (`git commit -m 'Menambahkan FiturKeren'`).
4. *Push* ke *branch* (`git push origin feature/FiturKeren`).
5. Buat *Pull Request*.

## 📝 Lisensi
Proyek ini dilisensikan di bawah lisensi MIT - lihat file [LICENSE](LICENSE) untuk detailnya.
