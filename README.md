# 📂 DocPortal — Portal Konversi & Manajemen Dokumen Internal

<p align="center">
  <strong>Solusi Konversi & Manajemen Dokumen 100% Offline, Cepat, dan Aman untuk Kebutuhan Kantor / Instansi</strong><br>
  Tanpa Cloud &bull; Tanpa Langganan &bull; Zero Node.js / NPM &bull; Berjalan Lokal di Komputer Sendiri
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20--%203.13%2B-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web%20Engine-black?style=flat-square&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/AI%20OCR-RapidOCR%20PP--OCRv4-orange?style=flat-square" alt="RapidOCR">
  <img src="https://img.shields.io/badge/Privacy-100%25%20Offline-emerald?style=flat-square" alt="100% Offline">
  <img src="https://img.shields.io/badge/License-MIT-purple?style=flat-square" alt="License">
</p>

---

## 📌 Mengapa DocPortal?

Banyak portal konversi online populer (seperti iLovePDF, Smallpdf, TinyPNG, dsb.) mengharuskan pengguna mengunggah dokumen penting ke server pihak ketiga (cloud). Hal ini berisiko melanggar kerahasiaan data internal, privasi data pegawai/klien, atau regulasi instansi.

**DocPortal** dirancang khusus sebagai solusi internal:
- 🔒 **100% Offline & Aman**: Seluruh pemrosesan dilakukan di RAM komputer lokal. Tidak ada data atau berkas yang dikirim keluar jaringan.
- ⚡ **Bebas Batasan**: Tidak ada batasan jumlah file per hari, batasan ukuran berkas gratisan, maupun *watermark*.
- 🖥️ **Akses Jaringan Kantor**: Cukup dijalankan di satu laptop/server lokal, seluruh rekan satu ruangan (PC kantor lain atau HP via Wi-Fi) dapat langsung memakainya lewat browser.
- 🧩 **Zero Node.js / Zero NPM**: Menggunakan Vanilla JavaScript modular dan pustaka vendor lokal berbobot ringan, sehingga mudah dipelihara tanpa dependensi frontend yang rumit.

---

## 🛠️ Fitur Unggulan

DocPortal menyediakan 12 alat terintegrasi dalam satu antarmuka modern yang bersih:

### 1. Dokumen & Kantor
| Alat | Keterangan & Keunggulan |
| :--- | :--- |
| **HTML ke Excel** | Mengekstrak struktur tabel `<table>` dan elemen kartu dari kode HTML halaman web menjadi file spreadsheet Excel (`.xlsx`). Mendukung paste kode langsung maupun unggah berkas `.html`/`.docx`. |
| **CSV ke Excel** | Konversi data tabel CSV menjadi spreadsheet Excel (`.xlsx`) dengan deteksi otomatis pemisah (*delimiter*) koma (`,`), titik koma (`;`), maupun tab. |
| **PDF ke Word** | Konversi dokumen PDF ke Word (`.docx`) dengan 3 mode cerdas:<br>&bull; **Mode Standar**: Untuk PDF digital biasa (tata letak, font, dan tabel utuh).<br>&bull; **Mode AI OCR**: Ekstraksi teks dari PDF hasil scan/foto secara offline menggunakan model PP-OCRv4.<br>&bull; **Mode Hybrid**: Solusi khusus sertifikat/piagam berlatar gradasi tebal agar visual latar tidak berubah menjadi kotak hitam sementara teks tetap dapat diedit. |
| **Word ke PDF** | Konversi Word (`.docx`) ke PDF dengan engine LibreOffice lokal — ukuran kertas (A4, F4, Letter), margin, kop surat, font, dan bingkai halaman dijamin 100% identik asli. |
| **PDF ke PPT** | Mengubah setiap lembar PDF menjadi slide presentasi Microsoft PowerPoint (`.pptx`) proporsional yang siap ditayangkan. |

### 2. Gambar & Media
| Alat | Keterangan & Keunggulan |
| :--- | :--- |
| **PDF ke Gambar** | Ekspor lembar dokumen PDF menjadi berkas citra gambar PNG (tajam) atau JPG (ringkas) dengan pilihan resolusi DPI (96, 150, 300). Mendukung unduh satu lembar atau seluruh lembar dikemas dalam arsip ZIP. |
| **Gambar ke PDF** | Satukan banyak foto atau berkas gambar (JPG, PNG, WEBP, BMP) menjadi satu dokumen PDF siap cetak/arsip. Pilihan format halaman: *Fit Asli* atau *Kertas Standar A4*. |
| **Kompres Gambar** | Kompresi cerdas berkas JPG, PNG, WEBP, BMP, GIF, TIFF:<br>&bull; **Teknologi Kuantisasi Warna (ala TinyPNG)**: Memangkas ukuran PNG hingga 60%–90%+ dengan visual tetap tajam.<br>&bull; **Slider Kualitas & Preset**: Pilihan Kuat (45%), Seimbang (70%), dan Ringan (85%).<br>&bull; **Auto-capping Kamera**: Foto resolusi tinggi (>2400px) otomatis disesuaikan agar ukuran berkurang nyata.<br>&bull; **Konversi Format Sekaligus**: Opsi langsung ekspor ke format WEBP atau JPG. |

### 3. Pengelola Berkas PDF
| Alat | Keterangan & Keunggulan |
| :--- | :--- |
| **Gabung PDF (Merge)** | Satukan beberapa dokumen PDF menjadi satu berkas utuh dengan kanvas visual drag-and-drop untuk mengatur urutan susunan dokumen. |
| **Pisah PDF (Split)** | Pecah dokumen PDF menjadi berkas individual per lembar (dikemas dalam ZIP) atau bagi dokumen berdasarkan rentang halaman (misal: 1-3, 4-6, 7-10). |
| **Kelola Halaman PDF** | Kelola isi PDF secara interaktif di layar: geser thumbnail untuk menukar urutan halaman, putar halaman 90°, atau buang halaman yang tidak diperlukan. |
| **Kompres PDF** | Perkecil ukuran file dokumen PDF secara signifikan (hingga 50%–90%+) dengan down-sampling cerdas, pembersihan metadata sampah, kuantisasi gambar transparan, dan *font subsetting*. Dilengkapi pratinjau penghematan MB sebelum diunduh. |

---

## 💻 Prasyarat Sistem

- **Sistem Operasi**: Windows 10/11, Linux, atau macOS
- **Python**: Versi `3.10`, `3.11`, `3.12`, atau `3.13+`
- **LibreOffice** *(Opsional tapi disarankan)*: Diperlukan jika ingin menggunakan fitur konversi **Word ke PDF**. Jika LibreOffice terpasang di sistem (di Program Files), DocPortal akan otomatis mendeteksinya.

---

## 🚀 Panduan Instalasi & Menjalankan

### 1. Clone Repositori
```bash
git clone https://github.com/SunnFlower47/DocPortal.git
cd DocPortal
```

### 2. Pasang Dependensi Python
Disarankan menggunakan virtual environment (opsional):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

Pasang pustaka yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
Di Windows, Anda cukup klik dua kali file **`start_app.bat`**, atau jalankan lewat terminal:
```bash
python app.py
```

Setelah aplikasi berjalan, terminal akan menampilkan alamat akses:
```text
=================================================================
    PORTAL KONVERSI DOKUMEN INTERNAL (100% AMAN & OFFLINE)
=================================================================
 [Akses Komputer Ini]  : http://localhost:5050 atau http://127.0.0.1:5050
 [Akses Perangkat/HP]  : http://192.168.1.x:5050
=================================================================
```

Buka peramban (browser) dan akses **`http://localhost:5050`**.

---

## 🌐 Berbagi Akses di Jaringan Kantor / Wi-Fi

DocPortal otomatis mendengarkan di seluruh kartu jaringan (`0.0.0.0:5050`). Jika komputer Anda terhubung ke Wi-Fi atau LAN kantor yang sama:
1. Periksa IP komputer server Anda (tertera di terminal saat `python app.py` dijalankan, contoh: `http://192.168.1.5:5050`).
2. Rekan kerja atau perangkat HP Anda dapat langsung membuka alamat tersebut di browser masing-masing tanpa perlu menginstal Python apa pun.

---

## 📁 Struktur Direktori

```text
DocPortal/
│
├── app.py                      # Flask Application Server & API Routing
├── requirements.txt            # Daftar pustaka Python (PyMuPDF, Pillow, rapidocr, dll)
├── start_app.bat               # Launcher instan untuk Windows
├── README.md                   # Dokumentasi proyek
│
├── services/                   # Backend Business Logic
│   ├── doc_converter.py        # Core Engine: Kompresi, OCR, Hybrid, PDF, Image & Office
│   ├── parser.py               # Parser tabel HTML & CSV
│   └── exporter.py             # Generator Excel (.xlsx) dengan styling rapi
│
├── static/                     # Aset Frontend Statis
│   ├── css/
│   │   └── style.css           # Styling kustom (Linear/Vercel-inspired clean UI)
│   ├── js/
│   │   ├── app.js              # Bootstrap & Dropzone initialization
│   │   └── services/           # Modul logika Vanilla JavaScript per fitur
│   │       ├── common.js       # Utility bersama, Loading Modal & Toast
│   │       ├── navigation.js   # Navigasi tool, dashboard filter & drawer mobile
│   │       ├── table_service.js# Handler HTML & CSV to Excel
│   │       ├── office_service.js # Handler PDF to Word, Word to PDF, PDF to PPT
│   │       ├── image_service.js# Handler PDF to Image, Image to PDF & Kompres Gambar
│   │       ├── pdf_organizer_service.js # Handler Merge, Split & Page Manager
│   │       └── pdf_compress_service.js  # Handler Kompresi Dokumen PDF
│   └── vendor/                 # Pustaka Offline Pihak Ketiga (Local)
│       ├── pdf.min.js          # Mozilla PDF.js (viewer & thumbnail rendering)
│       ├── pdf.worker.min.js   # PDF.js Web Worker
│       └── sortable.min.js     # SortableJS untuk drag-and-drop halaman & kartu
│
└── templates/                  # Template Antarmuka HTML (Jinja2)
    ├── index.html              # Shell halaman utama
    ├── components/             # Komponen UI modular
    │   ├── header.html         # Topbar & indikator berkas
    │   ├── sidebar.html        # Navigasi menu samping & status offline
    │   ├── loading_modal.html  # Modal progres konversi 3 tahap
    │   └── toast.html          # Pop-up notifikasi melayang
    └── views/                  # Tampilan lembar kerja per fitur
        ├── view_dashboard.html      # Beranda & pencarian cepat alat
        ├── view_table_tools.html    # Panel HTML/CSV ke Excel + pratinjau tabel
        ├── view_office_tools.html   # Panel PDF ke Word, Word ke PDF, PDF ke PPT
        ├── view_image_tools.html    # Panel PDF ke Gambar & Gambar ke PDF
        ├── view_compress_image.html # Panel Kompres Gambar
        ├── view_pdf_organizer.html  # Panel Gabung, Pisah & Kelola Halaman PDF
        └── view_pdf_compress.html   # Panel Kompresi Dokumen PDF
```

---

## 📄 Lisensi

Proyek ini didistribusikan di bawah lisensi [MIT](LICENSE). Bebas digunakan, dimodifikasi, dan disebarkan untuk keperluan pribadi, kantor, instansi, maupun komersial.
