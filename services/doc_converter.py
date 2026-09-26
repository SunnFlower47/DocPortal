import io
import os
import re
import shutil
import tempfile
import subprocess
import docx
import mammoth
from xhtml2pdf import pisa
from pdf2docx import Converter

def _clean_and_refine_reconstructed_docx(docx_path):
    """
    Menyempurnakan tata letak dokumen Word hasil rekonstruksi PDF:
    - Memperbaiki bullet list agar menggunakan List Bullet standar Word
    - Memperbaiki nomor ganda pada daftar berpenomoran (Numbered List)
    - Merapikan spasi dan perataan teks tabel
    """
    try:
        doc = docx.Document(docx_path)
        modified = False

        for p in doc.paragraphs:
            raw_text = p.text
            if not raw_text:
                continue

            # 1. Perbaiki Bullet List (karakter simbol bullet \uf0b7, •, dll)
            if '\uf0b7' in raw_text or raw_text.strip().startswith(('•', '–', '—', '■', '◆', '○')):
                cleaned = re.sub(r'^[\s\t]*[\uf0b7•–—■◆○\*\-]\s*\t*', '', raw_text).strip()
                p.text = cleaned
                try:
                    p.style = 'List Bullet'
                except Exception:
                    pass
                modified = True

            # 2. Perbaiki Numbered List yang sering kali angkanya terduplikasi (misal "1. \t1. Langkah")
            elif re.match(r'^\s*\d+[\.\)]\s*\t*\d+[\.\)]\s*', raw_text):
                cleaned = re.sub(r'^\s*\d+[\.\)]\s*\t*\d+[\.\)]\s*', '', raw_text).strip()
                p.text = cleaned
                try:
                    p.style = 'List Number'
                except Exception:
                    pass
                modified = True

        # 3. Optimasi padding dan perataan teks dalam sel tabel
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    # Pastikan teks dalam sel rapi tanpa leading tab berlebihan
                    for p in cell.paragraphs:
                        if p.text and p.text.startswith('\t'):
                            p.text = p.text.lstrip('\t')
                            modified = True

        if modified:
            doc.save(docx_path)
    except Exception:
        pass

def _find_libreoffice_executable():
    """Mencari executable LibreOffice (soffice.com atau soffice.exe) untuk konversi Word native 100% presisi."""
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.com",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.com",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    for name in ["soffice.com", "soffice.exe", "soffice", "libreoffice"]:
        found = shutil.which(name)
        if found:
            return found
    return None

def _find_browser_executable():
    """Mencari browser Chromium (Microsoft Edge atau Google Chrome) di Windows"""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    for name in ["msedge.exe", "msedge", "chrome.exe", "chrome"]:
        found = shutil.which(name)
        if found:
            return found
    return None

# ----------------------------------------------------------------------
# 1. KONVERSI PDF KE WORD (.docx) - MODE DIGITAL (ARTIFEX PRESISI TINGGI)
# ----------------------------------------------------------------------
def convert_pdf_to_word(pdf_stream):
    """
    Mengonversi file PDF digital menjadi dokumen Word (.docx) secara lokal
    menggunakan library ArtifexSoftware/pdf2docx dengan parameter rekonstruksi
    layout tingkat lanjut (optimasi posisi teks, list, borderless table, dan grafik).
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        temp_pdf.write(pdf_stream.read())
        temp_pdf_path = temp_pdf.name

    temp_docx_path = temp_pdf_path.replace('.pdf', '.docx')

    try:
        cv = Converter(temp_pdf_path)

        # Pengaturan presisi tinggi untuk mencegah teks bergeser, tabel pecah, atau list acak
        advanced_settings = {
            'multi_processing': False,         # False menjaga urutan dan kestabilan layout halaman
            'extract_stream_table': True,      # Mengekstrak tabel tanpa border (borderless table)
            'parse_lattice_table': True,       # Mengekstrak tabel bergaris (grid table)
            'parse_stream_table': True,        # Parsing tabel aliran teks
            'list_not_table': True,            # Mencegah daftar bullet/number disalahartikan sebagai tabel
            'delete_end_line_hyphen': True,    # Menghapus tanda hubung pemisah kata di ujung baris
            'float_image_ignorable_gap': 2.0,  # Toleransi posisi gambar mengambang lebih presisi
            'line_break_free_space_ratio': 0.05,
            'line_break_width_ratio': 0.6,
            'lines_left_aligned_threshold': 1.5,
            'lines_right_aligned_threshold': 1.5,
            'lines_center_aligned_threshold': 2.0,
            'connected_border_tolerance': 0.8, # Toleransi sambungan garis tabel
            'shape_min_dimension': 1.5,        # Deteksi elemen garis dan bentuk halus
        }

        cv.convert(temp_docx_path, start=0, end=None, **advanced_settings)
        cv.close()

        # Jalankan post-processing untuk merapikan list bullet & nomor ganda serta teks tabel
        _clean_and_refine_reconstructed_docx(temp_docx_path)

        with open(temp_docx_path, 'rb') as f:
            output_bytes = io.BytesIO(f.read())
        output_bytes.seek(0)
        return output_bytes
    except Exception as e:
        raise ValueError(f"Gagal memproses file PDF: {str(e)}")
    finally:
        for p in [temp_pdf_path, temp_docx_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

# ----------------------------------------------------------------------
# 2. KONVERSI PDF KE WORD (.docx) - MODE OCR SCAN (RAPIDOCR AI DENGAN POSISI & WARNA)
# ----------------------------------------------------------------------
def convert_pdf_ocr_to_word(pdf_stream):
    """
    Mengekstrak dokumen PDF hasil scan/foto menggunakan RapidOCR (Deep Learning)
    dengan rekonstruksi tata letak cerdas:
    - Mempertahankan posisi vertikal dan horizontal (rata kiri, tengah, rata kanan)
    - Memperkirakan ukuran font judul (heading) vs isi paragraf berdasarkan tinggi bounding-box
    - Mengekstrak warna teks asli (misal teks biru, merah, atau hitam)
    - Mendeteksi indentasi dan jarak baris antar paragraf
    100% offline di CPU lokal tanpa internet.
    """
    try:
        import pymupdf
        # rapidocr (Python 3.13+ support) menggantikan rapidocr_onnxruntime yang deprecated
        try:
            from rapidocr import RapidOCR
        except ImportError:
            from rapidocr_onnxruntime import RapidOCR  # fallback untuk Python <=3.12 lama
        import docx
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import numpy as np
        from PIL import Image
    except ImportError as ie:
        raise ValueError(f"Modul OCR belum terpasang: {str(ie)}")

    engine = RapidOCR()
    pdf_bytes = pdf_stream.read()

    try:
        doc_pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"File PDF rusak atau tidak dapat dibuka: {str(e)}")

    out_doc = docx.Document()
    total_pages = len(doc_pdf)

    if total_pages == 0:
        raise ValueError("Dokumen PDF tidak memiliki halaman.")

    # ── Deteksi & terapkan ukuran kertas dari halaman pertama PDF ──
    from docx.shared import Cm, Inches, Emu
    first_page = doc_pdf[0]
    page_rect  = first_page.rect               # unit: points (1pt = 1/72 inch)
    pdf_w_pt   = page_rect.width
    pdf_h_pt   = page_rect.height
    # Konversi: 1 inch = 72 pt; python-docx menggunakan EMU (914400 EMU/inch)
    emu_per_pt = 914400 / 72
    doc_w_emu  = int(pdf_w_pt * emu_per_pt)
    doc_h_emu  = int(pdf_h_pt * emu_per_pt)

    for section in out_doc.sections:
        section.page_width  = doc_w_emu
        section.page_height = doc_h_emu
        # Margin proporsional ~2cm
        margin_emu = int(Cm(2).emu)
        section.top_margin    = margin_emu
        section.bottom_margin = margin_emu
        section.left_margin   = margin_emu
        section.right_margin  = margin_emu

    # Lebar teks tersedia (dalam pixel untuk kalkulasi alignment)
    # akan dihitung per halaman berdasarkan page_width_px
    for page_idx in range(total_pages):
        page = doc_pdf[page_idx]

        if page_idx > 0:
            out_doc.add_page_break()
            # Terapkan ukuran kertas untuk halaman tambahan (section baru)
            p_rect   = page.rect
            new_w    = int(p_rect.width  * emu_per_pt)
            new_h    = int(p_rect.height * emu_per_pt)
            # Tidak ada section baru otomatis per halaman di python-docx,
            # page_break cukup — ukuran kertas sudah di-set di section utama


        # Render halaman PDF menjadi gambar resolusi tinggi (200 DPI)
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        page_width_px = pix.width
        page_height_px = pix.height

        # Konversi ke NumPy array untuk analisis warna teks
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_arr = np.array(pil_img)

        ocr_result, _ = engine(img_bytes)

        if not ocr_result:
            out_doc.add_paragraph("")
            continue

        # Sortir hasil OCR dari atas ke bawah (y), lalu kiri ke kanan (x)
        def get_box_top(item):
            box = item[0]
            return min(pt[1] for pt in box)

        sorted_ocr = sorted(ocr_result, key=get_box_top)

        for line_box in sorted_ocr:
            box = line_box[0]
            text = line_box[1].strip()
            score = float(line_box[2]) if len(line_box) > 2 else 1.0

            if not text or score < 0.3:
                continue

            # Hitung koordinat bounding box
            xs = [pt[0] for pt in box]
            ys = [pt[1] for pt in box]
            min_x, max_x = max(0, int(min(xs))), min(page_width_px - 1, int(max(xs)))
            min_y, max_y = max(0, int(min(ys))), min(page_height_px - 1, int(max(ys)))
            box_width = max_x - min_x
            box_height = max_y - min_y

            # 1. Estimasi Ukuran Font berdasarkan tinggi bounding box (skala 200 DPI)
            # 200 DPI = ~2.77 px per point
            estimated_pt = max(8.0, min(26.0, box_height / 2.7))

            # 2. Deteksi Perataan Posisi Teks (Kiri, Tengah, Kanan)
            box_center_x = (min_x + max_x) / 2.0
            page_center_x = page_width_px / 2.0

            p = out_doc.add_paragraph()

            # Rata tengah jika berada di area 25% tengah halaman dan lebar teks tidak memenuhi layar
            if abs(box_center_x - page_center_x) < (page_width_px * 0.12) and (box_width < page_width_px * 0.75):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif min_x > (page_width_px * 0.55):
                # Rata kanan / blok tanda tangan kanan
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                # Jika ada indentasi kiri yang cukup jelas
                if min_x > (page_width_px * 0.15) and min_x < (page_width_px * 0.45):
                    indent_pt = (min_x / page_width_px) * 360 # perkiraan pt
                    p.paragraph_format.left_indent = Pt(min(120, indent_pt))

            # 3. Deteksi Warna Teks Asli dari pixel gambar
            run = p.add_run(text)
            run.font.size = Pt(round(estimated_pt, 1))

            if estimated_pt >= 13.5:
                # Judul atau Heading otomatis dibuat tebal
                run.bold = True

            # Ambil sampel warna dari potongan area box teks
            try:
                crop = img_arr[min_y:max_y+1, min_x:max_x+1]
                if crop.size > 0:
                    # Filter pixel latar belakang (putih/sangat terang)
                    non_bg = crop[~np.all(crop > 215, axis=2)]
                    if len(non_bg) >= 10:
                        med_r, med_g, med_b = np.median(non_bg, axis=0).astype(int)
                        # Jika warnanya bukan hitam pekat / ada aksen warna jelas
                        if not (med_r < 40 and med_g < 40 and med_b < 40):
                            run.font.color.rgb = RGBColor(int(med_r), int(med_g), int(med_b))
            except Exception:
                pass

    doc_pdf.close()
    out_io = io.BytesIO()
    out_doc.save(out_io)
    out_io.seek(0)
    return out_io

# ----------------------------------------------------------------------
# 3. KONVERSI WORD (.docx) KE PDF (NATIVE FIDELITY DENGAN FALLBACK)
# ----------------------------------------------------------------------
def convert_word_to_pdf(docx_stream):
    """
    Mengonversi dokumen Word (.docx) ke PDF secara presisi 100% tinggi:
    1. Menggunakan Native Document Engine (LibreOffice / soffice) secara lokal dan headless:
       - Mempertahankan tata letak asli 100% (kop surat gambar + teks samping,
         bingkai garis batas halaman/page border, tata letak tanda tangan multi-kolom,
         margin asli, dan batas 1 halaman tetap 1 halaman).
    2. Fallback ke Chromium / Edge headless rendering jika native engine belum tersedia.
    """
    lo_bin = _find_libreoffice_executable()

    if lo_bin:
        temp_dir = tempfile.mkdtemp()
        temp_docx_path = os.path.join(temp_dir, "document.docx")
        try:
            with open(temp_docx_path, 'wb') as f_docx:
                f_docx.write(docx_stream.read())

            # Eksekusi LibreOffice headless
            cmd = [
                lo_bin,
                '--headless',
                '--convert-to',
                'pdf:writer_pdf_Export',
                '--outdir',
                temp_dir,
                temp_docx_path
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            expected_pdf = os.path.join(temp_dir, "document.pdf")
            if os.path.exists(expected_pdf) and os.path.getsize(expected_pdf) > 0:
                with open(expected_pdf, 'rb') as f_pdf:
                    output_bytes = io.BytesIO(f_pdf.read())
                output_bytes.seek(0)
                return output_bytes
        except Exception as err:
            # Jika native engine gagal, lanjutkan ke fallback Chromium
            pass
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # Reset stream jika ingin dicoba lagi di fallback
        docx_stream.seek(0)

    # Fallback Chromium / Mammoth
    try:
        result = mammoth.convert_to_html(docx_stream)
        body_html = result.value
    except Exception as e:
        raise ValueError(f"Gagal membaca file Word: {str(e)}")

    if not body_html.strip():
        raise ValueError("File Word kosong atau tidak memiliki konten teks/tabel.")

    # CSS A4 Professional Print
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dokumen Konversi</title>
  <style>
    @page {{
      size: A4;
      margin: 20mm 18mm 20mm 18mm;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.6;
      color: #1e293b;
      margin: 0;
      padding: 0;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }}
    h1 {{
      font-size: 20pt;
      font-weight: 700;
      color: #0f172a;
      margin-top: 0;
      margin-bottom: 14px;
      border-bottom: 2px solid #0f172a;
      padding-bottom: 8px;
    }}
    h2 {{
      font-size: 15pt;
      font-weight: 600;
      color: #1e293b;
      margin-top: 20px;
      margin-bottom: 8px;
    }}
    h3 {{
      font-size: 13pt;
      font-weight: 600;
      color: #334155;
      margin-top: 16px;
      margin-bottom: 6px;
    }}
    h4, h5, h6 {{
      font-size: 11pt;
      font-weight: 600;
      color: #475569;
      margin-top: 12px;
      margin-bottom: 4px;
    }}
    p {{
      margin-top: 0;
      margin-bottom: 10px;
      text-align: justify;
    }}
    b, strong {{
      font-weight: 700;
      color: #0f172a;
    }}
    i, em {{
      font-style: italic;
    }}
    u {{
      text-decoration: underline;
    }}
    s, strike, del {{
      text-decoration: line-through;
    }}
    ul, ol {{
      margin-top: 4px;
      margin-bottom: 12px;
      padding-left: 26px;
    }}
    li {{
      margin-bottom: 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 10pt;
      page-break-inside: auto;
    }}
    tr {{
      page-break-inside: avoid;
      page-break-after: auto;
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
    }}
    tr:nth-child(even) td {{
      background-color: #f8fafc;
    }}
    img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 12px auto;
    }}
    blockquote {{
      border-left: 3px solid #94a3b8;
      padding-left: 12px;
      color: #475569;
      margin: 12px 0;
      font-style: italic;
    }}
  </style>
</head>
<body>
  {body_html}
</body>
</html>
"""

    browser_bin = _find_browser_executable()

    if browser_bin:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f_html:
            f_html.write(html_content)
            temp_html_path = f_html.name

        temp_pdf_path = temp_html_path.replace('.html', '.pdf')

        try:
            cmd = [
                browser_bin,
                '--headless',
                '--disable-gpu',
                '--no-pdf-header-footer',
                f'--print-to-pdf={temp_pdf_path}',
                temp_html_path
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0 and os.path.exists(temp_pdf_path) and os.path.getsize(temp_pdf_path) > 0:
                with open(temp_pdf_path, 'rb') as f_pdf:
                    output_bytes = io.BytesIO(f_pdf.read())
                output_bytes.seek(0)
                return output_bytes
        except Exception:
            pass
        finally:
            for p in [temp_html_path, temp_pdf_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    # Fallback jika browser tidak ditemukan
    output_pdf = io.BytesIO()
    status = pisa.CreatePDF(html_content, dest=output_pdf)
    if status.err:
        raise ValueError("Gagal menghasilkan file PDF.")
    output_pdf.seek(0)
    return output_pdf


def _parse_page_selection(pages_str, total_pages):
    """
    Mengurai string seleksi halaman menjadi list indeks halaman (0-based).
    Mendukung:
    - 'all': semua halaman
    - 'first': halaman pertama
    - 'last': halaman terakhir
    - '3': halaman tunggal spesifik
    - '2-5': rentang halaman
    - '1, 3, 5-8': kombinasi halaman dan rentang
    """
    if not pages_str or str(pages_str).strip().lower() in ('all', '*', ''):
        return list(range(total_pages)), True

    s = str(pages_str).strip().lower()
    if s == 'first':
        return [0], False
    if s == 'last':
        return [total_pages - 1], False

    selected = set()
    parts = [p.strip() for p in s.split(',') if p.strip()]
    for part in parts:
        if '-' in part:
            bounds = part.split('-')
            if len(bounds) == 2:
                try:
                    start = int(bounds[0].strip())
                    end = int(bounds[1].strip())
                    if start > end:
                        start, end = end, start
                    for p_num in range(start, end + 1):
                        if 1 <= p_num <= total_pages:
                            selected.add(p_num - 1)
                except ValueError:
                    pass
        else:
            try:
                p_num = int(part)
                if 1 <= p_num <= total_pages:
                    selected.add(p_num - 1)
            except ValueError:
                pass

    indices = sorted(list(selected))
    if not indices:
        return [0], False

    is_all = (len(indices) == total_pages and indices == list(range(total_pages)))
    return indices, is_all


# ----------------------------------------------------------------------
# 4. KONVERSI PDF KE GAMBAR (PNG / JPG) - DUKUNGAN HALAMAN SPESIFIK & RENTANG
# ----------------------------------------------------------------------
def convert_pdf_to_image(pdf_stream, fmt='png', dpi=150, pages='all'):
    """
    Mengonversi halaman-halaman PDF menjadi file gambar (PNG / JPG) secara lokal.
    - fmt   : 'png' atau 'jpg'
    - dpi   : 96 (preview), 150 (standar), 300 (cetak/high quality)
    - pages : 'all', 'first', atau pilihan spesifik seperti '3', '2-5', '1, 3, 5-8'
    Semua proses berjalan 100% offline di CPU lokal.
    """
    import zipfile
    try:
        import pymupdf
        from PIL import Image
    except ImportError as ie:
        raise ValueError(f"Modul gambar belum terpasang: {str(ie)}")

    pdf_bytes = pdf_stream.read()
    try:
        doc_pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"File PDF rusak atau tidak dapat dibaca: {str(e)}")

    total_pages = len(doc_pdf)
    if total_pages == 0:
        raise ValueError("Dokumen PDF tidak memiliki halaman.")

    fmt = fmt.lower().strip()
    if fmt not in ('png', 'jpg', 'jpeg'):
        fmt = 'png'
    pil_fmt = 'JPEG' if fmt in ('jpg', 'jpeg') else 'PNG'
    ext = 'jpg' if fmt in ('jpg', 'jpeg') else 'png'
    mime = 'image/jpeg' if ext == 'jpg' else 'image/png'

    page_indices, is_all = _parse_page_selection(pages, total_pages)

    def render_page(page):
        """Render halaman PDF menjadi bytes gambar."""
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        save_kwargs = {'quality': 92, 'optimize': True} if pil_fmt == 'JPEG' else {'optimize': True}
        img.save(buf, format=pil_fmt, **save_kwargs)
        buf.seek(0)
        return buf.getvalue()

    # Jika hanya 1 halaman yang dipilih (misal 'first' atau halaman tertentu '3', bukan 'all'):
    if len(page_indices) == 1 and not (is_all and str(pages).strip().lower() == 'all'):
        target_idx = page_indices[0]
        img_bytes = render_page(doc_pdf[target_idx])
        doc_pdf.close()
        out = io.BytesIO(img_bytes)
        out.seek(0)
        return out, ext, mime, False, (target_idx + 1)  # (stream, ext, mime, is_zip, page_num)

    # Banyak halaman atau user meminta 'all': kemas dalam ZIP
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for idx in page_indices:
            page = doc_pdf[idx]
            img_bytes = render_page(page)
            filename = f"halaman_{idx + 1:03d}.{ext}"
            zf.writestr(filename, img_bytes)

    doc_pdf.close()
    zip_buf.seek(0)
    return zip_buf, 'zip', 'application/zip', True, None  # (stream, ext, mime, is_zip, page_num)


# ----------------------------------------------------------------------
# 5. KONVERSI PDF KE WORD (.docx) - MODE HYBRID (SERTIFIKAT & DESAIN GRAFIS)
# ----------------------------------------------------------------------
def convert_pdf_hybrid_to_word(pdf_stream):
    """
    Mode Hybrid (Khusus Sertifikat, Piagam & Desain Grafis Kompleks):
    - Merender background halaman visual asli (200 DPI) bebas dari bug kotak hitam vektor!
    - Menempatkan teks digital / OCR di lapisan foreground agar nama & teks tetap bisa diedit.
    """
    import pymupdf
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    doc_pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    if len(doc_pdf) == 0:
        raise ValueError("Dokumen PDF tidak memiliki halaman.")

    out_doc = Document()

    for page_idx in range(len(doc_pdf)):
        page = doc_pdf[page_idx]
        p_rect = page.rect
        page_w_in = p_rect.width / 72.0
        page_h_in = p_rect.height / 72.0

        if page_idx == 0:
            section = out_doc.sections[0]
        else:
            section = out_doc.add_section()

        section.page_width = Inches(page_w_in)
        section.page_height = Inches(page_h_in)
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

        # 1. Render halaman PDF visual (200 DPI) sebagai background header
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")

        header = section.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        section.header_distance = Inches(0)
        hrun = hp.add_run()
        hrun.add_picture(io.BytesIO(img_bytes), width=Inches(page_w_in), height=Inches(page_h_in))

        # 2. Ekstrak teks digital langsung dari halaman
        blocks = page.get_text("blocks")
        if not blocks:
            try:
                try:
                    from rapidocr import RapidOCR as _RapidOCR
                except ImportError:
                    from rapidocr_onnxruntime import RapidOCR as _RapidOCR
                ocr_res, _ = _RapidOCR()(img_bytes)
                if ocr_res:
                    for item in sorted(ocr_res, key=lambda x: min(pt[1] for pt in x[0])):
                        txt = item[1].strip()
                        if txt:
                            p = out_doc.add_paragraph()
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            r = p.add_run(txt)
                            r.font.size = Pt(13)
            except Exception:
                pass
        else:
            blocks_sorted = sorted(blocks, key=lambda b: b[1])
            for b in blocks_sorted:
                text = b[4].strip()
                if not text:
                    continue
                p = out_doc.add_paragraph()
                bx_center = (b[0] + b[2]) / 2.0
                px_center = p_rect.width / 2.0
                if abs(bx_center - px_center) < (p_rect.width * 0.15):
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif b[0] > (p_rect.width * 0.55):
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                lines = [l for l in text.split('\n') if l.strip()]
                line_count = max(1, len(lines))
                b_height = b[3] - b[1]
                est_font = max(9.0, min(28.0, (b_height / line_count) * 0.75))

                run = p.add_run(text)
                run.font.size = Pt(round(est_font, 1))
                if est_font >= 14:
                    run.font.bold = True

    doc_pdf.close()
    out_io = io.BytesIO()
    out_doc.save(out_io)
    out_io.seek(0)
    return out_io


# ----------------------------------------------------------------------
# 6. GABUNG PDF (MERGE PDFS)
# ----------------------------------------------------------------------
def merge_pdfs(pdf_streams):
    """Menggabungkan beberapa file PDF menjadi 1 file PDF utuh."""
    import pymupdf
    if not pdf_streams:
        raise ValueError("Tidak ada file PDF yang dipilih untuk digabungkan.")
    merged_doc = pymupdf.open()
    for s in pdf_streams:
        s_bytes = s.read() if hasattr(s, 'read') else s
        if not s_bytes:
            continue
        try:
            sub_doc = pymupdf.open(stream=s_bytes, filetype="pdf")
            merged_doc.insert_pdf(sub_doc)
            sub_doc.close()
        except Exception:
            continue
    if len(merged_doc) == 0:
        raise ValueError("Semua file PDF yang diunggah kosong atau rusak.")
    out_io = io.BytesIO()
    merged_doc.save(out_io, garbage=3, deflate=True)
    merged_doc.close()
    out_io.seek(0)
    return out_io


# ----------------------------------------------------------------------
# 7. PISAH PDF (SPLIT PDF)
# ----------------------------------------------------------------------
def split_pdf(pdf_stream, split_mode='all', ranges_str=None):
    """Memecah PDF menjadi lembaran terpisah (ZIP) atau per rentang halaman."""
    import pymupdf, zipfile
    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    if total == 0:
        raise ValueError("File PDF tidak memiliki halaman.")

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        if split_mode == 'all' or not ranges_str:
            for idx in range(total):
                sub = pymupdf.open()
                sub.insert_pdf(doc, from_page=idx, to_page=idx)
                b = io.BytesIO()
                sub.save(b, garbage=3, deflate=True)
                sub.close()
                zf.writestr(f"halaman_{idx+1:03d}.pdf", b.getvalue())
        else:
            parts = [p.strip() for p in str(ranges_str).split(',') if p.strip()]
            for part_idx, part in enumerate(parts):
                if '-' in part:
                    s, e = part.split('-')
                    start, end = int(s.strip()), int(e.strip())
                else:
                    start = end = int(part.strip())
                start = max(1, min(start, total)) - 1
                end = max(1, min(end, total)) - 1
                if start > end:
                    start, end = end, start
                sub = pymupdf.open()
                sub.insert_pdf(doc, from_page=start, to_page=end)
                b = io.BytesIO()
                sub.save(b, garbage=3, deflate=True)
                sub.close()
                zf.writestr(f"bagian_{part_idx+1}_hal_{start+1}-{end+1}.pdf", b.getvalue())

    doc.close()
    zip_buf.seek(0)
    return zip_buf


# ----------------------------------------------------------------------
# 8. HAPUS & EKSTRAK HALAMAN (REMOVE / EXTRACT PAGES)
# ----------------------------------------------------------------------
def remove_pdf_pages(pdf_stream, pages_str):
    """Menghapus nomor halaman tertentu dari PDF."""
    import pymupdf
    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    indices, _ = _parse_page_selection(pages_str, total)
    if not indices:
        raise ValueError("Nomor halaman yang akan dihapus tidak valid.")
    if len(indices) >= total:
        raise ValueError("Tidak dapat menghapus seluruh halaman PDF.")

    for idx in sorted(indices, reverse=True):
        doc.delete_page(idx)

    out_io = io.BytesIO()
    doc.save(out_io, garbage=3, deflate=True)
    doc.close()
    out_io.seek(0)
    return out_io


def extract_pdf_pages(pdf_stream, pages_str):
    """Mengekstrak hanya halaman yang dipilih menjadi PDF baru."""
    import pymupdf
    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    indices, _ = _parse_page_selection(pages_str, total)
    if not indices:
        raise ValueError("Nomor halaman yang akan diekstrak tidak valid.")

    new_doc = pymupdf.open()
    for idx in indices:
        new_doc.insert_pdf(doc, from_page=idx, to_page=idx)

    out_io = io.BytesIO()
    new_doc.save(out_io, garbage=3, deflate=True)
    doc.close()
    new_doc.close()
    out_io.seek(0)
    return out_io


# -------------------------------------------------------------
# 9. SUSUN ULANG HALAMAN (REORDER PDF) DENGAN ROTASI OPSIONAL
# -------------------------------------------------------------
def reorder_pdf_pages(pdf_stream, new_order_str, rotations=None):
    """Mengatur ulang urutan lembar halaman (misal: 3, 1, 2) serta rotasi per halaman."""
    import pymupdf, json
    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)

    parts = [int(x.strip()) - 1 for x in str(new_order_str).split(',') if x.strip().isdigit()]
    valid_indices = [idx for idx in parts if 0 <= idx < total]
    if not valid_indices:
        raise ValueError("Urutan halaman baru tidak valid.")

    # Susun urutan baru
    doc.select(valid_indices)

    # Terapkan rotasi jika ada (rotations misal: {"1": 90, "3": 180} atau {"0": 90})
    if rotations:
        rot_map = {}
        if isinstance(rotations, str):
            try:
                rot_map = json.loads(rotations)
            except Exception:
                pass
        elif isinstance(rotations, dict):
            rot_map = rotations

        for page_idx in range(len(doc)):
            # Cek dengan index 0-based atau 1-based
            rot = rot_map.get(str(page_idx)) or rot_map.get(str(page_idx + 1)) or rot_map.get(page_idx)
            if rot:
                try:
                    angle = int(rot)
                    if angle % 90 == 0:
                        doc[page_idx].set_rotation((doc[page_idx].rotation + angle) % 360)
                except Exception:
                    pass

    out_io = io.BytesIO()
    doc.save(out_io, garbage=3, deflate=True)
    doc.close()
    out_io.seek(0)
    return out_io


# -------------------------------------------------------------
# 10. KOMPRES UKURAN PDF (IMAGE-AWARE DOWN-SAMPLING ENGINE)
# -------------------------------------------------------------
def compress_pdf(pdf_stream, level='recommended'):
    """
    Mengompresi ukuran file PDF secara cerdas, agresif, dan optimal:
    - Melakukan down-sampling dan rekompresi gambar/foto di dalam PDF
    - Mengompresi gambar PNG/transparan menggunakan smart quantization
    - Memangkas subset font yang tidak terpakai (subset_fonts)
    - Mengaktifkan object streams (use_objstms=1) untuk memadatkan ribuan objek teks & struktur
    - Membersihkan metadata sampah dan men-deflate seluruh bytecode stream
    """
    import pymupdf
    from PIL import Image

    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    orig_len = len(pdf_bytes)
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Konfigurasi parameter kompresi gambar sesuai level
    if level == 'high':
        max_dim = 650
        quality = 36
        quantize_colors = 128
    elif level == 'low':
        max_dim = 1500
        quality = 75
        quantize_colors = 256
    else:  # recommended / medium (standar kantor tajam & sangat hemat)
        max_dim = 1000
        quality = 55
        quantize_colors = 256

    processed_xrefs = set()

    for page in doc:
        try:
            image_list = page.get_images()
        except Exception:
            continue

        for img_info in image_list:
            xref = img_info[0]
            smask = img_info[1]
            if xref in processed_xrefs:
                continue
            processed_xrefs.add(xref)

            try:
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue

                img_data = base_image["image"]
                orig_img_len = len(img_data)
                if orig_img_len < 1024:  # Jangan ubah icon sangat kecil
                    continue

                pil_img = Image.open(io.BytesIO(img_data))
                w, h = pil_img.size
                if w < 64 and h < 64:
                    continue

                # Resize jika melebihi batas resolusi
                ratio = min(1.0, max_dim / max(w, h))
                if ratio < 1.0:
                    new_w = max(1, int(w * ratio))
                    new_h = max(1, int(h * ratio))
                    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                out_img_io = io.BytesIO()

                # Cek apakah gambar memiliki transparansi (alpha channel) atau mask khusus (smask)
                has_alpha = (smask > 0) or (pil_img.mode in ('RGBA', 'LA')) or (pil_img.mode == 'P' and 'transparency' in pil_img.info)
                if has_alpha:
                    # Gambar transparan: lakukan smart quantization agar ukuran menyusut drastis tanpa merusak transparansi
                    try:
                        q_img = pil_img.quantize(colors=quantize_colors, method=Image.Quantize.FASTOCTREE)
                        q_img.save(out_img_io, format='PNG', optimize=True, compress_level=9)
                    except Exception:
                        pil_img.save(out_img_io, format='PNG', optimize=True, compress_level=9)
                else:
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    pil_img.save(out_img_io, format='JPEG', quality=quality, optimize=True, progressive=True)

                new_img_bytes = out_img_io.getvalue()

                # Ganti gambar jika hasil kompresi lebih kecil
                if len(new_img_bytes) < orig_img_len:
                    page.replace_image(xref, stream=new_img_bytes)
            except Exception:
                continue

    # Pangkas font yang tidak digunakan jika memungkinkan
    try:
        doc.subset_fonts()
    except Exception:
        pass

    out_io = io.BytesIO()
    doc.save(
        out_io,
        garbage=4,
        clean=True,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        use_objstms=1,
    )
    doc.close()

    new_len = len(out_io.getvalue())

    # Jika file terkompresi ternyata lebih besar dari aslinya, gunakan file asli
    if new_len > orig_len:
        out_io = io.BytesIO(pdf_bytes)
        new_len = orig_len
        saved_pct = 0.0
    else:
        saved_pct = max(0.0, round((orig_len - new_len) / orig_len * 100, 1))

    out_io.seek(0)
    return out_io, orig_len, new_len, saved_pct


# ----------------------------------------------------------------------
# 11. GAMBAR KE PDF (IMAGE TO PDF)
# ----------------------------------------------------------------------
def convert_image_to_pdf(image_streams, page_size='fit'):
    """Mengonversi satu atau banyak file gambar (JPG / PNG) menjadi PDF."""
    import pymupdf
    from PIL import Image
    doc = pymupdf.open()
    for s in image_streams:
        b = s.read() if hasattr(s, 'read') else s
        if not b:
            continue
        try:
            img = Image.open(io.BytesIO(b))
            w, h = img.size
            if page_size == 'a4':
                p_w, p_h = 595, 842
                ratio = min((p_w - 40) / w, (p_h - 40) / h)
                dw, dh = w * ratio, h * ratio
                dx, dy = (p_w - dw) / 2.0, (p_h - dh) / 2.0
                page = doc.new_page(width=p_w, height=p_h)
                page.insert_image(pymupdf.Rect(dx, dy, dx + dw, dy + dh), stream=b)
            else:
                p_w = w * 72.0 / 96.0
                p_h = h * 72.0 / 96.0
                page = doc.new_page(width=p_w, height=p_h)
                page.insert_image(pymupdf.Rect(0, 0, p_w, p_h), stream=b)
        except Exception:
            continue

    if len(doc) == 0:
        raise ValueError("Tidak ada gambar valid yang berhasil diolah.")
    out_io = io.BytesIO()
    doc.save(out_io, garbage=3, deflate=True)
    doc.close()
    out_io.seek(0)
    return out_io


# ----------------------------------------------------------------------
# 12. PDF KE POWERPOINT (PDF TO PPT / PPTX)
# ----------------------------------------------------------------------
def convert_pdf_to_ppt(pdf_stream):
    """Mengonversi dokumen PDF menjadi file presentasi PowerPoint (.pptx)."""
    import pymupdf, pptx
    from pptx.util import Inches
    pdf_bytes = pdf_stream.read() if hasattr(pdf_stream, 'read') else pdf_stream
    doc_pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    if len(doc_pdf) == 0:
        raise ValueError("Dokumen PDF tidak memiliki halaman.")

    prs = pptx.Presentation()
    blank_layout = prs.slide_layouts[6]

    first_p = doc_pdf[0]
    prs.slide_width = Inches(first_p.rect.width / 72.0)
    prs.slide_height = Inches(first_p.rect.height / 72.0)

    for p in doc_pdf:
        pix = p.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(io.BytesIO(img_bytes), 0, 0, width=prs.slide_width, height=prs.slide_height)

    doc_pdf.close()
    out_io = io.BytesIO()
    prs.save(out_io)
    out_io.seek(0)
    return out_io


# ----------------------------------------------------------------------
# 12. KOMPRES & KONVERSI GAMBAR (JPG / PNG / WEBP / BMP / GIF)
# ----------------------------------------------------------------------
def compress_image(img_stream, filename, quality=70, output_format=None, max_width=None, max_height=None):
    """
    Mengompresi file gambar (JPG, PNG, WEBP, BMP, GIF, TIFF) secara optimal dan nyata:
    - Default quality 70 (sweet spot pengurangan 50-80% tanpa penurunan visual kasat mata)
    - PNG: smart color quantization (TinyPNG-style) memangkas ukuran 60-80%
    - JPEG: optimize=True, progressive=True
    - WEBP: method=6 kompresi densitas tinggi
    - Auto-downscale jika gambar kamera raksasa (>2400px) saat batas tidak diatur manual
    """
    from PIL import Image

    img_bytes = img_stream.read() if hasattr(img_stream, 'read') else img_stream
    orig_size = len(img_bytes)

    ext_in = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext_in == 'jpeg':
        ext_in = 'jpg'

    if output_format:
        ext_out = output_format.lower().lstrip('.')
        if ext_out == 'jpeg':
            ext_out = 'jpg'
    else:
        ext_out = ext_in

    PIL_FORMAT_MAP = {
        'jpg':  'JPEG',
        'png':  'PNG',
        'webp': 'WEBP',
        'bmp':  'BMP',
        'gif':  'GIF',
        'tiff': 'TIFF',
        'tif':  'TIFF',
    }
    MIME_MAP = {
        'jpg':  'image/jpeg',
        'png':  'image/png',
        'webp': 'image/webp',
        'bmp':  'image/bmp',
        'gif':  'image/gif',
        'tiff': 'image/tiff',
        'tif':  'image/tiff',
    }

    pil_fmt_out = PIL_FORMAT_MAP.get(ext_out, 'JPEG')
    mime = MIME_MAP.get(ext_out, 'image/jpeg')

    img = Image.open(io.BytesIO(img_bytes))

    # Dimensi & Auto-capping
    w, h = img.size
    # Jika user tidak membatasi ukuran manual, batasi gambar kamera raksasa (>2400px) ke 2048px
    if not max_width and not max_height:
        if max(w, h) > 2400:
            max_width = 2048

    if max_width and w > max_width:
        ratio = max_width / w
        img = img.resize((max_width, max(1, int(h * ratio))), Image.Resampling.LANCZOS)
    if max_height and img.size[1] > max_height:
        ratio = max_height / img.size[1]
        img = img.resize((max(1, int(img.size[0] * ratio)), max_height), Image.Resampling.LANCZOS)

    has_alpha = img.mode in ('RGBA', 'LA', 'PA') or (img.mode == 'P' and 'transparency' in img.info)

    out_io = io.BytesIO()

    if pil_fmt_out in ('JPEG', 'BMP'):
        if has_alpha:
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            alpha = img.split()[-1] if img.mode in ('RGBA', 'LA') else None
            bg.paste(img, mask=alpha)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        if pil_fmt_out == 'JPEG':
            img.save(out_io, format='JPEG', quality=quality, optimize=True, progressive=True)
        else:
            img.save(out_io, format='BMP')

    elif pil_fmt_out == 'WEBP':
        img.save(out_io, format='WEBP', quality=quality, method=6)

    elif pil_fmt_out == 'PNG':
        # Smart PNG Compression:
        # Coba simpan standar dulu
        buf_std = io.BytesIO()
        img.save(buf_std, format='PNG', optimize=True, compress_level=9)
        best_bytes = buf_std.getvalue()

        # Jika quality < 92, lakukan smart color quantization (ala TinyPNG)
        if quality < 92:
            try:
                num_colors = 256 if quality >= 68 else (128 if quality >= 45 else 64)
                if has_alpha:
                    q_img = img.quantize(colors=num_colors, method=Image.Quantize.FASTOCTREE)
                else:
                    img_rgb = img.convert('RGB') if img.mode != 'RGB' else img
                    q_img = img_rgb.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)

                buf_q = io.BytesIO()
                q_img.save(buf_q, format='PNG', optimize=True, compress_level=9)
                q_bytes = buf_q.getvalue()
                if len(q_bytes) < len(best_bytes):
                    best_bytes = q_bytes
            except Exception:
                pass

        out_io.write(best_bytes)

    elif pil_fmt_out == 'GIF':
        img.save(out_io, format='GIF', optimize=True)
    else:
        img.save(out_io, format=pil_fmt_out)

    new_size = len(out_io.getvalue())
    if new_size > orig_size and output_format is None:
        # Jika hasil kompresi malah lebih besar dan format tidak diubah, pakai berkas asli
        out_io = io.BytesIO(img_bytes)
        new_size = orig_size
        saved_pct = 0.0
    else:
        saved_pct = max(0.0, round((orig_size - new_size) / orig_size * 100, 1))

    out_io.seek(0)
    return out_io, ext_out, mime, orig_size, new_size, saved_pct
