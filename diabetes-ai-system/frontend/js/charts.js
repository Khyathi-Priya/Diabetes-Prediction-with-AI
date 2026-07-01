// Chart.js helpers shared across the dashboard/report pages.
const Charts = {
  instances: {},

  destroy(key) {
    if (this.instances[key]) {
      this.instances[key].destroy();
      delete this.instances[key];
    }
  },

  pieChart(canvasId, probability) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const healthy = Math.round((1 - probability) * 1000) / 10;
    const risk = Math.round(probability * 1000) / 10;
    this.instances[canvasId] = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Healthy", "Diabetes Risk"],
        datasets: [{
          data: [healthy, risk],
          backgroundColor: ["#00E5FF", "#FF3B5C"],
          borderColor: "#0A1128",
          borderWidth: 3,
        }],
      },
      options: {
        plugins: {
          legend: { labels: { color: "#8FA3C4", font: { family: "Space Grotesk" } } },
        },
        cutout: "62%",
      },
    });
  },

  radarChart(canvasId, radarData) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const labels = Object.keys(radarData);
    const values = Object.values(radarData);
    this.instances[canvasId] = new Chart(ctx, {
      type: "radar",
      data: {
        labels,
        datasets: [{
          label: "Health Metrics",
          data: values,
          backgroundColor: "rgba(0,229,255,0.18)",
          borderColor: "#00E5FF",
          pointBackgroundColor: "#00E5FF",
        }],
      },
      options: {
        scales: {
          r: {
            angleLines: { color: "rgba(255,255,255,0.08)" },
            grid: { color: "rgba(255,255,255,0.08)" },
            pointLabels: { color: "#8FA3C4", font: { size: 10, family: "Space Grotesk" } },
            ticks: { display: false, backdropColor: "transparent" },
            suggestedMin: 0,
            suggestedMax: 100,
          },
        },
        plugins: { legend: { display: false } },
      },
    });
  },

  gaugeChart(canvasId, probability) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const pct = Math.round(probability * 100);
    const color = pct >= 66 ? "#FF3B5C" : pct >= 33 ? "#FFB020" : "#1FD976";
    this.instances[canvasId] = new Chart(ctx, {
      type: "doughnut",
      data: {
        datasets: [{
          data: [pct, 100 - pct],
          backgroundColor: [color, "rgba(255,255,255,0.06)"],
          borderWidth: 0,
        }],
      },
      options: {
        circumference: 180,
        rotation: 270,
        cutout: "72%",
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
      },
    });
    document.getElementById("gauge-pct").textContent = `${pct}%`;
    document.getElementById("gauge-pct").style.color = color;
  },

  trendChart(canvasId, history) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const sorted = [...history].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    const labels = sorted.map(r => new Date(r.created_at).toLocaleDateString());
    const values = sorted.map(r => Math.round(r.probability * 1000) / 10);
    this.instances[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Risk Probability (%)",
          data: values,
          borderColor: "#00E5FF",
          backgroundColor: "rgba(0,229,255,0.12)",
          tension: 0.35,
          fill: true,
          pointBackgroundColor: "#00E5FF",
        }],
      },
      options: {
        scales: {
          x: { ticks: { color: "#8FA3C4" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#8FA3C4" }, grid: { color: "rgba(255,255,255,0.05)" }, suggestedMin: 0, suggestedMax: 100 },
        },
        plugins: { legend: { labels: { color: "#8FA3C4" } } },
      },
    });
  },
};

function animateCounter(el, target, suffix = "", duration = 1400) {
  if (!el) return;
  const start = 0;
  const startTime = performance.now();
  function tick(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(start + (target - start) * eased);
    el.textContent = value.toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
