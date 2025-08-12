const uploader = document.getElementById('uploader');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const statusBox = document.getElementById('upload-status');
const gallery = document.getElementById('gallery');

function setStatus(msg) {
  statusBox.textContent = msg || '';
}

async function fetchImages() {
  const res = await fetch('/api/images');
  const data = await res.json();
  renderGallery(data.items || []);
}

function fileListFromItems(items) {
  const files = [];
  for (const item of items) {
    const file = item.getAsFile && item.getAsFile();
    if (file) files.push(file);
  }
  return files;
}

async function uploadFiles(files) {
  if (!files || files.length === 0) return;
  setStatus(`Загрузка ${files.length} файл(ов)...`);
  const form = new FormData();
  for (const f of files) form.append('files', f);
  const res = await fetch('/api/upload', { method: 'POST', body: form });
  if (!res.ok) {
    const text = await res.text();
    setStatus(`Ошибка: ${text}`);
    return;
  }
  const data = await res.json();
  setStatus('Готово');
  prependToGallery(data.items || []);
}

function renderGallery(items) {
  gallery.innerHTML = '';
  for (const it of items) gallery.appendChild(card(it));
}

function prependToGallery(items) {
  for (const it of items.reverse()) {
    gallery.prepend(card(it));
  }
}

function card(item) {
  const el = document.createElement('div');
  el.className = 'card';
  el.innerHTML = `
    <a href="${item.urls.orig}" target="_blank" rel="noopener">
      <img loading="lazy" src="${item.urls.md}" alt="${item.original_filename}" />
    </a>
    <div class="meta">
      <div class="links">
        <a class="link" href="${item.urls.sm}" target="_blank">sm</a>
        <a class="link" href="${item.urls.md}" target="_blank">md</a>
        <a class="link" href="${item.urls.lg}" target="_blank">lg</a>
      </div>
      <span class="delete" title="Удалить" data-uuid="${item.uuid}">Удалить</span>
    </div>
  `;
  const del = el.querySelector('.delete');
  del.addEventListener('click', async () => {
    if (!confirm('Удалить изображение?')) return;
    const res = await fetch(`/api/images/${item.uuid}`, { method: 'DELETE' });
    if (res.ok) el.remove();
  });
  return el;
}

uploader.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploader.classList.add('dragover');
});

uploader.addEventListener('dragleave', () => uploader.classList.remove('dragover'));

uploader.addEventListener('drop', (e) => {
  e.preventDefault();
  uploader.classList.remove('dragover');
  const files = e.dataTransfer.files?.length ? e.dataTransfer.files : fileListFromItems(e.dataTransfer.items || []);
  uploadFiles(files);
});

uploadBtn.addEventListener('click', () => uploadFiles(fileInput.files));

fetchImages().catch(console.error);