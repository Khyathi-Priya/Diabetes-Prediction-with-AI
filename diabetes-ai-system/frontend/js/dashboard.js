const Dashboard = {
  async init() {
    const user = Auth.currentUser();
    document.getElementById("dash-username").textContent = user ? user.username : "User";

    this.bindForm();
    await this.loadStats();
    await this.loadTrend();
  },

  async loadStats() {
    try {
      const stats = await Api.stats();
      document.getElementById("stat-total").textContent = stats.total_predictions;
      document.getElementById("stat-high").textContent = stats.high_risk_count;
      document.getElementById("stat-mod").textContent = stats.moderate_risk_count;
      document.getElementById("stat-low").textContent = stats.low_risk_count;

      const banner = document.getElementById("risk-alert-banner");
      if (stats.high_risk_count > 0) {
        banner.classList.remove("hidden");
        banner.innerHTML = `⚠️ You have <strong>${stats.high_risk_count}</strong> high-risk prediction(s) on record. Consider consulting a healthcare professional.`;
      } else {
        banner.classList.add("hidden");
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadTrend() {
    try {
      const history = await Api.history();
      const trendEmpty = document.getElementById("trend-empty");
      const canvas = document.getElementById("trend-chart");
      if (!history.length) {
        trendEmpty.classList.remove("hidden");
        canvas.classList.add("hidden");
        return;
      }
      trendEmpty.classList.add("hidden");
      canvas.classList.remove("hidden");
      Charts.trendChart("trend-chart", history);
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  bindForm() {
    const form = document.getElementById("predict-form");
    const errorEl = document.getElementById("predict-error");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorEl.textContent = "";

      const payload = {
        pregnancies: parseInt(document.getElementById("f-pregnancies").value, 10),
        glucose: parseFloat(document.getElementById("f-glucose").value),
        bloodpressure: parseFloat(document.getElementById("f-bp").value),
        skinthickness: parseFloat(document.getElementById("f-skin").value),
        insulin: parseFloat(document.getElementById("f-insulin").value),
        bmi: parseFloat(document.getElementById("f-bmi").value),
        dpf: parseFloat(document.getElementById("f-dpf").value),
        age: parseInt(document.getElementById("f-age").value, 10),
      };

      const btn = form.querySelector("button[type=submit]");
      setBtnLoading(btn, true);
      try {
        const result = await Api.predict(payload);
        sessionStorage.setItem("last_prediction", JSON.stringify(result));
        showToast("Analysis complete — opening your report.", "success");
        Router.go("report");
      } catch (err) {
        errorEl.textContent = err.message;
      } finally {
        setBtnLoading(btn, false);
      }
    });
  },
};
