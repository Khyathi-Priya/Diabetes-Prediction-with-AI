const Auth = {
  saveSession(data) {
    localStorage.setItem("diabetes_ai_token", data.access_token);
    localStorage.setItem("diabetes_ai_user", JSON.stringify(data.user));
  },

  currentUser() {
    const raw = localStorage.getItem("diabetes_ai_user");
    return raw ? JSON.parse(raw) : null;
  },

  logout(silent = false) {
    localStorage.removeItem("diabetes_ai_token");
    localStorage.removeItem("diabetes_ai_user");
    sessionStorage.removeItem("last_prediction");
    if (!silent) showToast("You have been signed out.", "success");
    App.updateNav();
    Router.go("landing");
  },

  bindSignup() {
    const form = document.getElementById("signup-form");
    const errorEl = document.getElementById("signup-error");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorEl.textContent = "";
      const username = document.getElementById("su-username").value.trim();
      const email = document.getElementById("su-email").value.trim();
      const password = document.getElementById("su-password").value;

      const btn = form.querySelector("button[type=submit]");
      setBtnLoading(btn, true);
      try {
        const data = await Api.signup({ username, email, password });
        Auth.saveSession(data);
        showToast(`Welcome, ${data.user.username}! Account created.`, "success");
        App.updateNav();
        Router.go("dashboard");
      } catch (err) {
        errorEl.textContent = err.message;
      } finally {
        setBtnLoading(btn, false);
      }
    });
  },

  bindSignin() {
    const form = document.getElementById("signin-form");
    const errorEl = document.getElementById("signin-error");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorEl.textContent = "";
      const email = document.getElementById("si-email").value.trim();
      const password = document.getElementById("si-password").value;

      const btn = form.querySelector("button[type=submit]");
      setBtnLoading(btn, true);
      try {
        const data = await Api.signin({ email, password });
        Auth.saveSession(data);
        showToast(`Welcome back, ${data.user.username}!`, "success");
        App.updateNav();
        Router.go("dashboard");
      } catch (err) {
        errorEl.textContent = err.message;
      } finally {
        setBtnLoading(btn, false);
      }
    });
  },
};

function setBtnLoading(btn, loading) {
  const label = btn.querySelector(".btn-label");
  const spinner = btn.querySelector(".btn-spinner");
  btn.disabled = loading;
  if (label) label.style.opacity = loading ? "0" : "1";
  if (spinner) spinner.classList.toggle("hidden", !loading);
}
