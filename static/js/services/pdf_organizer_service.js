// ============================================================
// Service: PDF Organizer (Visual Merge, Split, & Visual Page Manager)
// ============================================================

let mergePdfFiles = [];
let currentSplitMode = 'all';

// --- MERGE PDF FUNCTIONS ---
function addMergePdfFiles(files) {
  const validPdfs = files.filter(f => f.name.toLowerCase().endsWith('.pdf'));
  if (!validPdfs.length) {
    showAlert('Bukan File PDF', 'File yang dipilih harus berekstensi .pdf');
    return;
  }

  validPdfs.forEach(f => {
    mergePdfFiles.push({
      id: 'm_' + Date.now() + '_' + Math.random().toString(36).substring(2, 8),
      file: f,
      pageCount: null
    });
  });

  renderMergeFilesVisualGrid();
  hideAlert();
}

function removeMergeFile(fileId) {
  mergePdfFiles = mergePdfFiles.filter(item => item.id !== fileId);
  renderMergeFilesVisualGrid();
}

function clearMergePdfFiles() {
  mergePdfFiles = [];
  renderMergeFilesVisualGrid();
}

function updateMergeOrderFromDOM() {
  const grid = document.getElementById('mergeCardsGrid');
  if (!grid) return;
  const cards = grid.querySelectorAll('.merge-card');
  const newOrderFiles = [];

  cards.forEach((card, idx) => {
    const badge = card.querySelector('.card-order-badge');
    if (badge) badge.textContent = `#${idx + 1}`;
    const id = card.dataset.fileId;
    const found = mergePdfFiles.find(item => item.id === id);
    if (found) newOrderFiles.push(found);
  });

  if (newOrderFiles.length === mergePdfFiles.length) {
    mergePdfFiles = newOrderFiles;
  }
}

async function renderMergeFilesVisualGrid() {
  const container = document.getElementById('mergeFilesContainer');
  const countEl = document.getElementById('mergeFilesCount');
  const grid = document.getElementById('mergeCardsGrid');
  const dz = document.getElementById('dz-mergepdf');
  const actionBtns = document.getElementById('mergeActionButtons');
  const btnMergeText = document.getElementById('btnMergeText');

  if (!container || !grid) return;

  if (mergePdfFiles.length === 0) {
    container.classList.add('hidden');
    if (actionBtns) actionBtns.classList.add('hidden');
    if (dz) dz.classList.remove('hidden');
    if (btnMergeText) btnMergeText.textContent = 'Gabungkan Semua PDF';
    return;
  }

  container.classList.remove('hidden');
  if (actionBtns) actionBtns.classList.remove('hidden');
  if (countEl) countEl.textContent = mergePdfFiles.length;
  if (btnMergeText) btnMergeText.textContent = `Gabungkan ${mergePdfFiles.length} PDF Sekarang`;

  grid.innerHTML = mergePdfFiles.map((item, i) => {
    const f = item.file;
    const sizeStr = f.size > 1048576 ? (f.size / 1048576).toFixed(1) + ' MB' : Math.round(f.size / 1024) + ' KB';
    return `
      <div class="visual-card merge-card" data-file-id="${item.id}">
        <div class="card-order-badge">#${i + 1}</div>
        <button type="button" onclick="removeMergeFile('${item.id}')" class="card-action-btn btn-delete absolute top-2 right-2 z-10" title="Hapus file ini">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
        <div class="visual-card-canvas-wrap">
          <canvas id="canvas-merge-${item.id}"></canvas>
          <div id="spinner-merge-${item.id}" class="absolute inset-0 flex items-center justify-center bg-slate-50/80">
            <svg class="animate-spin w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </div>
        <div class="p-2.5 bg-white">
          <p class="text-xs font-semibold text-slate-800 truncate" title="${f.name}">${f.name}</p>
          <div class="flex items-center justify-between text-[11px] text-slate-400 mt-1">
            <span>${sizeStr}</span>
            <span id="page-count-${item.id}">...</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  if (window.Sortable) {
    if (mergeSortableInstance) {
      mergeSortableInstance.destroy();
    }
    mergeSortableInstance = new Sortable(grid, {
      animation: 200,
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      onEnd: updateMergeOrderFromDOM
    });
  }

  for (const item of mergePdfFiles) {
    renderCardThumbnail(item);
  }
}

async function renderCardThumbnail(item) {
  const canvas = document.getElementById(`canvas-merge-${item.id}`);
  const spinner = document.getElementById(`spinner-merge-${item.id}`);
  const countSpan = document.getElementById(`page-count-${item.id}`);
  if (!canvas || !window.pdfjsLib) return;

  try {
    const arrayBuffer = await item.file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    item.pageCount = pdf.numPages;
    if (countSpan) countSpan.textContent = `${pdf.numPages} hal`;

    const page = await pdf.getPage(1);
    const viewport = page.getViewport({ scale: 0.35 });
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    const ctx = canvas.getContext('2d');
    await page.render({ canvasContext: ctx, viewport }).promise;
    if (spinner) spinner.remove();
  } catch (err) {
    console.warn('Gagal merender thumbnail:', err);
    if (spinner) spinner.innerHTML = '<span class="text-[10px] text-slate-400 font-semibold">PDF</span>';
  }
}

async function handleMergePdfProcess() {
  hideAlert();
  if (mergePdfFiles.length < 2) {
    showAlert('File Kurang', 'Silakan pilih minimal 2 file PDF untuk digabungkan.');
    return;
  }

  showLoading([
    `Membaca ${mergePdfFiles.length} file PDF...`,
    'Menggabungkan halaman sesuai urutan visual...',
    'Menyimpan file PDF terpadu...'
  ]);

  const fd = new FormData();
  mergePdfFiles.forEach(item => fd.append('files', item.file));

  try {
    setStep(2);
    const res = await fetch('/api/pdf/merge', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Menggabungkan PDF', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    triggerBlobDownload(blob, 'Dokumen_Gabungan.pdf');
    hideLoading();
    showToast(`Berhasil menggabungkan ${mergePdfFiles.length} file PDF!`);
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

// --- SPLIT PDF FUNCTIONS ---
function setSplitMode(mode) {
  currentSplitMode = mode;
  const cAll = document.getElementById('card-split-all');
  const cRange = document.getElementById('card-split-range');
  if (cAll) cAll.classList.toggle('selected', mode === 'all');
  if (cRange) cRange.classList.toggle('selected', mode === 'range');
  const radioAll = document.querySelector('input[name="splitMode"][value="all"]');
  const radioRange = document.querySelector('input[name="splitMode"][value="range"]');
  if (radioAll) radioAll.checked = (mode === 'all');
  if (radioRange) radioRange.checked = (mode === 'range');
  const rangeBox = document.getElementById('splitRangeBox');
  if (rangeBox) rangeBox.classList.toggle('hidden', mode !== 'range');
}

async function handleSplitPdfProcess() {
  hideAlert();
  const file = document.getElementById('file-splitpdf').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file PDF yang akan dipisah.');
    return;
  }

  let rangesVal = '';
  if (currentSplitMode === 'range') {
    rangesVal = document.getElementById('splitRangeInput').value.trim();
    if (!rangesVal) {
      showAlert('Rentang Belum Ditentukan', 'Silakan ketik rentang halaman (contoh: 1-3, 4-6).');
      return;
    }
  }

  showLoading([
    'Membuka file PDF...',
    currentSplitMode === 'all' ? 'Memecah tiap halaman menjadi PDF individual...' : `Memisahkan halaman sesuai rentang (${rangesVal})...`,
    'Mengemas berkas ke dalam arsip ZIP...'
  ]);

  const fd = new FormData();
  fd.append('file', file);
  fd.append('split_mode', currentSplitMode);
  fd.append('ranges', rangesVal);

  try {
    setStep(2);
    const res = await fetch('/api/pdf/split', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Memisahkan PDF', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    const baseName = file.name.replace(/\.pdf$/i, '');
    triggerBlobDownload(blob, `${baseName}_pisah.zip`);
    hideLoading();
    showToast('Dokumen PDF berhasil dipisahkan!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}

// --- VISUAL PAGE MANAGER FUNCTIONS ---
async function loadPageManagerDocument(file) {
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    showAlert('Format Salah', 'Silakan pilih file berformat PDF.');
    return;
  }

  currentPmFile = file;
  hideAlert();
  showLoading([
    'Membuka dokumen PDF...',
    'Merender visual thumbnail setiap lembar halaman...',
    'Menyiapkan kanvas interaktif...'
  ]);

  try {
    const arrayBuffer = await file.arrayBuffer();
    currentPmPdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    const numPages = currentPmPdfDoc.numPages;

    const dz = document.getElementById('dz-pagemgr');
    const headerBadge = document.getElementById('pmFileHeaderBadge');
    const fileInfo = document.getElementById('pmFileInfo');
    const workspace = document.getElementById('pageManagerWorkspace');

    if (dz) dz.classList.add('hidden');
    if (headerBadge) headerBadge.classList.remove('hidden');
    const sizeStr = file.size > 1048576 ? (file.size / 1048576).toFixed(1) + ' MB' : Math.round(file.size / 1024) + ' KB';
    if (fileInfo) fileInfo.textContent = `📄 ${file.name} (${numPages} Halaman · ${sizeStr})`;
    if (workspace) workspace.classList.remove('hidden');

    const grid = document.getElementById('pageCardsGrid');
    grid.innerHTML = '';

    for (let p = 1; p <= numPages; p++) {
      const card = document.createElement('div');
      card.className = 'visual-card page-card';
      card.id = `pm-card-${p}`;
      card.dataset.origPage = p;
      card.dataset.rotation = '0';
      card.dataset.excluded = 'false';

      card.innerHTML = `
        <div class="card-order-badge">Hal ${p}</div>
        <div class="absolute top-2 right-2 z-10 flex items-center gap-1">
          <button type="button" onclick="rotateCardPage(this, 90)" class="card-action-btn btn-rotate" title="Putar 90°">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          </button>
          <button type="button" onclick="toggleExcludePage(this)" class="card-action-btn btn-delete" title="Hapus / Pulihkan Halaman">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
          </button>
        </div>
        <div class="visual-card-canvas-wrap">
          <canvas id="pm-canvas-${p}"></canvas>
          <div class="excluded-overlay hidden absolute inset-0 bg-rose-900/60 backdrop-blur-[1px] flex flex-col items-center justify-center text-white z-20">
            <svg class="w-6 h-6 text-rose-300 mb-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            <span class="text-[11px] font-bold uppercase tracking-wider">Dihapus</span>
          </div>
        </div>
        <div class="p-2 bg-white flex items-center justify-between text-[11px] text-slate-500">
          <span class="font-medium">Asli #${p}</span>
          <span class="rot-tag hidden text-[10px] font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">0°</span>
        </div>
      `;
      grid.appendChild(card);
    }

    if (window.Sortable) {
      if (pmSortableInstance) pmSortableInstance.destroy();
      pmSortableInstance = new Sortable(grid, {
        animation: 200,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        onEnd: updatePageManagerStats
      });
    }

    for (let p = 1; p <= numPages; p++) {
      renderPageThumbnail(p);
    }

    updatePageManagerStats();
    hideLoading();
  } catch (err) {
    hideLoading();
    showAlert('Gagal Memuat PDF', 'Tidak dapat membaca lembar halaman dokumen: ' + String(err));
  }
}

async function renderPageThumbnail(pageNum) {
  const canvas = document.getElementById(`pm-canvas-${pageNum}`);
  if (!canvas || !currentPmPdfDoc) return;
  try {
    const page = await currentPmPdfDoc.getPage(pageNum);
    const viewport = page.getViewport({ scale: 0.35 });
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    const ctx = canvas.getContext('2d');
    await page.render({ canvasContext: ctx, viewport }).promise;
  } catch (e) {
    console.warn(`Gagal merender thumbnail halaman ${pageNum}:`, e);
  }
}

function rotateCardPage(el, angle) {
  const card = el.closest('.page-card');
  if (!card) return;
  let curRot = (parseInt(card.dataset.rotation || '0', 10) + angle) % 360;
  card.dataset.rotation = curRot.toString();

  const canvas = card.querySelector('canvas');
  if (canvas) {
    canvas.style.transform = curRot !== 0 ? `rotate(${curRot}deg)` : '';
  }

  const rotTag = card.querySelector('.rot-tag');
  if (rotTag) {
    if (curRot !== 0) {
      rotTag.textContent = `${curRot}°`;
      rotTag.classList.remove('hidden');
    } else {
      rotTag.classList.add('hidden');
    }
  }
  updatePageManagerStats();
}

function toggleExcludePage(el) {
  const card = el.closest('.page-card');
  if (!card) return;
  const isExcluded = card.dataset.excluded === 'true';
  card.dataset.excluded = (!isExcluded).toString();
  card.classList.toggle('is-excluded', !isExcluded);
  updatePageManagerStats();
}

function rotateAllPages(angle) {
  const cards = document.querySelectorAll('#pageCardsGrid .page-card');
  cards.forEach(card => {
    let curRot = (parseInt(card.dataset.rotation || '0', 10) + angle) % 360;
    card.dataset.rotation = curRot.toString();
    const canvas = card.querySelector('canvas');
    if (canvas) canvas.style.transform = curRot !== 0 ? `rotate(${curRot}deg)` : '';
    const rotTag = card.querySelector('.rot-tag');
    if (rotTag) {
      if (curRot !== 0) {
        rotTag.textContent = `${curRot}°`;
        rotTag.classList.remove('hidden');
      } else {
        rotTag.classList.add('hidden');
      }
    }
  });
  updatePageManagerStats();
}

function toggleRestoreAllPages() {
  const cards = document.querySelectorAll('#pageCardsGrid .page-card');
  cards.forEach(card => {
    card.dataset.excluded = 'false';
    card.classList.remove('is-excluded');
  });
  updatePageManagerStats();
}

function resetPageOrder() {
  const grid = document.getElementById('pageCardsGrid');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.page-card'));
  cards.sort((a, b) => parseInt(a.dataset.origPage, 10) - parseInt(b.dataset.origPage, 10));
  cards.forEach(card => {
    card.dataset.rotation = '0';
    card.dataset.excluded = 'false';
    card.classList.remove('is-excluded');
    const canvas = card.querySelector('canvas');
    if (canvas) canvas.style.transform = '';
    const rotTag = card.querySelector('.rot-tag');
    if (rotTag) rotTag.classList.add('hidden');
    grid.appendChild(card);
  });
  updatePageManagerStats();
}

function updatePageManagerStats() {
  const grid = document.getElementById('pageCardsGrid');
  if (!grid) return;
  const cards = grid.querySelectorAll('.page-card');
  let kept = 0;
  let excluded = 0;

  cards.forEach((card, idx) => {
    const badge = card.querySelector('.card-order-badge');
    if (badge) badge.textContent = `Posisi #${idx + 1}`;
    if (card.dataset.excluded === 'true') {
      excluded++;
    } else {
      kept++;
    }
  });

  const sumEl = document.getElementById('pmSummaryText');
  if (sumEl) sumEl.textContent = `Total ${cards.length} Halaman (${kept} aktif, ${excluded} dibuang)`;
  const btnTxt = document.getElementById('btnPageManagerText');
  if (btnTxt) btnTxt.textContent = `Simpan & Unduh PDF (${kept} Halaman)`;
}

async function handlePageManagerProcess() {
  hideAlert();
  const file = currentPmFile || document.getElementById('file-pagemgr').files[0];
  if (!file) {
    showAlert('File Belum Dipilih', 'Silakan pilih file PDF terlebih dahulu.');
    return;
  }

  const manualInp = document.getElementById('pageManagerInput') ? document.getElementById('pageManagerInput').value.trim() : '';
  let orderStr = '';
  let rotationsMap = {};

  if (manualInp) {
    orderStr = manualInp;
  } else {
    const grid = document.getElementById('pageCardsGrid');
    const cards = grid ? Array.from(grid.querySelectorAll('.page-card')) : [];
    const keptCards = cards.filter(c => c.dataset.excluded !== 'true');

    if (!keptCards.length) {
      showAlert('Semua Halaman Dihapus', 'Semua lembar halaman ditandai untuk dihapus. Sisakan minimal 1 halaman.');
      return;
    }

    orderStr = keptCards.map(c => c.dataset.origPage).join(',');
    keptCards.forEach((c, newIdx) => {
      const rot = parseInt(c.dataset.rotation || '0', 10);
      if (rot !== 0) {
        rotationsMap[String(newIdx)] = rot;
        rotationsMap[String(newIdx + 1)] = rot;
        rotationsMap[c.dataset.origPage] = rot;
      }
    });
  }

  showLoading([
    'Membuka file PDF...',
    'Menyusun urutan & menerapkan rotasi halaman...',
    'Menyimpan file PDF hasil kelola...'
  ]);

  const fd = new FormData();
  fd.append('file', file);
  fd.append('order', orderStr);
  if (Object.keys(rotationsMap).length > 0) {
    fd.append('rotations', JSON.stringify(rotationsMap));
  }

  try {
    setStep(2);
    const res = await fetch('/api/pdf/reorder-pages', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      hideLoading();
      showAlert(err.error_title || 'Gagal Memproses Halaman', err.error || 'Terjadi kesalahan.');
      return;
    }
    setStep(3);
    const blob = await res.blob();
    const baseName = file.name.replace(/\.pdf$/i, '');
    triggerBlobDownload(blob, `${baseName}_kelola.pdf`);
    hideLoading();
    showToast('Dokumen PDF baru berhasil disimpan dan diunduh!');
  } catch (err) {
    hideLoading();
    showAlert('Kesalahan Jaringan', String(err));
  }
}
