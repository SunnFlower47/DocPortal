// ============================================================
// Service: PDF Compress (Stream Optimization & MB Comparison Preview)
// ============================================================

let currentCompressLevel = 'recommended';

function setCompressLevel(level) {
  currentCompressLevel = level;
  ['recommended', 'low', 'high'].forEach(l => {
    const card = document.getElementById('card-comp-' + l);
    if (card) card.classList.toggle('selected', l === level);
    const radio = document.querySelector(`input[name="compLevel"][value="${l}"]`);
    if (radio) radio.checked = (l === level);
  });
}

async function handleCompressPdfProcess() {
  hideAlert();
  const file = document.getElementById('file-compresspdf').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file PDF yang ingin dikompres.');
    return;
  }

  showLoading([
    'Menganalisis struktur file PDF & citra gambar...',
    `Mengompresi dan downsampling citra (Level ${currentCompressLevel.toUpperCase()})...`,
    'Menyusun berkas PDF terkompresi...'
  ]);

  const fd = new FormData();
  fd.append('file', file);
  fd.append('level', currentCompressLevel);

  try {
    setStep(2);
    const res = await fetch('/api/pdf/compress', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Kompres PDF', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);

    const savedPct = res.headers.get('X-Saved-Percent') || '0';
    const origSize = parseInt(res.headers.get('X-Original-Size') || file.size, 10);
    const compSize = parseInt(res.headers.get('X-Compressed-Size') || '0', 10);

    const blob = await res.blob();
    currentCompressedBlob = blob;
    const baseName = file.name.replace(/\.pdf$/i, '');
    currentCompressedFileName = `${baseName}_terkompresi.pdf`;

    hideLoading();

    const origStr = origSize > 1048576 ? (origSize / 1048576).toFixed(2) + ' MB' : Math.round(origSize / 1024) + ' KB';
    const compStr = compSize > 1048576 ? (compSize / 1048576).toFixed(2) + ' MB' : Math.round(compSize / 1024) + ' KB';
    const pctNum = parseFloat(savedPct);

    const resultCard = document.getElementById('compressResultCard');
    const origEl = document.getElementById('compOrigSize');
    const savedEl = document.getElementById('compSavedPct');
    const newEl = document.getElementById('compNewSize');
    const dlBtnText = document.getElementById('compDownloadBtnText');

    if (origEl) origEl.textContent = origStr;
    if (savedEl) savedEl.textContent = pctNum > 0 ? `-${pctNum}%` : 'Optimal';
    if (newEl) newEl.textContent = compStr;
    if (dlBtnText) dlBtnText.textContent = `Unduh PDF Terkompresi (${compStr})`;

    if (resultCard) {
      resultCard.classList.remove('hidden');
      resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    showToast(`Kompresi selesai! Ukuran menjadi ${compStr} (Hemat ${pctNum}%)`);
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

function downloadCompressedPdf() {
  if (!currentCompressedBlob) {
    showAlert('Belum Ada Hasil', 'Silakan jalankan kompresi terlebih dahulu.');
    return;
  }
  triggerBlobDownload(currentCompressedBlob, currentCompressedFileName);
  showToast('File PDF terkompresi berhasil diunduh!');
}
