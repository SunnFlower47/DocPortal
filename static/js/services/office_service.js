// ============================================================
// Service: Office Document Converter (PDF to Word, Word to PDF, PDF to PPT)
// ============================================================

let currentPdfMode = 'standard';

function setPdfMode(mode) {
  currentPdfMode = mode;
  ['standard', 'ocr', 'hybrid'].forEach(m => {
    const card = document.getElementById('card-pdf-' + m);
    if (card) card.classList.toggle('selected', m === mode);
    const radio = document.querySelector(`input[name="pdfMode"][value="${m}"]`);
    if (radio) radio.checked = (m === mode);
  });
  const label = document.getElementById('btnPdfToWordLabel');
  if (label) {
    if (mode === 'ocr') label.textContent = 'Konversi ke Word (Mode AI OCR)';
    else if (mode === 'hybrid') label.textContent = 'Konversi ke Word (Mode Hybrid)';
    else label.textContent = 'Konversi ke Word (.docx)';
  }
}

async function handlePdfToWordProcess() {
  hideAlert();
  const file = document.getElementById('file-pdf').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file PDF terlebih dahulu.');
    return;
  }

  let step2Text = 'Menganalisis tata letak halaman PDF...';
  let suffix = '_converted.docx';
  if (currentPdfMode === 'ocr') {
    step2Text = 'AI OCR membaca teks dari scan foto...';
    suffix = '_ocr.docx';
  } else if (currentPdfMode === 'hybrid') {
    step2Text = 'Mode Hybrid merender background anti kotak hitam & menyusun teks...';
    suffix = '_hybrid.docx';
  }

  showLoading([
    'Membuka file PDF...',
    step2Text,
    'Menyusun dokumen Word (.docx)'
  ]);

  const fd = new FormData();
  fd.append('file', file);
  fd.append('mode', currentPdfMode);

  try {
    setStep(2);
    const res = await fetch('/api/convert/pdf-to-word', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Konversi', err.error || 'Terjadi kesalahan pada dokumen.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    const baseName = file.name.replace(/\.pdf$/i, '');
    const outName = `${baseName}${suffix}`;
    triggerBlobDownload(blob, outName);
    hideLoading();
    showToast('Dokumen Word (.docx) berhasil diunduh!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

async function handleWordToPdfProcess() {
  hideAlert();
  const file = document.getElementById('file-word').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file Word (.docx) terlebih dahulu.');
    return;
  }

  showLoading([
    'Membuka dokumen Word...',
    'LibreOffice merender tata letak & ukuran kertas asli...',
    'Menghasilkan file PDF...'
  ]);

  const fd = new FormData();
  fd.append('file', file);

  try {
    setStep(2);
    const res = await fetch('/api/convert/word-to-pdf', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Konversi', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    const baseName = file.name.replace(/\.docx$/i, '');
    triggerBlobDownload(blob, `${baseName}_converted.pdf`);
    hideLoading();
    showToast('Dokumen PDF berhasil diunduh dengan layout 100% presisi!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

async function handlePdfToPptProcess() {
  hideAlert();
  const file = document.getElementById('file-pdfppt').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file PDF terlebih dahulu.');
    return;
  }

  showLoading([
    'Membaca dokumen PDF...',
    'Mengonversi slide ke tata letak presentasi PowerPoint...',
    'Menyusun berkas PowerPoint (.pptx)...'
  ]);

  const fd = new FormData();
  fd.append('file', file);

  try {
    setStep(2);
    const res = await fetch('/api/convert/pdf-to-ppt', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Konversi', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    const baseName = file.name.replace(/\.pdf$/i, '');
    triggerBlobDownload(blob, `${baseName}_presentasi.pptx`);
    hideLoading();
    showToast('File PowerPoint (.pptx) berhasil diunduh!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}
