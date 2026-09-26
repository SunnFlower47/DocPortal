// ============================================================
// Service: Navigation & Tool Switching
// ============================================================

let currentTool = 'dashboard';

const TOOL_META = {
  dashboard:   { title: 'Dashboard Utama', sub: 'Pusat konversi & pengelolaan dokumen internal kantor' },
  htmlToExcel: { title: 'HTML ke Excel', sub: 'Ekstrak tabel dan elemen kartu dari kode HTML halaman web' },
  csvToExcel:  { title: 'CSV ke Excel',  sub: 'Ubah data tabel CSV menjadi spreadsheet Microsoft Excel (.xlsx)' },
  pdfToWord:   { title: 'PDF ke Word',   sub: 'Konversi file PDF ke dokumen Word (.docx) — Mode Standar, OCR & Hybrid' },
  wordToPdf:   { title: 'Word ke PDF',   sub: 'Konversi Word (.docx) ke PDF — ukuran kertas, margin & kop surat identik asli' },
  pdfToPpt:    { title: 'PDF ke PPT',    sub: 'Konversi slide PDF menjadi presentasi Microsoft PowerPoint (.pptx)' },
  pdfToImage:  { title: 'PDF ke Gambar', sub: 'Ekspor setiap halaman PDF menjadi file gambar PNG atau JPG (bisa ZIP)' },
  imageToPdf:  { title: 'Gambar ke PDF', sub: 'Satukan file JPG / PNG / WEBP menjadi satu berkas dokumen PDF' },
  mergePdf:    { title: 'Gabung PDF',    sub: 'Gabungkan beberapa file dokumen PDF menjadi satu file utuh' },
  splitPdf:    { title: 'Pisah PDF',     sub: 'Pisah dokumen PDF per lembar ke ZIP atau berdasarkan rentang halaman' },
  pageManager: { title: 'Kelola Halaman PDF', sub: 'Hapus, ekstrak, atau atur ulang urutan lembar halaman PDF' },
  compressPdf: { title: 'Kompres PDF',   sub: 'Kecilkan ukuran file dokumen PDF tanpa merusak struktur dan teks' },
  compressImage: { title: 'Kompres Gambar', sub: 'Kecilkan ukuran file JPG, PNG, WEBP, BMP — atur kualitas dan resize dimensi' }
};

function selectTool(key) {
  currentTool = key;
  hideAlert();
  const preview = document.getElementById('previewCard');
  if (preview) preview.classList.add('hidden');
  const badge = document.getElementById('fileInfoBadge');
  if (badge) {
    badge.classList.add('hidden');
    badge.classList.remove('flex');
  }

  Object.keys(TOOL_META).forEach(t => {
    const btn = document.getElementById('btn-' + t);
    const view = document.getElementById('view-' + t);
    if (btn) btn.classList.toggle('active', t === key);
    if (view) view.classList.toggle('hidden', t !== key);
  });

  const titleEl = document.getElementById('currentToolTitle');
  const subEl = document.getElementById('currentToolSub');
  if (titleEl && TOOL_META[key]) titleEl.textContent = TOOL_META[key].title;
  if (subEl && TOOL_META[key]) subEl.textContent = TOOL_META[key].sub;

  closeMobileMenu();
}

function toggleMobileMenu() {
  const sidebar = document.getElementById('sidebarDrawer');
  const backdrop = document.getElementById('mobileBackdrop');
  if (!sidebar || !backdrop) return;
  
  const isClosed = sidebar.classList.contains('-translate-x-full');
  if (isClosed) {
    sidebar.classList.remove('-translate-x-full');
    sidebar.classList.add('translate-x-0');
    backdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  } else {
    closeMobileMenu();
  }
}

function closeMobileMenu() {
  const sidebar = document.getElementById('sidebarDrawer');
  const backdrop = document.getElementById('mobileBackdrop');
  if (sidebar) {
    sidebar.classList.add('-translate-x-full');
    sidebar.classList.remove('translate-x-0');
  }
  if (backdrop) backdrop.classList.add('hidden');
  document.body.style.overflow = '';
}

// ── Dashboard Live Filter & Search ──
let currentDashCategory = 'all';

function filterDashboardTools(query) {
  const q = (query || '').toLowerCase().trim();
  const cards = document.querySelectorAll('[data-keywords]');
  let matchCount = 0;

  cards.forEach(card => {
    const keywords = (card.getAttribute('data-keywords') || '').toLowerCase();
    const titleEl = card.querySelector('.dash-card-title');
    const descEl  = card.querySelector('.dash-card-desc');
    const title   = titleEl ? titleEl.textContent.toLowerCase() : '';
    const desc    = descEl  ? descEl.textContent.toLowerCase()  : '';
    const category = card.getAttribute('data-category') || 'all';

    const matchesCategory = (currentDashCategory === 'all' || category === currentDashCategory);
    const matchesSearch   = !q || keywords.includes(q) || title.includes(q) || desc.includes(q);

    if (matchesCategory && matchesSearch) {
      card.classList.remove('hidden');
      matchCount++;
    } else {
      card.classList.add('hidden');
    }
  });

  const qSpan = document.getElementById('dashEmptyQuery');
  if (qSpan) qSpan.textContent = q;
  const emptyEl = document.getElementById('dashEmptySearch');
  if (emptyEl) {
    emptyEl.classList.toggle('hidden', matchCount > 0);
  }
}

function filterDashboardCategory(cat, btn) {
  currentDashCategory = cat;
  document.querySelectorAll('.dash-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const searchInput = document.getElementById('dashboardSearchInput');
  filterDashboardTools(searchInput ? searchInput.value : '');
}
