// Density ramps matching python_cli specifications
const RAMPS = {
  standard: " .:-=+*#%@",
  detailed: " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
  blocks: " ░▒▓█",
  matrix: " 01",
  minimal: " .oO@"
};

// Application State
let currentImage = null;
let currentFontSize = 8;
let lastPlainText = "";

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const widthSlider = document.getElementById('width-slider');
const widthVal = document.getElementById('width-val');
const ratioSlider = document.getElementById('ratio-slider');
const ratioVal = document.getElementById('ratio-val');
const rampSelect = document.getElementById('ramp-select');
const customRampInput = document.getElementById('custom-ramp-input');
const colorModeSelect = document.getElementById('color-mode');
const invertToggle = document.getElementById('invert-toggle');

const asciiOutput = document.getElementById('ascii-output');
const emptyState = document.getElementById('empty-state');
const metaDims = document.getElementById('meta-dims');
const metaChars = document.getElementById('meta-chars');
const zoomInBtn = document.getElementById('zoom-in');
const zoomOutBtn = document.getElementById('zoom-out');
const zoomLevel = document.getElementById('zoom-level');

const btnCopy = document.getElementById('btn-copy');
const btnDownloadTxt = document.getElementById('btn-download-txt');
const btnDownloadPng = document.getElementById('btn-download-png');
const hiddenCanvas = document.getElementById('hidden-canvas');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
  setupUploadEvents();
  setupControlEvents();
  setupActionEvents();

  // Load default earth sample image on first load
  const defaultSampleBtn = document.querySelector('.preset-btn[data-src="assets/earth.jpg"]');
  if (defaultSampleBtn) {
    loadSampleImage(defaultSampleBtn.getAttribute('data-src'));
  }
});

// Setup File Upload & Drag-and-Drop
function setupUploadEvents() {
  dropZone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleImageFile(e.target.files[0]);
    }
  });

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  ['dragleave', 'dragend'].forEach(evt => {
    dropZone.addEventListener(evt, () => dropZone.classList.remove('dragover'));
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageFile(e.dataTransfer.files[0]);
    }
  });

  // Preset buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      loadSampleImage(btn.getAttribute('data-src'));
    });
  });
}

function handleImageFile(file) {
  if (!file.type.startsWith('image/')) {
    alert('Please choose an image file (PNG, JPG, WEBP, etc.)');
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      currentImage = img;
      renderAscii();
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function loadSampleImage(src) {
  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    currentImage = img;
    renderAscii();
  };
  img.onerror = () => {
    console.warn('Could not load preset image:', src);
  };
  img.src = src;
}

// Setup Interactive Controls
function setupControlEvents() {
  widthSlider.addEventListener('input', () => {
    widthVal.textContent = `${widthSlider.value} chars`;
    renderAscii();
  });

  ratioSlider.addEventListener('input', () => {
    ratioVal.textContent = parseFloat(ratioSlider.value).toFixed(2);
    renderAscii();
  });

  rampSelect.addEventListener('change', () => {
    if (rampSelect.value === 'custom') {
      customRampInput.style.display = 'block';
    } else {
      customRampInput.style.display = 'none';
    }
    renderAscii();
  });

  customRampInput.addEventListener('input', renderAscii);

  colorModeSelect.addEventListener('change', () => {
    updateThemeClass();
    renderAscii();
  });

  invertToggle.addEventListener('change', renderAscii);

  // Zoom controls
  zoomInBtn.addEventListener('click', () => {
    currentFontSize = Math.min(24, currentFontSize + 1);
    updateFontSize();
  });

  zoomOutBtn.addEventListener('click', () => {
    currentFontSize = Math.max(3, currentFontSize - 1);
    updateFontSize();
  });
}

function updateFontSize() {
  asciiOutput.style.fontSize = `${currentFontSize}px`;
  zoomLevel.textContent = `${currentFontSize}px`;
}

function updateThemeClass() {
  asciiOutput.className = 'ascii-output';
  const mode = colorModeSelect.value;
  if (mode === 'emerald') asciiOutput.classList.add('theme-emerald');
  else if (mode === 'classic') asciiOutput.classList.add('theme-classic');
  else if (mode === 'grayscale') asciiOutput.classList.add('theme-grayscale');
  else if (mode === 'fullcolor') asciiOutput.classList.add('theme-fullcolor');
}

// Active character ramp
function getActiveRamp() {
  if (rampSelect.value === 'custom') {
    const custom = customRampInput.value;
    return custom.length > 1 ? custom : RAMPS.standard;
  }
  return RAMPS[rampSelect.value] || RAMPS.standard;
}

// Core Image to ASCII algorithm
function renderAscii() {
  if (!currentImage) return;

  const targetWidth = parseInt(widthSlider.value, 10);
  const aspectCorrection = parseFloat(ratioSlider.value);
  const ramp = getActiveRamp();
  const rampLen = ramp.length;
  const isInverted = invertToggle.checked;
  const isFullColor = colorModeSelect.value === 'fullcolor';

  // Aspect ratio calculation (matching Python implementation)
  const origWidth = currentImage.naturalWidth || currentImage.width;
  const origHeight = currentImage.naturalHeight || currentImage.height;
  const aspectRatio = origHeight / origWidth;
  const targetHeight = Math.max(1, Math.round(targetWidth * aspectRatio * aspectCorrection));

  // Draw into offscreen canvas
  hiddenCanvas.width = targetWidth;
  hiddenCanvas.height = targetHeight;
  const ctx = hiddenCanvas.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(currentImage, 0, 0, targetWidth, targetHeight);

  const imgData = ctx.getImageData(0, 0, targetWidth, targetHeight);
  const pixels = imgData.data;

  const plainRows = [];
  let htmlOutput = '';

  for (let y = 0; y < targetHeight; y++) {
    const rowChars = [];
    let rowHtml = '';

    for (let x = 0; x < targetWidth; x++) {
      const idx = (y * targetWidth + x) * 4;
      const r = pixels[idx];
      const g = pixels[idx + 1];
      const b = pixels[idx + 2];
      const a = pixels[idx + 3];

      // ITU-R BT.601 Grayscale luminance
      let lum = (a === 0) ? 0 : (0.299 * r + 0.587 * g + 0.114 * b);

      let charIdx = Math.floor((lum / 255) * (rampLen - 1));
      if (isInverted) {
        charIdx = (rampLen - 1) - charIdx;
      }
      charIdx = Math.max(0, Math.min(rampLen - 1, charIdx));
      const char = ramp[charIdx];
      rowChars.push(char);

      if (isFullColor) {
        const escaped = (char === ' ') ? '&nbsp;' : (char === '<' ? '&lt;' : (char === '>' ? '&gt;' : (char === '&' ? '&amp;' : char)));
        rowHtml += `<span style="color:rgb(${r},${g},${b})">${escaped}</span>`;
      }
    }

    const plainLine = rowChars.join('');
    plainRows.push(plainLine);
    if (!isFullColor) {
      // Escape HTML for plain output
      const escapedLine = plainLine.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      htmlOutput += (y > 0 ? '\n' : '') + escapedLine;
    } else {
      htmlOutput += (y > 0 ? '\n' : '') + rowHtml;
    }
  }

  lastPlainText = plainRows.join('\n');

  // Render to DOM
  if (isFullColor) {
    asciiOutput.innerHTML = htmlOutput;
  } else {
    asciiOutput.textContent = lastPlainText;
  }

  // Update visibility and metadata
  emptyState.style.display = 'none';
  asciiOutput.style.display = 'block';
  metaDims.textContent = `${targetWidth} × ${targetHeight} chars`;
  metaChars.textContent = `${targetWidth * targetHeight} chars`;
}

// Action Buttons: Copy, Download TXT, Export PNG
function setupActionEvents() {
  // Copy to clipboard
  btnCopy.addEventListener('click', async () => {
    if (!lastPlainText) return;
    try {
      await navigator.clipboard.writeText(lastPlainText);
      const span = btnCopy.querySelector('span');
      const originalText = span.textContent;
      span.textContent = 'Copied!';
      btnCopy.style.borderColor = 'var(--accent-green)';
      setTimeout(() => {
        span.textContent = originalText;
        btnCopy.style.borderColor = '';
      }, 1800);
    } catch {
      alert('Unable to copy directly. Please select the output text and press Ctrl+C.');
    }
  });

  // Download .TXT
  btnDownloadTxt.addEventListener('click', () => {
    if (!lastPlainText) return;
    const blob = new Blob([lastPlainText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ascii_art_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Export as PNG
  btnDownloadPng.addEventListener('click', () => {
    if (!lastPlainText) return;

    const lines = lastPlainText.split('\n');
    if (!lines.length) return;

    const charWidth = 7;
    const charHeight = 11;
    const padding = 20;
    const canvasWidth = lines[0].length * charWidth + padding * 2;
    const canvasHeight = lines.length * charHeight + padding * 2;

    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = canvasWidth;
    exportCanvas.height = canvasHeight;
    const expCtx = exportCanvas.getContext('2d');

    // Fill dark background
    expCtx.fillStyle = '#0b0f0e';
    expCtx.fillRect(0, 0, canvasWidth, canvasHeight);

    // Font settings
    expCtx.font = '10px "JetBrains Mono", monospace';
    expCtx.textBaseline = 'top';

    const mode = colorModeSelect.value;
    let defaultColor = '#10b981';
    if (mode === 'classic') defaultColor = '#22c55e';
    else if (mode === 'grayscale') defaultColor = '#e2e8f0';

    expCtx.fillStyle = defaultColor;

    for (let r = 0; r < lines.length; r++) {
      const line = lines[r];
      expCtx.fillText(line, padding, padding + r * charHeight);
    }

    // Export image
    const a = document.createElement('a');
    a.href = exportCanvas.toDataURL('image/png');
    a.download = `ascii_art_${Date.now()}.png`;
    a.click();
  });
}
