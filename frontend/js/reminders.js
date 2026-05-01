/** Reminders module — set study reminders with browser notifications */
window.remindersModule = {
  reminders: JSON.parse(localStorage.getItem('edupilot-reminders') || '[]'),

  render(container) {
    container.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Add Reminder</h3>
        </div>
        <div class="reminder-form">
          <div class="form-group">
            <label>Title</label>
            <input type="text" id="reminder-title" placeholder="e.g. Study Math Chapter 5" />
          </div>
          <div class="form-group">
            <label>Date & Time</label>
            <input type="datetime-local" id="reminder-time" />
          </div>
          <button class="btn btn-primary" id="btn-add-reminder" style="align-self:flex-end">Add</button>
        </div>
        <div class="card-header">
          <h3 class="card-title">Upcoming Reminders</h3>
          <span class="reminder-badge" id="reminder-count">${this.reminders.length}</span>
        </div>
        <ul class="reminder-list" id="reminder-list"></ul>
        ${this.reminders.length === 0 ? '<div class="empty-state"><div class="icon">🔔</div><p>No reminders set. Add one above!</p></div>' : ''}
      </div>`;

    document.getElementById('btn-add-reminder').onclick = () => this.add();
    // Set default time to 1 hour from now
    const dt = new Date(Date.now() + 3600000);
    document.getElementById('reminder-time').value = dt.toISOString().slice(0,16);

    this.renderList();
    this.requestNotificationPermission();
  },

  renderList() {
    const list = document.getElementById('reminder-list');
    if (!list) return;
    // Sort by time
    this.reminders.sort((a,b) => new Date(a.time) - new Date(b.time));
    list.innerHTML = this.reminders.map((r, i) => {
      const dt = new Date(r.time);
      const isPast = dt < new Date();
      const timeStr = dt.toLocaleString('en-US', { month:'short', day:'numeric', hour:'numeric', minute:'2-digit' });
      return `<li class="reminder-item ${isPast ? 'completed' : ''}">
        <span class="reminder-time">${timeStr}</span>
        <span class="reminder-text">${r.title}</span>
        <button class="reminder-delete" data-idx="${i}" title="Delete">✕</button>
      </li>`;
    }).join('');
    list.querySelectorAll('.reminder-delete').forEach(btn => {
      btn.onclick = () => this.remove(parseInt(btn.dataset.idx));
    });
    const countEl = document.getElementById('reminder-count');
    if (countEl) countEl.textContent = this.reminders.length;
  },

  add() {
    const title = document.getElementById('reminder-title').value.trim();
    const time = document.getElementById('reminder-time').value;
    if (!title) { utils.toast('Enter a reminder title', 'error'); return; }
    if (!time) { utils.toast('Pick a date/time', 'error'); return; }

    const reminder = { id: Date.now(), title, time };
    this.reminders.push(reminder);
    this.save();
    this.renderList();
    this.scheduleNotification(reminder);
    document.getElementById('reminder-title').value = '';
    utils.toast(`Reminder set: "${title}"`, 'success');
  },

  remove(idx) {
    this.reminders.splice(idx, 1);
    this.save();
    this.renderList();
    utils.toast('Reminder deleted', 'info');
  },

  save() {
    localStorage.setItem('edupilot-reminders', JSON.stringify(this.reminders));
  },

  requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  },

  scheduleNotification(reminder) {
    const ms = new Date(reminder.time) - Date.now();
    if (ms > 0 && ms < 86400000 * 7) { // within 7 days
      setTimeout(() => {
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('EduPilot AI Reminder', { body: reminder.title, icon: '📚' });
        }
        utils.toast(`⏰ Reminder: ${reminder.title}`, 'info');
      }, ms);
    }
  },

  // Schedule all on page load
  scheduleAll() {
    this.reminders.forEach(r => this.scheduleNotification(r));
  }
};

// Auto-schedule reminders on load
if (window.remindersModule) window.remindersModule.scheduleAll();
