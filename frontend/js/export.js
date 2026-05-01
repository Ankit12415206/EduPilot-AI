/** Export module — export data as PDF, CSV, or Excel */
window.exportModule = {
  render(container) {
    container.innerHTML = `
      <div class="export-grid">
        <div class="export-card" id="export-pdf">
          <span class="export-icon">📄</span>
          <div class="export-label">Export as PDF</div>
          <div class="export-desc">Full performance report with charts</div>
        </div>
        <div class="export-card" id="export-csv">
          <span class="export-icon">📊</span>
          <div class="export-label">Export as CSV</div>
          <div class="export-desc">Raw data for spreadsheet analysis</div>
        </div>
        <div class="export-card" id="export-excel">
          <span class="export-icon">📗</span>
          <div class="export-label">Export as Excel</div>
          <div class="export-desc">Formatted workbook with multiple sheets</div>
        </div>
        <div class="export-card" id="export-json">
          <span class="export-icon">🔧</span>
          <div class="export-label">Export as JSON</div>
          <div class="export-desc">Machine-readable data format</div>
        </div>
      </div>
      <div class="card" id="export-preview">
        <div class="card-header">
          <h3 class="card-title">Data Preview</h3>
          <span class="card-subtitle" id="preview-info">Select a student profile to preview</span>
        </div>
        <div id="preview-table" style="overflow-x:auto"></div>
      </div>`;

    document.getElementById('export-pdf').onclick = () => this.exportPDF();
    document.getElementById('export-csv').onclick = () => this.exportCSV();
    document.getElementById('export-excel').onclick = () => this.exportExcel();
    document.getElementById('export-json').onclick = () => this.exportJSON();

    this.loadPreview();
  },

  async loadPreview() {
    try {
      const students = await api.getStudents();
      if (students.length === 0) {
        document.getElementById('preview-table').innerHTML = '<div class="empty-state"><p>No profiles to export</p></div>';
        return;
      }
      document.getElementById('preview-info').textContent = `${students.length} profile(s) available`;
      const keys = ['name','math','reading','writing','science','history','attendance_pct','study_hours_per_day','target_score'];
      let html = '<table style="width:100%;border-collapse:collapse;font-size:.78rem"><thead><tr>';
      keys.forEach(k => html += `<th style="text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--border-glass);color:var(--text-muted);font-size:.7rem;text-transform:uppercase">${k.replace(/_/g,' ')}</th>`);
      html += '</tr></thead><tbody>';
      students.forEach(s => {
        html += '<tr>';
        keys.forEach(k => html += `<td style="padding:.45rem .6rem;border-bottom:1px solid var(--border-glass)">${s[k] ?? '—'}</td>`);
        html += '</tr>';
      });
      html += '</tbody></table>';
      document.getElementById('preview-table').innerHTML = html;
    } catch(e) { console.warn(e); }
  },

  async getExportData() {
    const students = await api.getStudents();
    const id = window.app.currentStudentId;
    let overview = null;
    try { overview = id ? await api.getOverview(id) : null; } catch(e) {}
    return { students, overview };
  },

  async exportPDF() {
    utils.toast('Generating PDF report...', 'info');
    try {
      const { students, overview } = await this.getExportData();
      const id = window.app.currentStudentId;
      const student = students.find(s => s.id === id) || students[0];
      if (!student) { utils.toast('No profile data to export', 'error'); return; }

      // Build printable HTML
      const printWin = window.open('', '_blank');
      printWin.document.write(`<!DOCTYPE html><html><head><title>EduPilot AI Report - ${student.name}</title>
        <style>
          body{font-family:'Inter',Arial,sans-serif;padding:2rem;color:#1a2035;max-width:800px;margin:auto}
          h1{font-size:1.5rem;color:#7c6ef0;margin-bottom:.5rem}
          h2{font-size:1.1rem;margin:1.5rem 0 .5rem;color:#5b8def;border-bottom:2px solid #eee;padding-bottom:.3rem}
          .meta{color:#666;font-size:.85rem;margin-bottom:1.5rem}
          table{width:100%;border-collapse:collapse;margin:.75rem 0}
          th,td{text-align:left;padding:.5rem .7rem;border:1px solid #e0e4ea;font-size:.85rem}
          th{background:#f4f5f8;font-weight:600;font-size:.75rem;text-transform:uppercase;color:#5a6478}
          .kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1rem 0}
          .kpi{padding:1rem;border:1px solid #e0e4ea;border-radius:8px;text-align:center}
          .kpi .val{font-size:1.5rem;font-weight:700;color:#7c6ef0}
          .kpi .lbl{font-size:.7rem;color:#999;text-transform:uppercase}
          .footer{margin-top:2rem;text-align:center;color:#999;font-size:.75rem;border-top:1px solid #eee;padding-top:1rem}
          @media print{body{padding:0}}
        </style></head><body>
        <h1>📊 EduPilot AI — Performance Report</h1>
        <p class="meta">Generated: ${new Date().toLocaleDateString('en-US', {weekday:'long',year:'numeric',month:'long',day:'numeric'})} • Profile: ${student.name}</p>
        
        <h2>Profile Summary</h2>
        <table>
          <tr><th>Name</th><td>${student.name}</td><th>Gender</th><td>${student.gender || '—'}</td></tr>
          <tr><th>Attendance</th><td>${student.attendance_pct}%</td><th>Study Hours/Day</th><td>${student.study_hours_per_day}</td></tr>
          <tr><th>Target Score</th><td>${student.target_score}</td><th>Stress Level</th><td>${student.stress_level}/10</td></tr>
        </table>

        <h2>Subject Scores</h2>
        ${overview ? `<div class="kpi-row">
          <div class="kpi"><div class="val">${overview.predicted_score || '—'}</div><div class="lbl">Predicted Score</div></div>
          <div class="kpi"><div class="val">${overview.pass_probability ? Math.round(overview.pass_probability*100)+'%' : '—'}</div><div class="lbl">Pass Probability</div></div>
          <div class="kpi"><div class="val">${overview.study_streak || 0}</div><div class="lbl">Study Streak</div></div>
        </div>` : ''}
        <table>
          <tr><th>Subject</th><th>Score</th><th>Status</th></tr>
          ${['math','reading','writing','science','history'].map(s => 
            `<tr><td>${s.charAt(0).toUpperCase()+s.slice(1)}</td><td>${student[s]}</td><td>${student[s]>=60?'✅ Pass':'⚠️ Needs Work'}</td></tr>`
          ).join('')}
        </table>

        <h2>Behavioral Metrics</h2>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Sleep Hours</td><td>${student.sleep_hours}</td></tr>
          <tr><td>Social Media Hours</td><td>${student.social_media_hours}</td></tr>
          <tr><td>Assignment Completion</td><td>${student.assignment_completion_pct}%</td></tr>
          <tr><td>Extracurricular Hours</td><td>${student.extracurricular_hours}</td></tr>
        </table>

        <div class="footer">EduPilot AI • AI-Powered Academic Performance Predictor • ${new Date().getFullYear()}</div>
      </body></html>`);
      printWin.document.close();
      setTimeout(() => { printWin.print(); }, 500);
      utils.toast('PDF report generated!', 'success');
    } catch(e) { utils.toast(e.message, 'error'); }
  },

  async exportCSV() {
    try {
      const { students } = await this.getExportData();
      if (!students.length) { utils.toast('No data to export', 'error'); return; }
      const keys = Object.keys(students[0]).filter(k => k !== 'created_at' && k !== 'user_id');
      let csv = keys.join(',') + '\n';
      students.forEach(s => {
        csv += keys.map(k => {
          const val = s[k];
          return typeof val === 'string' ? `"${val}"` : val;
        }).join(',') + '\n';
      });
      this.download(csv, 'edupilot_data.csv', 'text/csv');
      utils.toast('CSV exported!', 'success');
    } catch(e) { utils.toast(e.message, 'error'); }
  },

  async exportExcel() {
    // Export as TSV (opens in Excel)
    try {
      const { students } = await this.getExportData();
      if (!students.length) { utils.toast('No data to export', 'error'); return; }
      const keys = Object.keys(students[0]).filter(k => k !== 'created_at' && k !== 'user_id');
      let tsv = keys.join('\t') + '\n';
      students.forEach(s => {
        tsv += keys.map(k => s[k] ?? '').join('\t') + '\n';
      });
      this.download(tsv, 'edupilot_data.xls', 'application/vnd.ms-excel');
      utils.toast('Excel file exported!', 'success');
    } catch(e) { utils.toast(e.message, 'error'); }
  },

  async exportJSON() {
    try {
      const { students, overview } = await this.getExportData();
      const json = JSON.stringify({ students, overview, exported_at: new Date().toISOString() }, null, 2);
      this.download(json, 'edupilot_data.json', 'application/json');
      utils.toast('JSON exported!', 'success');
    } catch(e) { utils.toast(e.message, 'error'); }
  },

  download(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
};
