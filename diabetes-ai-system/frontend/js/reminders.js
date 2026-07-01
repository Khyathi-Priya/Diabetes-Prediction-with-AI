const RemindersPage = {
  async init() {
    const form = document.getElementById("reminder-form");
    const errorEl = document.getElementById("reminder-error");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorEl.textContent = "";
      const title = document.getElementById("rem-title").value.trim();
      const remindAt = document.getElementById("rem-time").value;
      const message = document.getElementById("rem-message").value.trim();

      if (!title || !remindAt) {
        errorEl.textContent = "Please fill in the title and date/time.";
        return;
      }

      try {
        await Api.createReminder({
          title,
          message: message || null,
          remind_at: new Date(remindAt).toISOString(),
        });
        showToast("Reminder scheduled.", "success");
        form.reset();
        await this.load();
      } catch (err) {
        errorEl.textContent = err.message;
      }
    });

    await this.load();
  },

  async load() {
    try {
      const reminders = await Api.listReminders();
      const list = document.getElementById("reminders-list");
      const empty = document.getElementById("reminders-empty");

      if (!reminders.length) {
        list.innerHTML = "";
        empty.classList.remove("hidden");
        return;
      }
      empty.classList.add("hidden");

      list.innerHTML = reminders.map(r => `
        <div class="reminder-item">
          <div class="reminder-info">
            <strong>${escapeHtml(r.title)}</strong>
            <span>${new Date(r.remind_at).toLocaleString()}${r.message ? " — " + escapeHtml(r.message) : ""}</span>
          </div>
          <button class="icon-btn danger" onclick="RemindersPage.remove(${r.id})">🗑</button>
        </div>
      `).join("");
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async remove(id) {
    try {
      await Api.deleteReminder(id);
      showToast("Reminder removed.", "success");
      await this.load();
    } catch (err) {
      showToast(err.message, "error");
    }
  },
};
