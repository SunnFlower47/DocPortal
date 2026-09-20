// ============================================================
// Service: Image & PDF Converter (PDF to Image & Image to PDF)
// ============================================================

let imgFormat = 'png';
let imgDpi = 150;
let imgPages = 'all';
let imgToPdfPageSize = 'fit';
let imageToPdfFiles = [];

function setImgFormat(fmt) {
  imgFormat = fmt;
  const btnP = document.getElementById('btnFmt-png');
  const btnJ = document.getElementById('btnFmt-jpg');
  if (btnP) btnP.classList.toggle('active', fmt === 'png');
  if (btnJ) btnJ.classList.toggle('active', fmt === 'jpg');
}

function setImgDpi(dpi) {
  imgDpi = dpi;
  [96, 150, 300].forEach(d => {
    const btn = document.getElementById('btnDpi-' + d);
    if (btn) btn.classList.toggle('active', d === dpi);
  });
}

function setImgPages(pages) {
  imgPages = pages;
  ['all', 'first', 'custom'].forEach(p => {
    const btn = document.getElementById('btnPages-' + p);
    if (btn) btn.classList.toggle('active', p === pages);
  });
  const customBox = document.getElementById('customPagesBox');
  if (customBox) customBox.classList.toggle('hidden', pages !== 'custom');
}

function addImageToPdfFiles(files) {
  const validExts = ['.jpg', '.jpeg', '.png', '.webp', '.bmp'];
  const validImages = files.filter(f => {
    const name = f.name.toLowerCase();
    return validExts.some(ext => name.endsWith(ext));
  });
  if (!validImages.length) {
    showAlert('Bukan Format Gambar', 'Pilih file dengan ekstensi JPG, PNG, WEBP, atau BMP.');
    return;
  }
  imageToPdfFiles.push(...validImages);
  renderImageFilesList();
  hideAlert();
}

function removeImageFile(idx) {
  imageToPdfFiles.splice(idx, 1);
  renderImageFilesList();
}

function clearImgToPdfFiles() {
  imageToPdfFiles = [];
  renderImageFilesList();
}

function renderImageFilesList() {
  const container = document.getElementById('imgFilesContainer');
  const countEl = document.getElementById('imgFilesCount');
  const listEl = document.getElementById('imgFilesList');
  if (!container || !listEl) return;

  if (imageToPdfFiles.length === 0) {
    container.classList.add('hidden');
    return;
  }

  container.classList.remove('hidden');
  if (countEl) countEl.textContent = imageToPdfFiles.length;

  listEl.innerHTML = imageToPdfFiles.map((f, i) => {
    const sizeStr = f.size > 1048576 ? (f.size / 1048576).toFixed(1) + ' MB' : Math.round(f.size / 1024) + ' KB';
    return `
      <div class="file-item">
        <div class="flex items-center gap-2.5 min-w-0">
          <span class="w-5 h-5 rounded-full bg-teal-100 text-teal-700 text-[11px] font-bold flex items-center justify-center flex-shrink-0">${i + 1}</span>
          <svg class="w-4 h-4 text-teal-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          <span class="text-xs font-semibold text-slate-700 truncate">${f.name}</span>
          <span class="text-[11px] text-slate-400 font-normal">(${sizeStr})</span>
        </div>
        <button type="button" onclick="removeImageFile(${i})" class="text-slate-400 hover:text-rose-600 p-1 rounded-md" title="Hapus gambar ini">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
    `;
  }).join('');
}

function setImgToPdfPageSize(size) {
  imgToPdfPageSize = size;
  const btnFit = document.getElementById('btnImgPdfSize-fit');
  const btnA4 = document.getElementById('btnImgPdfSize-a4');
  if (btnFit) btnFit.classList.toggle('active', size === 'fit');
  if (btnA4) btnA4.classList.toggle('active', size === 'a4');
}

async function handlePdfToImageProcess() {
  hideAlert();
  const file = document.getElementById('file-pdfimg').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file PDF terlebih dahulu.');
    return;
  }

  let pagesVal = imgPages;
  if (imgPages === 'custom') {
    const customInput = document.getElementById('customPagesInput').value.trim();
    if (!customInput) {
      showAlert('Halaman Belum Ditentukan', 'Silakan ketik nomor halaman yang ingin diekstrak (contoh: 1, 3, 5-8).');
      return;
    }
    pagesVal = customInput;
  }

  showLoading([
    'Membuka file PDF...',
    `Merender ke ${imgFormat.toUpperCase()} (${imgDpi} DPI)...`,
    pagesVal === 'first' ? 'Menyimpan gambar halaman 1...' : (pagesVal === 'all' ? 'Mengemas semua halaman dalam file ZIP...' : `Memproses halaman terpilih (${pagesVal})...`)
  ]);

  const fd = new FormData();
  fd.append('file', file);
  fd.append('format', imgFormat);
  fd.append('dpi', imgDpi);
  fd.append('pages', pagesVal);

  try {
    setStep(2);
    const res = await fetch('/api/convert/pdf-to-image', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Ekspor', err.error || 'Terjadi kesalahan rendering gambar.');
      return;
    }
    setStep(3);
    const blob = await res.blob();

    if (blob.type && blob.type.startsWith('image/')) {
      const previewUrl = URL.createObjectURL(blob);
      const previewEl = document.getElementById('imgPreviewEl');
      if (previewEl) previewEl.src = previewUrl;
      const wrap = document.getElementById('imgPreviewWrapper');
      if (wrap) wrap.classList.remove('hidden');
    }

    const disposition = res.headers.get('content-disposition');
    let dlName = '';
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (match && match[1]) {
        dlName = match[1].replace(/['"]/g, '').trim();
      }
    }
    if (!dlName) {
      const baseName = file.name.replace(/\.pdf$/i, '');
      const isZip = blob.type === 'application/zip' || (!blob.type.startsWith('image/'));
      dlName = isZip ? `${baseName}_gambar.zip` : `${baseName}_halaman.${imgFormat}`;
    }

    triggerBlobDownload(blob, dlName);
    hideLoading();
    showToast('Gambar PDF berhasil diekstrak dan diunduh!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

async function handleImageToPdfProcess() {
  hideAlert();
  if (!imageToPdfFiles.length) {
    showAlert('Belum Ada Gambar', 'Silakan pilih minimal 1 file gambar (JPG/PNG).');
    return;
  }

  showLoading([
    `Mempersiapkan ${imageToPdfFiles.length} file gambar...`,
    `Menyusun halaman PDF (${imgToPdfPageSize.toUpperCase()})...`,
    'Menghasilkan berkas PDF...'
  ]);

  const fd = new FormData();
  imageToPdfFiles.forEach(f => fd.append('files', f));
  fd.append('page_size', imgToPdfPageSize);

  try {
    setStep(2);
    const res = await fetch('/api/convert/image-to-pdf', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Konversi', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    triggerBlobDownload(blob, 'Dokumen_Gambar.pdf');
    hideLoading();
    showToast('Dokumen PDF dari gambar berhasil dibuat!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}
