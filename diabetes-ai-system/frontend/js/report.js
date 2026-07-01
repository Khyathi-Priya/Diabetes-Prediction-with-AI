const Report = {
  init() {
    const raw = sessionStorage.getItem("last_prediction");
    if (!raw) {
      Router.go("dashboard");
      return;
    }
    const result = JSON.parse(raw);

    document.getElementById("report-label").textContent = result.prediction_label;
    document.getElementById("report-label").style.color =
      result.prediction_label === "Diabetic" ? "var(--red)" : "var(--green)";

    const badge = document.getElementById("report-badge");
    badge.textContent = `${result.risk_level} Risk`;
    badge.className = `risk-badge ${result.risk_level}`;

    Charts.gaugeChart("risk-gauge", result.probability);
    Charts.pieChart("pie-chart", result.probability);
    Charts.radarChart("radar-chart", result.radar);

    const recsGrid = document.getElementById("recs-grid");
    recsGrid.innerHTML = result.recommendations.map(rec => `
      <div class="rec-card"><span class="rec-icon">✓</span><span>${escapeHtml(rec)}</span></div>
    `).join("");

    document.getElementById("download-report-btn").onclick = () => {
      this.downloadPdf(result.prediction_id);
    };
  },

  downloadPdf(predictionId) {
    const url = Api.reportPdfUrl(predictionId);
    fetch(url, { headers: { Authorization: `Bearer ${Api.token()}` } })
      .then(res => {
        if (!res.ok) throw new Error("Could not generate the report. Please try again.");
        return res.blob();
      })
      .then(blob => {
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = `diabetes_report_${predictionId}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        showToast("Report downloaded.", "success");
      })
      .catch(err => showToast(err.message, "error"));
  },
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
