const HistoryPage = {
  async init() {
    this.searchInput = document.getElementById("hist-search");
    this.filterSelect = document.getElementById("hist-filter");
    this.sortSelect = document.getElementById("hist-sort");

    this.searchInput.addEventListener("input", debounce(() => this.load(), 350));
    this.filterSelect.addEventListener("change", () => this.load());
    this.sortSelect.addEventListener("change", () => this.load());

    await this.load();
  },

  async load() {
    const [sortBy, sortDir] = this.sortSelect.value.split("-");
    const params = {
      sort_by: sortBy,
      sort_dir: sortDir,
    };
    if (this.searchInput.value.trim()) params.search = this.searchInput.value.trim();
    if (this.filterSelect.value) params.risk_level = this.filterSelect.value;

    try {
      const records = await Api.history(params);
      this.render(records);
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  render(records) {
    const tbody = document.getElementById("history-tbody");
    const empty = document.getElementById("history-empty");

    if (!records.length) {
      tbody.innerHTML = "";
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");

    tbody.innerHTML = records.map(r => {
      const label = r.prediction === 1 ? "Diabetic" : "Non-Diabetic";
      const date = new Date(r.created_at).toLocaleString();
      return `
        <tr>
          <td>${date}</td>
          <td>${label}</td>
          <td>${(r.probability * 100).toFixed(1)}%</td>
          <td><span class="risk-pill ${r.risk_level}">${r.risk_level}</span></td>
          <td>
            <div class="row-actions">
              <button class="icon-btn" title="Download PDF" onclick="HistoryPage.download(${r.id})">⬇</button>
              <button class="icon-btn danger" title="Delete" onclick="HistoryPage.remove(${r.id})">🗑</button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  },

  download(id) {
    fetch(Api.reportPdfUrl(id), { headers: { Authorization: `Bearer ${Api.token()}` } })
      .then(res => {
        if (!res.ok) throw new Error("Could not generate the report.");
        return res.blob();
      })
      .then(blob => {
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = `diabetes_report_${id}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
      })
      .catch(err => showToast(err.message, "error"));
  },

  async remove(id) {
    if (!confirm("Delete this prediction record? This cannot be undone.")) return;
    try {
      await Api.deleteHistoryItem(id);
      showToast("Record deleted.", "success");
      await this.load();
    } catch (err) {
      showToast(err.message, "error");
    }
  },
};

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
