/** Progress tracking module */
window.progress = {
  async load(studentId) {
    const container = document.getElementById('progress-content');
    if (!container) return;
    try {
      const [progData, streakData] = await Promise.all([
        api.getProgress(studentId, 30),
        api.getStreak(studentId),
      ]);
      this.render(container, progData, streakData, studentId);
    } catch (e) {
      container.innerHTML = `<div class="empty-state"><div class="icon">📈</div><p>No progress data yet. Start logging!</p></div>`;
      this.renderLogForm(container, studentId);
    }
  },

  render(container, progData, streakData, studentId) {
    const logs = progData.logs || [];
    container.innerHTML = `
      <div class="card" style="margin-bottom:1.5rem">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
          <div>
            <div class="streak-display"><span class="streak-fire">🔥</span>${streakData.streak}-day streak</div>
            <div style="color:var(--text-muted);font-size:.85rem;margin-top:.25rem">${logs.length} study sessions logged</div>
          </div>
          <button class="btn btn-primary" onclick="progress.showLogForm(${studentId})">📝 Log Progress</button>
        </div>
      </div>
      <div id="log-form-area"></div>
      <div class="card">
        <h3 class="card-title">📜 Study History</h3>
        <div style="margin-top:1rem">
          ${logs.length === 0 ? '<p class="empty-state">No logs yet. Start studying!</p>' :
            logs.map(l => `
              <div class="task-item">
                <div style="flex:1">
                  <div style="font-weight:600;font-size:.9rem">${l.subject} — ${l.hours_studied}h</div>
                  <div style="font-size:.8rem;color:var(--text-muted)">${l.date} ${l.topics_covered ? '• ' + l.topics_covered : ''}</div>
                </div>
                <div style="display:flex;gap:2px">${'⭐'.repeat(l.self_rating)}</div>
              </div>
            `).join('')}
        </div>
      </div>`;
  },

  showLogForm(studentId) {
    const area = document.getElementById('log-form-area');
    if (!area) return;
    area.innerHTML = `
      <div class="card" style="margin-bottom:1.5rem">
        <h3 class="card-title">📝 Log Study Session</h3>
        <form id="log-form" class="form-grid" style="margin-top:1rem">
          <div class="form-group"><label>Subject</label><select name="subject"><option value="math">Math</option><option value="reading">Reading</option><option value="writing">Writing</option><option value="science">Science</option><option value="history">History</option></select></div>
          <div class="form-group"><label>Hours Studied</label><input type="number" name="hours_studied" min="0" max="12" step="0.5" value="1" /></div>
          <div class="form-group"><label>Topics Covered</label><input type="text" name="topics_covered" placeholder="e.g. Algebra, Geometry" /></div>
          <div class="form-group"><label>Tasks Completed</label><input type="number" name="tasks_completed" min="0" value="3" /></div>
          <div class="form-group"><label>Tasks Total</label><input type="number" name="tasks_total" min="0" value="5" /></div>
          <div class="form-group"><label>Self Rating (1-5) <span class="range-val" id="sr-val">3</span></label><input type="range" name="self_rating" min="1" max="5" value="3" oninput="document.getElementById('sr-val').textContent=this.value" /></div>
          <div class="form-group"><label>Notes</label><input type="text" name="notes" placeholder="Optional notes" /></div>
        </form>
        <button class="btn btn-primary" style="margin-top:1rem" onclick="progress.submitLog(${studentId})">✅ Log Progress</button>
      </div>`;
  },

  async submitLog(studentId) {
    try {
      const f = document.getElementById('log-form');
      const fd = new FormData(f);
      const d = {};
      for (const [k,v] of fd.entries()) {
        d[k] = ['subject','topics_covered','notes'].includes(k) ? v : Number(v);
      }
      await api.logProgress(studentId, d);
      utils.toast('Progress logged! 🎉', 'success');
      this.load(studentId);
    } catch (e) { utils.toast(e.message, 'error'); }
  },

  renderLogForm(container, studentId) {
    const area = document.createElement('div');
    area.id = 'log-form-area';
    container.appendChild(area);
    this.showLogForm(studentId);
  }
};
