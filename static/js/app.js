// ============================================================
// DocPortal Master Application Client Logic (Modular Bootstrap)
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  // 1. Inisialisasi Dropzones Tunggal
  setupDropzone('dz-html', 'file-html', 'lbl-html');
  setupDropzone('dz-csv', 'file-csv', 'lbl-csv');
  setupDropzone('dz-pdf', 'file-pdf', 'lbl-pdf');
  setupDropzone('dz-word', 'file-word', 'lbl-word');
  setupDropzone('dz-pdfppt', 'file-pdfppt', 'lbl-pdfppt');
  setupDropzone('dz-pdfimg', 'file-pdfimg', 'lbl-pdfimg');
  setupDropzone('dz-splitpdf', 'file-splitpdf', 'lbl-splitpdf');
  setupDropzone('dz-pagemgr', 'file-pagemgr', 'lbl-pagemgr');
  setupDropzone('dz-compresspdf', 'file-compresspdf', 'lbl-compresspdf');
  setupDropzone('dz-imgcmp', 'file-imgcmp', 'lbl-imgcmp');

  // Preview listener untuk kompres gambar
  const inpImgCmp = document.getElementById('file-imgcmp');
  if (inpImgCmp) {
    inpImgCmp.addEventListener('change', () => {
      if (inpImgCmp.files && inpImgCmp.files.length > 0) {
        previewSelectedImageForCompression(inpImgCmp.files[0]);
      }
    });
  }
  const dzImgCmp = document.getElementById('dz-imgcmp');
  if (dzImgCmp) {
    dzImgCmp.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        previewSelectedImageForCompression(e.dataTransfer.files[0]);
      }
    });
  }

  // 2. Inisialisasi Multi-file Dropzones
  setupMultiFileDropzone('dz-imgtopdf', 'file-imgtopdf', addImageToPdfFiles);
  setupMultiFileDropzone('dz-mergepdf', 'file-mergepdf', addMergePdfFiles);

  // 3. Listener Khusus: Kelola Halaman PDF (Canvas Grid)
  const inpPageMgr = document.getElementById('file-pagemgr');
  if (inpPageMgr) {
    inpPageMgr.addEventListener('change', () => {
      if (inpPageMgr.files && inpPageMgr.files.length > 0) {
        loadPageManagerDocument(inpPageMgr.files[0]);
      }
    });
  }

  const dzPageMgr = document.getElementById('dz-pagemgr');
  if (dzPageMgr) {
    dzPageMgr.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        loadPageManagerDocument(e.dataTransfer.files[0]);
      }
    });
  }

  // 4. Listener Khusus: Reset Kartu Kompresi jika Ganti File
  const inpCompress = document.getElementById('file-compresspdf');
  if (inpCompress) {
    inpCompress.addEventListener('change', () => {
      const card = document.getElementById('compressResultCard');
      if (card) card.classList.add('hidden');
      currentCompressedBlob = null;
    });
  }

  // 5. Set Tool Awal Aktif (Dashboard Utama)
  selectTool('dashboard');
});
