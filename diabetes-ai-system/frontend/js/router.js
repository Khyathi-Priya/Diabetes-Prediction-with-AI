const Router = {
  current: null,

  go(page) {
    window.location.hash = page;
  },

  async render(page) {
    const app = document.getElementById("app");
    const tpl = document.getElementById(`tpl-${page}`);
    if (!tpl) {
      this.go("landing");
      return;
    }

    // Page guards
    const protectedPages = ["dashboard", "history", "reminders", "report"];
    if (protectedPages.includes(page) && !Api.token()) {
      showToast("Please sign in to continue.", "error");
      this.go("signin");
      return;
    }
    if (page === "report" && !sessionStorage.getItem("last_prediction")) {
      this.go("dashboard");
      return;
    }

    DnaAnimation.destroy();
    app.innerHTML = "";
    app.appendChild(tpl.content.cloneNode(true));
    this.current = page;

    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });

    // Page-specific init
    if (page === "landing") {
      DnaAnimation.init();
      App.loadPlatformStats();
    } else if (page === "signup") {
      Auth.bindSignup();
    } else if (page === "signin") {
      Auth.bindSignin();
    } else if (page === "dashboard") {
      await Dashboard.init();
    } else if (page === "report") {
      Report.init();
    } else if (page === "history") {
      await HistoryPage.init();
    } else if (page === "reminders") {
      await RemindersPage.init();
    }

    if (window.AOS) {
      AOS.refreshHard();
    }

    App.updateNav();
  },

  init() {
    window.addEventListener("hashchange", () => {
      const page = window.location.hash.replace("#", "") || "landing";
      this.render(page);
    });
    const initial = window.location.hash.replace("#", "") || "landing";
    this.render(initial);
  },
};
