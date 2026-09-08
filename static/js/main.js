/* ==========================================================================
   Crop Recommendation System - Core Frontend Application Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initSyncInputs();
  initPresets();
  initPredictorForm();
  initCatalogSearch();
});

/* --------------------------------------------------------------------------
   1. Dark / Light Theme Toggle
   -------------------------------------------------------------------------- */
function initThemeToggle() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  if (!toggleBtn) return;

  const savedTheme = localStorage.getItem('crop_theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(toggleBtn, savedTheme);

  toggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('crop_theme', newTheme);
    updateThemeIcon(toggleBtn, newTheme);

    // Re-render chart with new theme text colors if chart exists
    if (window.currentCropChart) {
      updateChartColors(newTheme);
    }
  });
}

function updateThemeIcon(btn, theme) {
  btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
}

/* --------------------------------------------------------------------------
   2. Sync Range Sliders and Numeric Input Fields
   -------------------------------------------------------------------------- */
function initSyncInputs() {
  const fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];

  fields.forEach(field => {
    const numInput = document.getElementById(`input_${field}`);
    const sliderInput = document.getElementById(`slider_${field}`);

    if (numInput && sliderInput) {
      // Slider updates number
      sliderInput.addEventListener('input', (e) => {
        numInput.value = e.target.value;
      });

      // Number updates slider
      numInput.addEventListener('input', (e) => {
        if (e.target.value !== '') {
          sliderInput.value = e.target.value;
        }
      });
    }
  });
}

/* --------------------------------------------------------------------------
   3. Soil & Climate Presets Loader
   -------------------------------------------------------------------------- */
const PRESETS_DATA = {
  paddy: { N: 90, P: 42, K: 43, temperature: 23.6, humidity: 82, ph: 6.5, rainfall: 236 },
  cotton: { N: 118, P: 46, K: 19, temperature: 24.0, humidity: 80, ph: 6.9, rainfall: 80 },
  arid: { N: 20, P: 25, K: 50, temperature: 31.0, humidity: 50, ph: 7.2, rainfall: 45 },
  highland: { N: 20, P: 135, K: 200, temperature: 22.0, humidity: 92, ph: 6.0, rainfall: 110 },
  coastal: { N: 22, P: 17, K: 31, temperature: 27.5, humidity: 95, ph: 6.0, rainfall: 175 }
};

function initPresets() {
  const presetBtns = document.querySelectorAll('.preset-btn');
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const presetKey = btn.dataset.preset;
      const data = PRESETS_DATA[presetKey];
      if (data) {
        fillFormValues(data);
        showToast(`Loaded ${btn.innerText.trim()} profile!`);
      }
    });
  });
}

function fillFormValues(data) {
  Object.keys(data).forEach(key => {
    const numInput = document.getElementById(`input_${key}`);
    const sliderInput = document.getElementById(`slider_${key}`);
    if (numInput && sliderInput) {
      numInput.value = data[key];
      sliderInput.value = data[key];
    }
  });
}

/* --------------------------------------------------------------------------
   4. AJAX Predictor Form Submission & Dynamic Radar Chart
   -------------------------------------------------------------------------- */
let radarChartInstance = null;

function initPredictorForm() {
  const form = document.getElementById('cropForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>⏳ Analyzing Conditions...</span>';

    const formData = new FormData(form);
    const payload = {};
    formData.forEach((val, key) => payload[key] = parseFloat(val));

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;

      if (data.status === 'success') {
        renderPredictionResults(data, payload);
      } else {
        alert('Prediction error: ' + (data.message || 'Unable to predict crop.'));
      }
    } catch (err) {
      console.error(err);
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
      alert('Network error connecting to server.');
    }
  });
}

function renderPredictionResults(res, userInput) {
  const resultsContainer = document.getElementById('resultsContainer');
  if (!resultsContainer) return;

  const topCrop = res.top_crop;
  const probabilities = res.probabilities || [];
  const cropStats = res.crop_stats || {};

  let probsHtml = '';
  probabilities.slice(0, 3).forEach((item, idx) => {
    const isTop = idx === 0;
    probsHtml += `
      <div class="prob-item">
        <span class="prob-name">${item.crop} ${isTop ? '⭐' : ''}</span>
        <div class="prob-bar-track">
          <div class="prob-bar-fill" style="width: ${item.probability}%;"></div>
        </div>
        <span class="prob-val">${item.probability}%</span>
      </div>
    `;
  });

  resultsContainer.innerHTML = `
    <div class="recommendation-card">
      <span class="rec-header-tag">🌾 AI Optimal Recommendation</span>
      <h2 class="crop-title">${topCrop}</h2>
      <div class="crop-confidence">Match Confidence: ${res.confidence}%</div>
    </div>

    <div class="prob-section">
      <div class="prob-title">Top Recommended Alternatives</div>
      ${probsHtml}
    </div>

    <div class="chart-card">
      <div class="chart-title">
        <span>📊 Field Condition vs Optimal ${topCrop} Profile</span>
      </div>
      <div class="chart-container">
        <canvas id="cropRadarChart"></canvas>
      </div>
    </div>

    <div style="margin-top: 1.5rem; background: var(--bg-secondary); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
      <h4 style="margin-bottom: 0.5rem; color: var(--text-main);">💡 Agricultural Tips for ${topCrop}:</h4>
      <p style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.5;">
        ${getAgriculturalTip(topCrop)}
      </p>
    </div>
  `;

  // Render Radar Chart using Chart.js
  renderRadarChart(userInput, cropStats, topCrop);
}

function renderRadarChart(userInput, cropStats, cropName) {
  const ctx = document.getElementById('cropRadarChart');
  if (!ctx) return;

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  // Normalize user input and ideal input relative to max scales for readable radar overlay
  const maxScales = {
    N: 140, P: 145, K: 205, temperature: 45, humidity: 100, ph: 10, rainfall: 300
  };

  const labels = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temp (°C)', 'Humidity (%)', 'Soil pH', 'Rainfall (mm)'];
  const keys = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];

  const userDataNormalized = keys.map(k => Math.min(100, Math.round((userInput[k] / maxScales[k]) * 100)));
  const cropDataNormalized = keys.map(k => {
    const meanVal = cropStats[k] ? cropStats[k].mean : userInput[k];
    return Math.min(100, Math.round((meanVal / maxScales[k]) * 100));
  });

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#eefbf5' : '#0f291e';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Your Soil & Weather Input',
          data: userDataNormalized,
          backgroundColor: 'rgba(59, 130, 246, 0.25)',
          borderColor: '#3b82f6',
          pointBackgroundColor: '#3b82f6',
          borderWidth: 2
        },
        {
          label: `Optimal ${cropName} Standard`,
          data: cropDataNormalized,
          backgroundColor: 'rgba(16, 185, 129, 0.25)',
          borderColor: '#10b981',
          pointBackgroundColor: '#10b981',
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: gridColor },
          grid: { color: gridColor },
          pointLabels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 11, weight: 'bold' } },
          ticks: { display: false, max: 100 }
        }
      },
      plugins: {
        legend: {
          labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: '600' } }
        }
      }
    }
  });

  window.currentCropChart = radarChartInstance;
}

function updateChartColors(theme) {
  if (!radarChartInstance) return;
  const isDark = theme === 'dark';
  const textColor = isDark ? '#eefbf5' : '#0f291e';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';

  radarChartInstance.options.scales.r.angleLines.color = gridColor;
  radarChartInstance.options.scales.r.grid.color = gridColor;
  radarChartInstance.options.scales.r.pointLabels.color = textColor;
  radarChartInstance.options.plugins.legend.labels.color = textColor;
  radarChartInstance.update();
}

function getAgriculturalTip(crop) {
  const tips = {
    rice: "Rice thrives in clayey loam soil with high water-retention capacity and high humidity during vegetative growth.",
    maize: "Maize prefers well-drained fertile loam soil with balanced Nitrogen levels and moderate rainfall.",
    chickpea: "Chickpeas require dry climate, cool weather during growth, and well-drained soil with low humidity.",
    cotton: "Cotton needs high sunshine, warm temperature, moderate rainfall, and deep black alluvial soil.",
    apple: "Apples flourish in well-drained loamy soil with high Potassium levels and cooler highland temperatures.",
    banana: "Bananas demand rich organic soil, warm humid weather, and heavy Nitrogen fertilization.",
    coffee: "Coffee grows best in shaded, well-drained acidic soil at cooler high-altitude regions."
  };
  return tips[crop.toLowerCase()] || `${crop} is highly suitable for your provided soil nutrient profile and climate parameters. Ensure adequate irrigation and organic fertilizer management.`;
}

/* --------------------------------------------------------------------------
   5. Catalog Live Search & Auto Load
   -------------------------------------------------------------------------- */
function initCatalogSearch() {
  const searchInput = document.getElementById('catalogSearch');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const cards = document.querySelectorAll('.crop-card');

    cards.forEach(card => {
      const name = card.dataset.cropName.toLowerCase();
      if (name.includes(query)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

function loadCropPreset(dataJsonStr) {
  try {
    const data = JSON.parse(dataJsonStr);
    localStorage.setItem('pending_preset', JSON.stringify(data));
    window.location.href = '/';
  } catch(e) {
    console.error(e);
  }
}

// Auto check for pending preset on home load
if (window.location.pathname === '/') {
  const pending = localStorage.getItem('pending_preset');
  if (pending) {
    localStorage.removeItem('pending_preset');
    setTimeout(() => {
      fillFormValues(JSON.parse(pending));
      showToast('Loaded custom crop profile values!');
    }, 200);
  }
}

/* --------------------------------------------------------------------------
   6. Helper Toast Banner
   -------------------------------------------------------------------------- */
function showToast(message) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>🌱 ${message}</span>`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
