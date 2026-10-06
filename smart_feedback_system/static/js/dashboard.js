// Global chart instances
let sentimentChartInstance = null;
let categoryChartInstance = null;
let priorityChartInstance = null;
let languageChartInstance = null;

async function loadDashboard() {
  try {
    const res = await fetch('/api/dashboard-stats');
    if (!res.ok) throw new Error("Failed to load dashboard data");
    const data = await res.json();

    // 1. Update KPI numbers
    document.getElementById('kpiTotal').innerText = data.total;
    document.getElementById('kpiPos').innerText = `${data.sentiment_percentages.Positive}%`;
    document.getElementById('kpiPosCount').innerText = `${data.sentiment_counts.Positive} entries`;
    
    document.getElementById('kpiNeu').innerText = `${data.sentiment_percentages.Neutral}%`;
    document.getElementById('kpiNeuCount').innerText = `${data.sentiment_counts.Neutral} entries`;

    document.getElementById('kpiNeg').innerText = `${data.sentiment_percentages.Negative}%`;
    document.getElementById('kpiNegCount').innerText = `${data.sentiment_counts.Negative} entries`;

    document.getElementById('kpiEsc').innerText = data.escalation_summary.total_escalated;
    document.getElementById('kpiOpenEsc').innerText = `${data.escalation_summary.open} Open`;
    document.getElementById('kpiRes').innerText = data.escalation_summary.resolved;

    // Update tab badge
    const badge = document.getElementById('tab-escalation-badge');
    if (badge) {
      badge.innerText = data.escalation_summary.open;
    }

    // 2. Render Sentiment Chart
    renderSentimentChart(data.sentiment_counts);

    // 3. Render Category Chart (Stacked Bar)
    renderCategoryChart(data.category_matrix);

    // 4. Render Priority Chart
    renderPriorityChart(data.priority_counts);

    // 5. Render Language Chart
    renderLanguageChart(data.language_counts);

  } catch (err) {
    console.error("Dashboard load error:", err);
  }
}

function renderSentimentChart(counts) {
  const ctx = document.getElementById('sentimentChart');
  if (!ctx) return;

  if (sentimentChartInstance) {
    sentimentChartInstance.destroy();
  }

  sentimentChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Positive 😊', 'Neutral 😐', 'Negative 😡'],
      datasets: [{
        data: [counts.Positive || 0, counts.Neutral || 0, counts.Negative || 0],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        hoverOffset: 6,
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 12, font: { family: 'Plus Jakarta Sans', size: 11 } }
        }
      },
      cutout: '65%'
    }
  });
}

function renderCategoryChart(matrix) {
  const ctx = document.getElementById('categoryChart');
  if (!ctx) return;

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  const categories = Object.keys(matrix);
  const posData = categories.map(cat => (matrix[cat] && matrix[cat].Positive) || 0);
  const neuData = categories.map(cat => (matrix[cat] && matrix[cat].Neutral) || 0);
  const negData = categories.map(cat => (matrix[cat] && matrix[cat].Negative) || 0);

  categoryChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: categories,
      datasets: [
        {
          label: 'Positive',
          data: posData,
          backgroundColor: '#10b981',
          stack: 'Stack 0'
        },
        {
          label: 'Neutral',
          data: neuData,
          backgroundColor: '#f59e0b',
          stack: 'Stack 0'
        },
        {
          label: 'Negative',
          data: negData,
          backgroundColor: '#ef4444',
          stack: 'Stack 0'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true, grid: { display: false } },
        y: { stacked: true, beginAtZero: true }
      },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12 } }
      }
    }
  });
}

function renderPriorityChart(counts) {
  const ctx = document.getElementById('priorityChart');
  if (!ctx) return;

  if (priorityChartInstance) {
    priorityChartInstance.destroy();
  }

  priorityChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['High', 'Medium', 'Low'],
      datasets: [{
        data: [counts.High || 0, counts.Medium || 0, counts.Low || 0],
        backgroundColor: ['#ef4444', '#f97316', '#3b82f6'],
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12 } }
      }
    }
  });
}

function renderLanguageChart(counts) {
  const ctx = document.getElementById('languageChart');
  if (!ctx) return;

  if (languageChartInstance) {
    languageChartInstance.destroy();
  }

  const labels = Object.keys(counts);
  const data = labels.map(l => counts[l]);

  languageChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Entries',
        data: data,
        backgroundColor: '#6366f1',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
