const App = {
  updateNav() {
    const loggedIn = !!Api.token();
    const user = Auth.currentUser();

    document.getElementById("nav-auth").classList.toggle("hidden", loggedIn);
    document.getElementById("nav-user").classList.toggle("hidden", !loggedIn);
    document.getElementById("nav-dashboard").classList.toggle("hidden", !loggedIn);
    document.getElementById("nav-history").classList.toggle("hidden", !loggedIn);
    document.getElementById("nav-reminders").classList.toggle("hidden", !loggedIn);

    if (loggedIn && user) {
      document.getElementById("nav-username").textContent = user.username;
    }
  },

  async loadPlatformStats() {
    try {
      const stats = await Api.platformStats();
      animateCounter(document.getElementById("ctr-predictions"), stats.predictions_made);
      animateCounter(document.getElementById("ctr-users"), stats.registered_users);
      const accEl = document.getElementById("ctr-accuracy");
      const target = Math.round(stats.accuracy_percentage);
      let frame = 0;
      const totalFrames = 60;
      const tick = () => {
        frame++;
        const val = Math.round((target * frame) / totalFrames);
        accEl.innerHTML = `${val}<span class="pct">%</span>`;
        if (frame < totalFrames) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    } catch (err) {
      // Platform stats are non-critical; fail silently with sensible fallback.
      document.getElementById("ctr-predictions").textContent = "—";
      document.getElementById("ctr-users").textContent = "—";
      document.getElementById("ctr-accuracy").innerHTML = "—";
    }
  },
};

document.addEventListener("DOMContentLoaded", async () => {
  if (window.AOS) {
    AOS.init({ duration: 700, once: true, offset: 60 });
  }
  await ParticlesBg.init();
  App.updateNav();
  Router.init();
});
