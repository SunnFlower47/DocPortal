// ============================================================
// Service: Table & Spreadsheet Converter (HTML & CSV to Excel)
// ============================================================

let currentHtmlMode = 'paste';
let extractedRows = [];

function setHtmlMode(mode) {
  currentHtmlMode = mode;
  hideAlert();
  const btnP = document.getElementById('btnHtml-paste');
  const btnU = document.getElementById('btnHtml-upload');
  const pMode = document.getElementById('htmlInputMode-paste');
  const uMode = document.getElementById('htmlInputMode-upload');

  if (btnP) btnP.classList.toggle('active', mode === 'paste');
  if (btnU) btnU.classList.toggle('active', mode === 'upload');
  if (pMode) pMode.classList.toggle('hidden', mode !== 'paste');
  if (uMode) uMode.classList.toggle('hidden', mode !== 'upload');
}

function clearHtmlText() {
  const txt = document.getElementById('htmlTextInput');
  if (txt) txt.value = '';
  hideAlert();
}

async function handleHtmlProcess() {
  hideAlert();
  const fd = new FormData();
  if (currentHtmlMode === 'paste') {
    const text = document.getElementById('htmlTextInput').value.trim();
    if (!text) {
      showAlert('Input Kosong', 'Silakan tempelkan kode HTML tabel terlebih dahulu.');
      return;
    }
    fd.append('html_text', text);
    showLoading(['Membaca teks HTML...', 'Mengekstrak tabel dan data...', 'Menyiapkan pratinjau tabel']);
  } else {
    const file = document.getElementById('file-html').files[0];
    if (!file) {
      showAlert('File Belum Dipilih', 'Pilih file HTML atau Word terlebih dahulu.');
      return;
    }
    fd.append('file', file);
    showLoading(['Membaca file input...', 'Mengekstrak tabel dari dokumen...', 'Menyiapkan pratinjau data']);
  }

  try {
    setStep(2);
    const res = await fetch('/api/parse', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) {
      hideLoading();
      showAlert(data.error_title || 'Gagal Parsing', data.error || 'Format tidak dikenali.');
      return;
    }
    setStep(3);
    extractedRows = data.data;
    renderPreview(extractedRows);
    hideLoading();
    showToast(`Berhasil mengekstrak ${data.total} baris data!`);
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

async function handleCsvProcess() {
  hideAlert();
  const file = document.getElementById('file-csv').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file CSV terlebih dahulu.');
    return;
  }

  showLoading(['Membaca file CSV...', 'Mendeteksi pemisah & encoding...', 'Menyiapkan tabel data']);
  const fd = new FormData();
  fd.append('file', file);

  try {
    setStep(2);
    const res = await fetch('/api/parse-csv', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) {
      hideLoading();
      showAlert(data.error_title || 'Gagal Parsing CSV', data.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    extractedRows = data.data;
    renderPreview(extractedRows);
    hideLoading();
    showToast(`Berhasil membaca ${data.total} baris dari CSV!`);
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

function renderPreview(rows) {
  if (!rows || !rows.length) return;
  const headers = Object.keys(rows[0]);
  const countBadge = document.getElementById('previewCountBadge');
  const thead = document.getElementById('previewThead');
  const tbody = document.getElementById('previewTbody');
  const card = document.getElementById('previewCard');

  if (countBadge) countBadge.textContent = `${rows.length} baris`;
  if (thead) thead.innerHTML = '<tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr>';
  if (tbody) {
    tbody.innerHTML = rows.slice(0, 150).map(row => {
      return '<tr>' + headers.map(h => `<td>${row[h] !== null && row[h] !== undefined ? row[h] : ''}</td>`).join('') + '</tr>';
    }).join('');
  }

  if (card) {
    card.classList.remove('hidden');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

async function downloadExcel() {
  if (!extractedRows || !extractedRows.length) {
    showAlert('Data Kosong', 'Tidak ada data untuk diekspor.');
    return;
  }
  showLoading(['Menyiapkan format Excel...', 'Menyusun tabel .xlsx...', 'Mengunduh file...']);
  try {
    setStep(2);
    const res = await fetch('/api/export-excel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: extractedRows })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert('Gagal Ekspor', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    triggerBlobDownload(blob, 'Hasil_Ekstrak_Tabel.xlsx');
    hideLoading();
    showToast('File Excel (.xlsx) berhasil diunduh!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}
