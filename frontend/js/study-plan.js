/** Study Plan display module */
window.studyPlan = {
  async load(studentId) {
    const container = document.getElementById('plan-content');
    if (!container) return;
    try {
      const plan = await api.getPlan(studentId);
      this.render(container, plan);
    } catch (e) {
      container.innerHTML = `<div class="empty-state"><div class="icon">📋</div><p>${e.message}</p><button class="btn btn-primary" onclick="studyPlan.generate(${studentId})" style="margin-top:1rem">Generate Study Plan</button></div>`;
    }
  },

  async generate(studentId) {
    try {
      utils.toast('Generating plan...', 'info');
      const plan = await api.generatePlan(studentId, 4);
      const container = document.getElementById('plan-content');
      this.render(container, plan);
      utils.toast('Plan generated!', 'success');
    } catch (e) { utils.toast(e.message, 'error'); }
  },

  render(container, plan) {
    const p = plan.plan || plan;
    const weekly = p.weekly_schedule || [];
    const tasks = p.daily_tasks || [];
    const recs = plan.recommendations || [];

    container.innerHTML = `
      <div style="display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap">
        <button class="btn btn-primary" onclick="studyPlan.generate(${plan.student_id || app.currentStudentId})">🔄 Regenerate Plan</button>
        <button class="btn btn-secondary" onclick="studyPlan.adapt(${plan.student_id || app.currentStudentId})">🧠 Adaptive Replan</button>
      </div>

      <div class="card" style="margin-bottom:1.5rem">
        <h3 class="card-title">📅 Weekly Schedule</h3>
        <div class="plan-week" style="margin-top:1rem">
          ${weekly.map(day => `
            <div class="plan-day">
              <div class="plan-day-header">${day.day} ${day.is_revision_day ? '📖' : ''}</div>
              ${(day.sessions||[]).map(s => `
                <div class="plan-session">
                  <span class="subject-name">${s.subject}</span>
                  <span>${s.duration_min}m</span>
                </div>
              `).join('')}
              ${day.total_study_min ? `<div style="font-size:.75rem;color:var(--accent-cyan);margin-top:.5rem">${day.total_study_min} min total</div>` : ''}
            </div>
          `).join('')}
        </div>
      </div>

      <div class="card" style="margin-bottom:1.5rem">
        <h3 class="card-title">✅ Today's Tasks</h3>
        <ul class="task-list" id="task-list" style="margin-top:1rem">
          ${tasks.map(t => `
            <li class="task-item" data-id="${t.id}">
              <div class="task-check" onclick="studyPlan.toggleTask(this)"></div>
              <span class="task-text">${t.task}</span>
              <span class="task-subject badge badge-${t.priority}">${t.subject}</span>
              <span style="font-size:.75rem;color:var(--text-muted)">${t.duration_min}m</span>
            </li>
          `).join('')}
        </ul>
      </div>

      ${recs.length ? `
      <div class="card">
        <h3 class="card-title">💡 Recommendations</h3>
        <div style="margin-top:1rem">
          ${recs.map(r => `
            <div class="rec-card">
              <div class="rec-title">${r.title}</div>
              <div class="rec-desc">${r.description}</div>
              <ul class="rec-actions">${(r.action_items||[]).map(a => `<li>${a}</li>`).join('')}</ul>
            </div>
          `).join('')}
        </div>
      </div>` : ''}
    `;
  },

  toggleTask(el) {
    el.classList.toggle('checked');
    el.closest('.task-item').classList.toggle('completed');
    const total = document.querySelectorAll('.task-item').length;
    const done = document.querySelectorAll('.task-item.completed').length;
    if (done === total && total > 0) {
      utils.toast('🎉 All tasks completed! Great work!', 'success');
    }
  },

  async adapt(studentId) {
    try {
      utils.toast('Analyzing progress...', 'info');
      const result = await api.adaptPlan(studentId);
      if (result.adapted) {
        utils.toast(`Plan adapted: ${result.message}`, 'success');
        this.load(studentId);
      } else {
        utils.toast(result.message, 'info');
      }
    } catch (e) { utils.toast(e.message, 'error'); }
  }
};
