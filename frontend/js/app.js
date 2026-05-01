/**
 * EduPilot AI — Main Application Controller
 * SPA routing, student context, voice interaction, theme toggle
 */
window.app = {
  currentStudentId: null,

  async init() {
    this.setupNav();
    this.setupThemeToggle();
    this.setupVoice();
    await this.loadStudentList();
    this.navigate('dashboard');
    // Mobile sidebar toggle
    document.getElementById('mobile-toggle')?.addEventListener('click', () => {
      document.querySelector('.sidebar').classList.toggle('open');
    });
  },

  setupNav() {
    document.querySelectorAll('.nav-item').forEach(el => {
      el.addEventListener('click', () => {
        const section = el.dataset.section;
        if (section) this.navigate(section);
        // Close mobile sidebar
        document.querySelector('.sidebar')?.classList.remove('open');
      });
    });
  },

  navigate(section) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-section="${section}"]`)?.classList.add('active');
    // Show section
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(`section-${section}`);
    if (el) el.classList.add('active');
    // Load section data
    this.loadSection(section);
  },

  async loadSection(section) {
    const id = this.currentStudentId;
    switch (section) {
      case 'dashboard':
        if (id) dashboard.load(id); else dashboard.renderEmpty();
        break;
      case 'profile':
        studentForm.render(document.getElementById('profile-content'));
        break;
      case 'plans':
        if (id) studyPlan.load(id);
        else document.getElementById('plan-content').innerHTML = '<div class="empty-state"><div class="icon">📋</div><p>Select a profile first</p></div>';
        break;
      case 'progress':
        if (id) progress.load(id);
        break;
      case 'reminders':
        remindersModule.render(document.getElementById('reminders-content'));
        break;
      case 'export':
        exportModule.render(document.getElementById('export-content'));
        break;
    }
  },

  async loadStudentList() {
    try {
      const students = await api.getStudents();
      const sel = document.getElementById('student-select');
      if (!sel) return;
      sel.innerHTML = '<option value="">+ New Student</option>' +
        students.map(s => `<option value="${s.id}" ${s.id === this.currentStudentId ? 'selected' : ''}>${s.name}</option>`).join('');
      sel.onchange = (e) => {
        this.currentStudentId = e.target.value ? parseInt(e.target.value) : null;
        this.loadSection(this.getCurrentSection());
      };
      // Auto-select first student if none selected and list not empty
      if (!this.currentStudentId && students.length > 0) {
        this.currentStudentId = students[0].id;
        sel.value = students[0].id;
      }
      // If current student was set, also update selector
      if (this.currentStudentId) {
        sel.value = this.currentStudentId;
      }
    } catch (e) { console.warn('Load students:', e); }
  },

  getCurrentSection() {
    const active = document.querySelector('.nav-item.active');
    return active?.dataset.section || 'dashboard';
  },

  setupThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    const saved = localStorage.getItem('edupilot-theme') || 'dark';
    if (saved === 'light') document.documentElement.dataset.theme = 'light';
    btn.onclick = () => {
      const isLight = document.documentElement.dataset.theme === 'light';
      document.documentElement.dataset.theme = isLight ? '' : 'light';
      localStorage.setItem('edupilot-theme', isLight ? 'dark' : 'light');
    };
  },

  setupVoice() {
    const btn = document.getElementById('voice-btn');
    if (!btn || !('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      if (btn) btn.style.display = 'none';
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    btn.onclick = () => {
      btn.classList.add('listening');
      recognition.start();
      utils.toast('🎤 Listening...', 'info');
    };

    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript.toLowerCase();
      btn.classList.remove('listening');
      this.handleVoiceCommand(text);
    };

    recognition.onerror = () => btn.classList.remove('listening');
    recognition.onend = () => btn.classList.remove('listening');
  },

  handleVoiceCommand(text) {
    utils.toast(`Heard: "${text}"`, 'info');
    if (text.includes('study today') || text.includes('what should i study')) {
      this.navigate('plans');
    } else if (text.includes('improving') || text.includes('progress')) {
      this.navigate('progress');
    } else if (text.includes('predict') || text.includes('score')) {
      this.navigate('profile');
      setTimeout(() => studentForm.runPrediction(), 500);
    } else if (text.includes('dashboard')) {
      this.navigate('dashboard');
    } else {
      utils.toast('Try: "What should I study today?" or "Am I improving?"', 'info');
    }
  },

  logout() {
    localStorage.removeItem('edupilot-token');
    localStorage.removeItem('edupilot-user');
    window.location.href = '/';
  }
};

// Boot
document.addEventListener('DOMContentLoaded', () => app.init());
