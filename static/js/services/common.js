// ============================================================
// Service: Common / Core Utilities & Shared State
// ============================================================

// Configure PDF.js Worker
if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/vendor/pdf.worker.min.js';
}

// Global Shared State
let currentCompressedBlob = null;
let currentCompressedFileName = '';
let currentPmFile = null;
let currentPmPdfDoc = null;
let mergeSortableInstance = null;
let pmSortableInstance = null;
let toastTimer = null;

// Loading Modal Controller
function setStep(num) {
  for (let i = 1; i <= 3; i++) {
    const dot = document.getElementById('step' + i + '-dot');
    const txt = document.getElementById('step' + i + '-txt');
    if (!dot || !txt) continue;
    if (i < num) {
      dot.className = 'step-circle done';
      dot.innerHTML = '✓';
      txt.className = 'text-xs font-semibold text-slate-700';
    } else if (i === num) {
      dot.className = 'step-circle active';
      dot.textContent = i;
      txt.className = 'text-xs font-bold text-indigo-700';
    } else {
      dot.className = 'step-circle waiting';
      dot.textContent = i;
      txt.className = 'text-xs font-medium text-slate-400';
    }
  }
}

function showLoading(steps) {
  if (steps && steps.length >= 3) {
    const t1 = document.getElementById('step1-txt');
    const t2 = document.getElementById('step2-txt');
    const t3 = document.getElementById('step3-txt');
    if (t1) t1.textContent = steps[0];
    if (t2) t2.textContent = steps[1];
    if (t3) t3.textContent = steps[2];
  }
  setStep(1);
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.add('show');
}

function hideLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.remove('show');
}

// Toast Controller
function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toastMsg');
  if (!toast || !msgEl) return;
  msgEl.textContent = msg;
  toast.classList.toggle('error', isError);

  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 4500);
}

// Alert Notification Box
function showAlert(title, msg) {
  const box = document.getElementById('alertBox');
  const tEl = document.getElementById('alertTitle');
  const mEl = document.getElementById('alertMsg');
  if (!box || !tEl || !mEl) return;
  tEl.textContent = title;
  mEl.textContent = msg;
  box.classList.remove('hidden');
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideAlert() {
  const box = document.getElementById('alertBox');
  if (box) box.classList.add('hidden');
}

// Trigger Blob File Download
function triggerBlobDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 300);
}

// Dropzone Initializers
function setupDropzone(dzId, inputId, lblId) {
  const dz = document.getElementById(dzId);
  const inp = document.getElementById(inputId);
  const lbl = document.getElementById(lblId);
  if (!dz || !inp) return;

  dz.addEventListener('click', () => inp.click());
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('active'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('active'));
  dz.addEventListener('drop', e => {
    e.preventDefault();
    dz.classList.remove('active');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      inp.files = e.dataTransfer.files;
      updateFileInfo(inp, lbl);
    }
  });
  inp.addEventListener('change', () => updateFileInfo(inp, lbl));
}

function setupMultiFileDropzone(dzId, inputId, onFilesAdded) {
  const dz = document.getElementById(dzId);
  const inp = document.getElementById(inputId);
  if (!dz || !inp) return;

  dz.addEventListener('click', () => inp.click());
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('active'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('active'));
  dz.addEventListener('drop', e => {
    e.preventDefault();
    dz.classList.remove('active');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFilesAdded(Array.from(e.dataTransfer.files));
    }
  });
  inp.addEventListener('change', () => {
    if (inp.files && inp.files.length > 0) {
      onFilesAdded(Array.from(inp.files));
      inp.value = '';
    }
  });
}

function updateFileInfo(inp, lbl) {
  if (!inp.files || !inp.files.length) return;
  const f = inp.files[0];
  const sizeStr = f.size > 1048576 ? (f.size / 1048576).toFixed(1) + ' MB' : Math.round(f.size / 1024) + ' KB';
  if (lbl) {
    lbl.textContent = `✓ ${f.name} (${sizeStr})`;
    lbl.classList.remove('hidden');
  }
  const badge = document.getElementById('fileInfoBadge');
  const badgeName = document.getElementById('fileInfoName');
  if (badge && badgeName) {
    badgeName.textContent = `${f.name} · ${sizeStr}`;
    badge.classList.remove('hidden');
    badge.classList.add('flex');
  }
  hideAlert();
}
