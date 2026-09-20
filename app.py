import socket
import os
from flask import Flask, request, jsonify, send_file, render_template
from services.parser import (
    extract_text_from_docx,
    validate_input_content,
    parse_html_data,
    parse_csv_data
)
from services.exporter import generate_excel_bytes
from services.doc_converter import (
    convert_pdf_to_word,
    convert_word_to_pdf,
    convert_pdf_ocr_to_word,
    convert_pdf_hybrid_to_word,
    convert_pdf_to_image,
    merge_pdfs,
    split_pdf,
    remove_pdf_pages,
    extract_pdf_pages,
    reorder_pdf_pages,
    compress_pdf,
    convert_image_to_pdf,
    convert_pdf_to_ppt,
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Maksimal 100MB
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    return render_template('index.html')

# -------------------------------------------------------------
# 1. API: PARSE HTML (PASTE / FILE DOCX/HTML)
# -------------------------------------------------------------
@app.route('/api/parse', methods=['POST'])
def api_parse_html():
    try:
        html_content = ""
        if 'file' in request.files:
            f = request.files['file']
            filename = f.filename.lower()
            if not filename:
                return jsonify({'error_title': 'File Kosong', 'error': 'Tidak ada file yang dipilih.'}), 400

            if filename.endswith('.docx'):
                html_content = extract_text_from_docx(f)
            else:
                html_content = f.read().decode('utf-8', errors='ignore')
        elif 'html_text' in request.form:
            html_content = request.form['html_text']
        else:
            return jsonify({'error_title': 'Input Kosong', 'error': 'Tidak ada data yang dikirim.'}), 400

        is_valid, err_msg = validate_input_content(html_content)
        if not is_valid:
            return jsonify({'error_title': 'Input Tidak Valid', 'error': err_msg}), 400

        data = parse_html_data(html_content)
        if not data:
            return jsonify({
                'error_title': 'Format Data Tidak Cocok',
                'error': 'Kode HTML tidak memuat struktur tabel atau data kartu yang dikenali. Pastikan Anda menyalin tag elemen yang berisi baris data.'
            }), 400

        return jsonify({'total': len(data), 'data': data})

    except ValueError as ve:
        return jsonify({'error_title': 'Format File Salah', 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error_title': 'Terjadi Kesalahan Server', 'error': f"Gagal mengekstrak: {str(e)}"}), 500

# -------------------------------------------------------------
# 2. API: PARSE CSV
# -------------------------------------------------------------
@app.route('/api/parse-csv', methods=['POST'])
def api_parse_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file CSV.'}), 400
        f = request.files['file']
        filename = f.filename.lower()
        if not filename.endswith('.csv'):
            return jsonify({'error_title': 'Bukan File CSV', 'error': 'File yang dipilih harus berformat .csv'}), 400

        data = parse_csv_data(f)
        return jsonify({'total': len(data), 'data': data})
    except ValueError as ve:
        return jsonify({'error_title': 'File CSV Tidak Valid', 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error_title': 'Gagal Membaca CSV', 'error': str(e)}), 500

# -------------------------------------------------------------
# 3. API: EXPORT EXCEL (.xlsx)
# -------------------------------------------------------------
@app.route('/api/export-excel', methods=['POST'])
def api_export_excel():
    try:
        req_json = request.get_json()
        if not req_json or 'data' not in req_json:
            return jsonify({'error': 'Tidak ada data untuk diekspor'}), 400

        data = req_json['data']
        excel_stream = generate_excel_bytes(data)
        return send_file(
            excel_stream,
            as_attachment=True,
            download_name='Data_Hasil_Konversi.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f"Gagal menghasilkan file Excel: {str(e)}"}), 500

# -------------------------------------------------------------
# 4. API: KONVERSI PDF KE WORD (.docx)
# -------------------------------------------------------------
@app.route('/api/convert/pdf-to-word', methods=['POST'])
def api_pdf_to_word():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        filename = f.filename
        if not filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File yang diunggah harus berekstensi .pdf'}), 400

        base_name = os.path.splitext(filename)[0]
        mode = request.form.get('mode', 'standard')

        if mode == 'ocr':
            output_stream = convert_pdf_ocr_to_word(f)
            download_suffix = "_ocr.docx"
        elif mode == 'hybrid':
            output_stream = convert_pdf_hybrid_to_word(f)
            download_suffix = "_hybrid.docx"
        else:
            output_stream = convert_pdf_to_word(f)
            download_suffix = "_converted.docx"

        return send_file(
            output_stream,
            as_attachment=True,
            download_name=f"{base_name}{download_suffix}",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        return jsonify({'error_title': 'Gagal Konversi PDF', 'error': f"Terjadi kesalahan: {str(e)}"}), 500

# -------------------------------------------------------------
# 5. API: KONVERSI WORD (.docx) KE PDF
# -------------------------------------------------------------
@app.route('/api/convert/word-to-pdf', methods=['POST'])
def api_word_to_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file Word (.docx).'}), 400
        f = request.files['file']
        filename = f.filename
        if not filename.lower().endswith('.docx'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File yang diunggah harus berekstensi .docx'}), 400

        base_name = os.path.splitext(filename)[0]
        output_stream = convert_word_to_pdf(f)

        return send_file(
            output_stream,
            as_attachment=True,
            download_name=f"{base_name}_converted.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error_title': 'Gagal Konversi Word', 'error': f"Terjadi kesalahan: {str(e)}"}), 500

# -------------------------------------------------------------
# 6. API: KONVERSI PDF KE GAMBAR (PNG / JPG / ZIP)
# -------------------------------------------------------------
@app.route('/api/convert/pdf-to-image', methods=['POST'])
def api_pdf_to_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        filename = f.filename
        if not filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File yang diunggah harus berekstensi .pdf'}), 400

        base_name = os.path.splitext(filename)[0]
        fmt   = request.form.get('format', 'png').lower()
        dpi   = int(request.form.get('dpi', 150))
        pages = request.form.get('pages', 'all')

        # Batasi DPI agar tidak terlalu berat
        dpi = max(72, min(dpi, 300))

        out_stream, ext, mime, is_zip, page_num = convert_pdf_to_image(f, fmt=fmt, dpi=dpi, pages=pages)

        if is_zip:
            dl_name = f"{base_name}_gambar.zip"
        else:
            dl_name = f"{base_name}_halaman_{page_num}.{ext}"

        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=dl_name,
            mimetype=mime
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Konversi PDF ke Gambar', 'error': f"Terjadi kesalahan: {str(e)}"}), 500

# -------------------------------------------------------------
# 7. API: GABUNG PDF (MERGE PDF)
# -------------------------------------------------------------
@app.route('/api/pdf/merge', methods=['POST'])
def api_pdf_merge():
    try:
        files = request.files.getlist('files')
        if not files or len(files) == 0 or not files[0].filename:
            return jsonify({'error_title': 'File Belum Dipilih', 'error': 'Silakan pilih minimal 2 file PDF untuk digabungkan.'}), 400

        pdf_files = [f for f in files if f.filename.lower().endswith('.pdf')]
        if len(pdf_files) < 2:
            return jsonify({'error_title': 'Jumlah File Kurang', 'error': 'Pilih minimal 2 file PDF untuk digabungkan.'}), 400

        out_stream = merge_pdfs(pdf_files)
        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name="Dokumen_Gabungan.pdf",
            mimetype='application/pdf'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Menggabungkan PDF', 'error': str(e)}), 500

# -------------------------------------------------------------
# 8. API: PISAH PDF (SPLIT PDF)
# -------------------------------------------------------------
@app.route('/api/pdf/split', methods=['POST'])
def api_pdf_split():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File harus berformat .pdf'}), 400

        base_name = os.path.splitext(f.filename)[0]
        split_mode = request.form.get('split_mode', 'all')
        ranges = request.form.get('ranges', '')

        zip_buf = split_pdf(f, split_mode=split_mode, ranges_str=ranges)
        resp = send_file(
            zip_buf,
            as_attachment=True,
            download_name=f"{base_name}_pisah.zip",
            mimetype='application/zip'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Memisahkan PDF', 'error': str(e)}), 500

# -------------------------------------------------------------
# 9. API: HAPUS HALAMAN PDF (REMOVE PAGES)
# -------------------------------------------------------------
@app.route('/api/pdf/remove-pages', methods=['POST'])
def api_pdf_remove_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File harus berformat .pdf'}), 400

        pages = request.form.get('pages', '').strip()
        if not pages:
            return jsonify({'error_title': 'Halaman Belum Ditentukan', 'error': 'Ketik nomor halaman yang ingin dihapus (contoh: 2, 4-6).'}), 400

        base_name = os.path.splitext(f.filename)[0]
        out_stream = remove_pdf_pages(f, pages)
        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=f"{base_name}_halaman_dihapus.pdf",
            mimetype='application/pdf'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Menghapus Halaman', 'error': str(e)}), 500

# -------------------------------------------------------------
# 10. API: EKSTRAK HALAMAN PDF (EXTRACT PAGES)
# -------------------------------------------------------------
@app.route('/api/pdf/extract-pages', methods=['POST'])
def api_pdf_extract_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File harus berformat .pdf'}), 400

        pages = request.form.get('pages', '').strip()
        if not pages:
            return jsonify({'error_title': 'Halaman Belum Ditentukan', 'error': 'Ketik nomor halaman yang ingin diekstrak (contoh: 1, 3, 5-8).'}), 400

        base_name = os.path.splitext(f.filename)[0]
        out_stream = extract_pdf_pages(f, pages)
        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=f"{base_name}_halaman_terpilih.pdf",
            mimetype='application/pdf'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Mengekstrak Halaman', 'error': str(e)}), 500

# -------------------------------------------------------------
# 11. API: SUSUN ULANG HALAMAN PDF (REORDER PAGES)
# -------------------------------------------------------------
@app.route('/api/pdf/reorder-pages', methods=['POST'])
def api_pdf_reorder_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File harus berformat .pdf'}), 400

        order = request.form.get('order', '').strip()
        rotations = request.form.get('rotations', '').strip()
        if not order:
            return jsonify({'error_title': 'Urutan Belum Ditentukan', 'error': 'Ketik atau susun urutan halaman baru.'}), 400

        base_name = os.path.splitext(f.filename)[0]
        out_stream = reorder_pdf_pages(f, order, rotations=rotations if rotations else None)
        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=f"{base_name}_diurutkan.pdf",
            mimetype='application/pdf'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Menyusun Ulang Halaman', 'error': str(e)}), 500

# -------------------------------------------------------------
# 12. API: KOMPRES UKURAN PDF (COMPRESS PDF)
# -------------------------------------------------------------
@app.route('/api/pdf/compress', methods=['POST'])
def api_pdf_compress():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File harus berformat .pdf'}), 400

        level = request.form.get('level', 'recommended')
        base_name = os.path.splitext(f.filename)[0]

        out_stream, orig_len, new_len, saved_pct = compress_pdf(f, level=level)
        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=f"{base_name}_terkompresi.pdf",
            mimetype='application/pdf'
        )
        resp.headers["X-Saved-Percent"] = str(saved_pct)
        resp.headers["X-Original-Size"] = str(orig_len)
        resp.headers["X-Compressed-Size"] = str(new_len)
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition, X-Saved-Percent, X-Original-Size, X-Compressed-Size"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Kompres PDF', 'error': str(e)}), 500

# -------------------------------------------------------------
# 13. API: GAMBAR KE PDF (IMAGE TO PDF)
# -------------------------------------------------------------
@app.route('/api/convert/image-to-pdf', methods=['POST'])
def api_image_to_pdf():
    try:
        files = request.files.getlist('files')
        if not files or len(files) == 0 or not files[0].filename:
            if 'file' in request.files and request.files['file'].filename:
                files = [request.files['file']]
            else:
                return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih satu atau beberapa file gambar (JPG/PNG).'}), 400

        valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
        img_files = [f for f in files if f.filename.lower().endswith(valid_exts)]
        if not img_files:
            return jsonify({'error_title': 'Bukan Gambar yang Didukung', 'error': 'Format yang didukung: JPG, PNG, WEBP, BMP.'}), 400

        page_size = request.form.get('page_size', 'fit')
        out_stream = convert_image_to_pdf(img_files, page_size=page_size)

        first_name = os.path.splitext(img_files[0].filename)[0]
        dl_name = f"{first_name}_gabungan.pdf" if len(img_files) > 1 else f"{first_name}.pdf"

        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=dl_name,
            mimetype='application/pdf'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Konversi Gambar ke PDF', 'error': str(e)}), 500

# -------------------------------------------------------------
# 14. API: PDF KE POWERPOINT (.pptx)
# -------------------------------------------------------------
@app.route('/api/convert/pdf-to-ppt', methods=['POST'])
def api_pdf_to_ppt():
    try:
        if 'file' not in request.files:
            return jsonify({'error_title': 'File Kosong', 'error': 'Silakan pilih file PDF.'}), 400
        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'error_title': 'Format Salah', 'error': 'File harus berformat .pdf'}), 400

        base_name = os.path.splitext(f.filename)[0]
        out_stream = convert_pdf_to_ppt(f)
        resp = send_file(
            out_stream,
            as_attachment=True,
            download_name=f"{base_name}_presentasi.pptx",
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp
    except Exception as e:
        return jsonify({'error_title': 'Gagal Konversi PDF ke PowerPoint', 'error': str(e)}), 500

# -------------------------------------------------------------
# RUNNER SERVER
# -------------------------------------------------------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5050

    print("=" * 65)
    print("    PORTAL KONVERSI DOKUMEN INTERNAL (100% AMAN & OFFLINE)")
    print("=" * 65)
    print(f" [Akses Komputer Ini]  : http://localhost:{port} atau http://127.0.0.1:{port}")
    print(f" [Akses Perangkat/HP]  : http://{local_ip}:{port}")
    print("=" * 65)
    print("  Fitur Aktif: HTML ke Excel | CSV ke Excel | PDF ke Word | Word ke PDF | PDF ke Gambar")

    print("  Semua proses berjalan lokal di RAM/komputer Anda (No Cloud).\n")

    app.run(host='0.0.0.0', port=port, debug=False)
