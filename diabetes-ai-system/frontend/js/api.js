const Api = {
  token() {
    return localStorage.getItem("diabetes_ai_token");
  },

  async request(path, { method = "GET", body = null, auth = true } = {}) {
    const headers = { "Content-Type": "application/json" };
    if (auth && this.token()) {
      headers["Authorization"] = `Bearer ${this.token()}`;
    }
    let res;
    try {
      res = await fetch(`${CONFIG.API_BASE}${path}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
      });
    } catch (err) {
      throw new Error("Cannot reach the server. Please make sure the backend is running.");
    }

    if (res.status === 401) {
      Auth.logout(true);
      throw new Error("Your session expired. Please sign in again.");
    }

    if (!res.ok) {
      let detail = "Something went wrong. Please try again.";
      try {
        const data = await res.json();
        detail = data.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    if (res.status === 204) return null;
    return res.json();
  },

  signup(payload) {
    return this.request("/api/auth/signup", { method: "POST", body: payload, auth: false });
  },
  signin(payload) {
    return this.request("/api/auth/signin", { method: "POST", body: payload, auth: false });
  },
  me() {
    return this.request("/api/auth/me");
  },
  predict(payload) {
    return this.request("/api/predict", { method: "POST", body: payload });
  },
  stats() {
    return this.request("/api/stats");
  },
  platformStats() {
    return this.request("/api/stats/platform", { auth: false });
  },
  history(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/api/history${qs ? "?" + qs : ""}`);
  },
  deleteHistoryItem(id) {
    return this.request(`/api/history/${id}`, { method: "DELETE" });
  },
  reportPdfUrl(id) {
    return `${CONFIG.API_BASE}/api/report/${id}/pdf`;
  },
  createReminder(payload) {
    return this.request("/api/reminders", { method: "POST", body: payload });
  },
  listReminders() {
    return this.request("/api/reminders");
  },
  deleteReminder(id) {
    return this.request(`/api/reminders/${id}`, { method: "DELETE" });
  },
};

function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3800);
}
