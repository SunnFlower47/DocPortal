import re
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd

def extract_text_from_docx(file_stream):
    """Mengekstrak teks HTML dari file .docx dengan penanganan error"""
    try:
        with zipfile.ZipFile(file_stream) as z:
            if 'word/document.xml' not in z.namelist():
                raise ValueError("File .docx tidak memiliki struktur dokumen Word yang valid.")
            tree = ET.fromstring(z.read('word/document.xml'))
            texts = [node.text for node in tree.iter() if node.text]
            return ''.join(texts)
    except zipfile.BadZipFile:
        raise ValueError("File yang diunggah bukan file .docx yang valid atau file rusak.")
    except Exception as e:
        raise ValueError(f"Gagal membaca file docx: {str(e)}")

def validate_input_content(content):
    """Validasi awal apakah konten menyerupai HTML"""
    cleaned = content.strip()
    if not cleaned:
        return False, "Input kosong. Silakan paste kode HTML atau upload file."
    
    # Cek apakah hanya link URL
    if cleaned.startswith(('http://', 'https://', 'www.')) and '\n' not in cleaned:
        return False, "Anda memasukkan link URL website. Sistem ini memerlukan kode HTML mentah dari website tersebut, bukan link URL-nya. (Gunakan Inspect Element di browser lalu salin elemennya)."

    # Cek keberadaan tag HTML minimal (<...>)
    if not re.search(r'<[a-zA-Z\/][^>]*>', cleaned):
        return False, "Teks yang dimasukkan terdeteksi sebagai teks biasa tanpa tag HTML. Pastikan Anda menyalin kode HTML (misal klik kanan elemen di website -> Inspect -> Copy element / Copy outerHTML)."

    return True, ""

def parse_html_data(html_content):
    """Menguraikan data tabel / kartu dari kode HTML secara toleran terhadap format yang berbeda"""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []

    # 1. Deteksi elemen <tr> (Material UI TableRow atau tabel HTML biasa)
    rows = soup.find_all('tr')
    if rows:
        for tr in rows:
            row_dict = {}
            # Cek pola label caption (MUI Typography caption)
            captions = tr.find_all(class_=lambda c: c and 'caption' in c.lower())
            if captions:
                for cap in captions:
                    label = cap.get_text(strip=True)
                    parent = cap.parent
                    # Ambil teks di dalam parent kecuali label caption itu sendiri
                    val = ''.join([s.get_text(strip=True) for s in parent.children if s != cap])
                    if label and label not in row_dict:
                        row_dict[label] = val
            else:
                # Tabel HTML standar (th/td)
                cells = tr.find_all(['td', 'th'])
                if cells:
                    for idx, td in enumerate(cells):
                        val = td.get_text(strip=True)
                        if val:
                            row_dict[f'Kolom_{idx+1}'] = val

            if row_dict:
                data.append(row_dict)

    # 2. Jika tidak ada <tr>, coba cari elemen kartu / card box (DIV / Container)
    if not data:
        cards = soup.find_all(class_=lambda c: c and any(k in c.lower() for k in ['muibox-root', 'card', 'item', 'row']))
        for card in cards:
            captions = card.find_all(class_=lambda c: c and 'caption' in c.lower())
            if captions:
                row_dict = {}
                for cap in captions:
                    label = cap.get_text(strip=True)
                    parent = cap.parent
                    val = ''.join([s.get_text(strip=True) for s in parent.children if s != cap])
                    if label and label not in row_dict:
                        row_dict[label] = val
                if row_dict and row_dict not in data:
                    data.append(row_dict)

    # 3. Fallback jika tabel menggunakan <li> atau list terstruktur
    if not data:
        items = soup.find_all(['li', 'div'])
        for item in items:
            strong = item.find(['strong', 'b'])
            if strong:
                label = strong.get_text(strip=True).rstrip(':')
                val = item.get_text(strip=True).replace(strong.get_text(strip=True), '').lstrip(': ')
                if label and val:
                    data.append({'Label': label, 'Nilai': val})

    return data

def parse_csv_data(file_stream):
    """Membaca file CSV dengan deteksi otomatis delimiter (koma atau titik koma) dan encoding"""
    try:
        try:
            df = pd.read_csv(file_stream, sep=None, engine='python', encoding='utf-8-sig')
        except UnicodeDecodeError:
            file_stream.seek(0)
            df = pd.read_csv(file_stream, sep=None, engine='python', encoding='cp1252')
        
        df = df.fillna('')
        data = df.to_dict(orient='records')
        if not data:
            raise ValueError("Tidak ada data di dalam file CSV.")
        return data
    except Exception as e:
        raise ValueError(f"Gagal membaca file CSV: {str(e)}")
