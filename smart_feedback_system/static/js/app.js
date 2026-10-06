document.addEventListener('DOMContentLoaded', () => {
  initPresets();
  setupAnalyzer();
  setupBulkUpload();
  loadDashboard(); // Load stats on start
});

// Category Icons Mapping
const CATEGORY_ICONS = {
  'Technical': 'fa-solid fa-server',
  'Infrastructure': 'fa-solid fa-building-circle-exclamation',
  'Faculty': 'fa-solid fa-chalkboard-user',
  'Examination': 'fa-solid fa-file-pen',
  'Course': 'fa-solid fa-book-open',
  'Administration': 'fa-solid fa-briefcase'
};

/* ================= 1. PRESETS ================= */
async function initPresets() {
  try {
    const res = await fetch('/api/sample-presets');
    if (!res.ok) return;
    const data = await res.json();
    const container = document.getElementById('presetChipsContainer');
    if (!container) return;
    container.innerHTML = '';

    data.presets.forEach(p => {
      const chip = document.createElement('div');
      chip.className = 'preset-chip';
      chip.innerHTML = `<span class="badge bg-secondary-subtle text-dark me-1">${p.language}</span> ${p.label}`;
      chip.onclick = () => {
        document.getElementById('feedbackInput').value = p.text;
        analyzeFeedback(p.text);
      };
      container.appendChild(chip);
    });
  } catch (err) {
    console.error("Presets error:", err);
  }
}

/* ================= 2. ANALYZER ================= */
function setupAnalyzer() {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const clearBtn = document.getElementById('clearBtn');
  const input = document.getElementById('feedbackInput');

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', () => {
      const text = input.value.trim();
      if (text) {
        analyzeFeedback(text);
      } else {
        alert("Please enter feedback text to analyze.");
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      input.value = '';
      document.getElementById('resultCard').classList.add('d-none');
      document.getElementById('resultCardPlaceholder').classList.remove('d-none');
    });
  }
}

async function analyzeFeedback(text) {
  const spinner = document.getElementById('analyzeSpinner');
  const analyzeBtn = document.getElementById('analyzeBtn');
  spinner.classList.remove('d-none');
  analyzeBtn.disabled = true;

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    if (!res.ok) throw new Error("Analysis failed");
    const data = await res.json();

    displayAnalysisResult(data);

    // Refresh background dashboard & escalation count
    loadDashboard();
  } catch (err) {
    alert("Error analyzing feedback: " + err.message);
  } finally {
    spinner.classList.add('d-none');
    analyzeBtn.disabled = false;
  }
}

function displayAnalysisResult(data) {
  document.getElementById('resultCardPlaceholder').classList.add('d-none');
  const card = document.getElementById('resultCard');
  card.classList.remove('d-none');

  // Detected Language
  document.getElementById('detectedLanguageBadge').innerText = data.language;

  // Sentiment
  const sentEmoji = document.getElementById('resSentimentEmoji');
  const sentBadge = document.getElementById('resSentimentBadge');
  const confText = document.getElementById('resSentimentConf');

  confText.innerText = `${Math.round(data.confidence * 100)}%`;

  if (data.sentiment === 'Positive') {
    sentEmoji.innerText = '😊';
    sentBadge.innerText = 'Positive';
    sentBadge.className = 'badge bg-success-subtle text-success px-2 py-1';
  } else if (data.sentiment === 'Negative') {
    sentEmoji.innerText = '😡';
    sentBadge.innerText = 'Negative';
    sentBadge.className = 'badge bg-danger-subtle text-danger px-2 py-1';
  } else {
    sentEmoji.innerText = '😐';
    sentBadge.innerText = 'Neutral';
    sentBadge.className = 'badge bg-warning-subtle text-warning px-2 py-1';
  }

  // Category
  const catIcon = document.getElementById('resCategoryIcon');
  catIcon.className = (CATEGORY_ICONS[data.category] || 'fa-solid fa-tag') + ' text-primary fs-4 d-block mb-1';
  document.getElementById('resCategoryText').innerText = data.category;
  document.getElementById('resCategoryConf').innerText = `${Math.round(data.category_confidence * 100)}%`;

  // Priority
  const priBadge = document.getElementById('resPriorityBadge');
  priBadge.innerText = data.priority;
  if (data.priority === 'High') {
    priBadge.className = 'badge bg-danger text-white px-2 py-1';
  } else if (data.priority === 'Medium') {
    priBadge.className = 'badge bg-warning text-dark px-2 py-1';
  } else {
    priBadge.className = 'badge bg-primary text-white px-2 py-1';
  }

  // Departments
  document.getElementById('resDepartmentShort').innerText = data.category;
  document.getElementById('resDepartmentFull').innerText = data.department;

  // Action Banner
  const actionBanner = document.getElementById('actionBanner');
  const actionHeading = document.getElementById('actionHeading');
  const actionDetail = document.getElementById('actionDetail');
  const actionIcon = document.getElementById('actionIcon');

  actionDetail.innerText = data.action;

  if (data.is_escalated) {
    actionBanner.className = 'alert alert-danger mb-3 border-0 d-flex align-items-center gap-3';
    actionHeading.innerText = '⚠️ Escalation Required';
    actionIcon.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-danger"></i>';
  } else if (data.sentiment === 'Positive') {
    actionBanner.className = 'alert alert-success mb-3 border-0 d-flex align-items-center gap-3';
    actionHeading.innerText = '⭐ Commendation Logged';
    actionIcon.innerHTML = '<i class="fa-solid fa-star text-success"></i>';
  } else {
    actionBanner.className = 'alert alert-secondary mb-3 border-0 d-flex align-items-center gap-3';
    actionHeading.innerText = 'ℹ️ Standard Processing';
    actionIcon.innerHTML = '<i class="fa-solid fa-clipboard-check text-secondary"></i>';
  }

  // Explainability Summary & Token Pills
  const explain = data.explanation || {};
  document.getElementById('resExplainSummary').innerText = explain.summary || 'Summary unavailable.';
  
  const tokensList = document.getElementById('resTokensList');
  tokensList.innerHTML = '';

  const negWords = explain.negative_indicators || [];
  const posWords = explain.positive_indicators || [];

  negWords.forEach(w => {
    const span = document.createElement('span');
    span.className = 'badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1';
    span.innerHTML = `<i class="fa-solid fa-circle-down me-1"></i> "${w}"`;
    tokensList.appendChild(span);
  });

  posWords.forEach(w => {
    const span = document.createElement('span');
    span.className = 'badge bg-success-subtle text-success border border-success-subtle px-2 py-1';
    span.innerHTML = `<i class="fa-solid fa-circle-up me-1"></i> "${w}"`;
    tokensList.appendChild(span);
  });

  if (negWords.length === 0 && posWords.length === 0) {
    tokensList.innerHTML = '<span class="text-muted small">No extreme polar keywords detected.</span>';
  }

  // Probabilities Bars
  const probs = data.sentiment_probabilities || {};
  const pPos = Math.round((probs.Positive || 0) * 100);
  const pNeu = Math.round((probs.Neutral || 0) * 100);
  const pNeg = Math.round((probs.Negative || 0) * 100);

  document.getElementById('barPosVal').innerText = `${pPos}%`;
  document.getElementById('barPos').style.width = `${pPos}%`;

  document.getElementById('barNeuVal').innerText = `${pNeu}%`;
  document.getElementById('barNeu').style.width = `${pNeu}%`;

  document.getElementById('barNegVal').innerText = `${pNeg}%`;
  document.getElementById('barNeg').style.width = `${pNeg}%`;
}

/* ================= 3. BULK CSV UPLOAD ================= */
function setupBulkUpload() {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('csvFileInput');
  const sampleBtn = document.getElementById('loadSampleCsvBtn');

  if (dropZone && fileInput) {
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        uploadFile(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        uploadFile(fileInput.files[0]);
      }
    });
  }

  if (sampleBtn) {
    sampleBtn.addEventListener('click', async () => {
      // Simulate sample upload with pre-generated test sample
      const sampleContent = `feedback
"The lab computer was not working and I couldn't complete my assignment."
"Sir, portal open nahi ho raha hai aur kal morning exam registration close ho jayegi."
"Lab lo Wi-Fi connection asalu ravatledu, speed chala slow undi."
"Professor explains all concepts very clearly and cleared all doubts."
"Examination branch declared the mid term results promptly within 5 days."
"Course curriculum is severely outdated and lacks practical coding projects."
"Accounts department charged extra late fine unfairly, please refund."
"Restrooms on 2nd floor are unhygienic and leaking water continuously."
"Auditorium sound system and air conditioning are world class."
"Teacher bohot jaldi slides bhagate hain, doubt poochne par gussa karte hain."
"Classroom lo bench lu virigi poyi unnai, immediate ga replace cheyandi."
"Canteen food is hygienic and prices are very reasonable."`;

      const blob = new Blob([sampleContent], { type: 'text/csv' });
      const file = new File([blob], 'sample_bulk_test.csv', { type: 'text/csv' });
      uploadFile(file);
    });
  }
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const dropZone = document.getElementById('dropZone');
  dropZone.innerHTML = `
    <div class="spinner-border text-primary mb-3" role="status"></div>
    <h5>Processing Batch Feedback...</h5>
    <p class="text-muted small">Extracting features, classifying sentiments & escalating issues...</p>
  `;

  try {
    const res = await fetch('/api/upload-csv', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) throw new Error("CSV processing failed");
    const data = await res.json();

    // Reset dropzone
    dropZone.innerHTML = `
      <i class="fa-solid fa-cloud-arrow-up display-4 text-primary mb-3"></i>
      <h5 class="fw-bold">Drag and drop your feedback CSV file here</h5>
      <p class="text-muted small">or click to browse from your computer</p>
      <input type="file" id="csvFileInput" class="d-none" accept=".csv">
      <button class="btn btn-primary px-4" onclick="document.getElementById('csvFileInput').click()">Select Another CSV</button>
    `;
    setupBulkUpload();

    // Populate summary bar
    document.getElementById('bulkSummaryCard').classList.remove('d-none');
    document.getElementById('bulkTotal').innerText = data.summary.total_processed;
    document.getElementById('bulkPos').innerText = data.summary.positive;
    document.getElementById('bulkNeu').innerText = data.summary.neutral;
    document.getElementById('bulkNeg').innerText = data.summary.negative;
    document.getElementById('bulkEsc').innerText = data.summary.escalated;

    // Populate table preview
    const tableWrapper = document.getElementById('bulkTableWrapper');
    const tableBody = document.getElementById('bulkTableBody');
    tableWrapper.classList.remove('d-none');
    tableBody.innerHTML = '';

    data.results.forEach((r, idx) => {
      const tr = document.createElement('tr');
      const sentClass = r.sentiment === 'Positive' ? 'bg-success-subtle text-success' : (r.sentiment === 'Negative' ? 'bg-danger-subtle text-danger' : 'bg-warning-subtle text-warning');
      const priClass = r.priority === 'High' ? 'bg-danger text-white' : (r.priority === 'Medium' ? 'bg-warning text-dark' : 'bg-primary text-white');

      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td class="text-truncate" style="max-width: 320px;" title="${r.feedback_text}">${r.feedback_text}</td>
        <td><span class="badge bg-light text-dark border">${r.language}</span></td>
        <td><span class="badge ${sentClass}">${r.sentiment}</span></td>
        <td><strong>${r.category}</strong></td>
        <td><span class="badge ${priClass}">${r.priority}</span></td>
        <td class="small">${r.is_escalated ? '<span class="text-danger fw-bold"><i class="fa-solid fa-bell me-1"></i> Escalated</span>' : '<span class="text-muted">Standard</span>'}</td>
      `;
      tableBody.appendChild(tr);
    });

    showToast(`Batch processed ${data.summary.total_processed} feedback entries successfully!`);
    loadDashboard();
  } catch (err) {
    alert("Error uploading CSV: " + err.message);
  }
}

/* ================= 4. ESCALATION DESK ================= */
async function loadEscalations() {
  const statusFilter = document.getElementById('escFilterStatus').value;
  const deptFilter = document.getElementById('escFilterDept').value;
  const tbody = document.getElementById('escalationTableBody');

  try {
    const res = await fetch(`/api/escalations?status=${encodeURIComponent(statusFilter)}&department=${encodeURIComponent(deptFilter)}`);
    if (!res.ok) throw new Error("Failed to load escalations");
    const data = await res.json();

    tbody.innerHTML = '';
    if (data.escalations.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center py-4 text-muted">
            <i class="fa-solid fa-circle-check text-success fs-4 d-block mb-2"></i>
            No escalated tickets matching selected filter. All issues are under control!
          </td>
        </tr>
      `;
      return;
    }

    data.escalations.forEach(t => {
      const tr = document.createElement('tr');
      const priBadge = t.priority === 'High' ? '<span class="badge bg-danger">HIGH</span>' : '<span class="badge bg-warning text-dark">MED</span>';
      
      let statusBadge = '<span class="badge bg-danger-subtle text-danger">Open</span>';
      if (t.status === 'In Progress') {
        statusBadge = '<span class="badge bg-warning-subtle text-warning-emphasis">In Progress</span>';
      } else if (t.status === 'Resolved') {
        statusBadge = '<span class="badge bg-success-subtle text-success">Resolved</span>';
      }

      tr.innerHTML = `
        <td><strong>#${t.id}</strong></td>
        <td>${priBadge}</td>
        <td><i class="${CATEGORY_ICONS[t.category] || 'fa-solid fa-tag'} me-1 text-primary"></i> ${t.category}</td>
        <td>
          <div class="fw-semibold text-dark">${t.feedback_text}</div>
          <div class="small text-muted mt-1"><i class="fa-solid fa-circle-info text-info me-1"></i> ${t.explanation_summary || ''}</div>
        </td>
        <td><span class="badge bg-light text-dark border">${t.department}</span></td>
        <td id="statusCell-${t.id}">${statusBadge}</td>
        <td class="text-end">
          <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-warning" title="Mark In Progress" onclick="updateTicketStatus(${t.id}, 'In Progress')">
              <i class="fa-solid fa-spinner"></i>
            </button>
            <button class="btn btn-outline-success" title="Mark Resolved" onclick="updateTicketStatus(${t.id}, 'Resolved')">
              <i class="fa-solid fa-check"></i>
            </button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Escalations error:", err);
  }
}

async function updateTicketStatus(id, newStatus) {
  try {
    const res = await fetch(`/api/escalations/${id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (!res.ok) throw new Error("Failed to update status");

    showToast(`Ticket #${id} marked as "${newStatus}"!`);
    loadEscalations();
    loadDashboard();
  } catch (err) {
    alert("Error updating status: " + err.message);
  }
}

/* ================= 5. MODEL BENCHMARKS ================= */
async function loadModelMetrics() {
  try {
    const res = await fetch('/api/model-metrics');
    if (!res.ok) return;
    const data = await res.json();

    // Sentiment Task Table
    const sentTbody = document.getElementById('sentimentBenchmarkTableBody');
    if (sentTbody && data.sentiment_task) {
      document.getElementById('bestSentModelBadge').innerText = `Best: ${data.sentiment_task.best_model}`;
      sentTbody.innerHTML = '';
      for (const [modelName, m] of Object.entries(data.sentiment_task.models)) {
        const tr = document.createElement('tr');
        const isBest = modelName === data.sentiment_task.best_model;
        tr.innerHTML = `
          <td><strong>${modelName}</strong> ${isBest ? '<i class="fa-solid fa-award text-warning ms-1"></i>' : ''}</td>
          <td>${(m.accuracy * 100).toFixed(1)}%</td>
          <td><strong>${(m.f1_weighted * 100).toFixed(1)}%</strong></td>
          <td>${(m.precision * 100).toFixed(1)}%</td>
          <td><code>${m.latency_ms_per_sample} ms</code></td>
        `;
        sentTbody.appendChild(tr);
      }
    }

    // Category Task Table
    const catTbody = document.getElementById('categoryBenchmarkTableBody');
    if (catTbody && data.category_task) {
      document.getElementById('bestCatModelBadge').innerText = `Best: ${data.category_task.best_model}`;
      catTbody.innerHTML = '';
      for (const [modelName, m] of Object.entries(data.category_task.models)) {
        const tr = document.createElement('tr');
        const isBest = modelName === data.category_task.best_model;
        tr.innerHTML = `
          <td><strong>${modelName}</strong> ${isBest ? '<i class="fa-solid fa-award text-warning ms-1"></i>' : ''}</td>
          <td>${(m.accuracy * 100).toFixed(1)}%</td>
          <td><strong>${(m.f1_weighted * 100).toFixed(1)}%</strong></td>
          <td>${(m.precision * 100).toFixed(1)}%</td>
          <td><code>${m.latency_ms_per_sample} ms</code></td>
        `;
        catTbody.appendChild(tr);
      }
    }
  } catch (err) {
    console.error("Model metrics error:", err);
  }
}

/* ================= TOAST HELPER ================= */
function showToast(msg) {
  const toastEl = document.getElementById('statusToast');
  document.getElementById('toastMessage').innerText = msg;
  const toast = new bootstrap.Toast(toastEl);
  toast.show();
}
