/** Profile module — customizable fields, universal for any learner */
window.studentForm = {
  // Default field groups — users can toggle these on/off
  fieldGroups: {
    demographics: {
      label: 'Demographics', icon: '👤',
      fields: [
        { name: 'name', type: 'text', label: 'Full Name', required: true },
        { name: 'gender', type: 'select', label: 'Gender', options: ['female','male','other','prefer not to say'] },
        { name: 'ethnicity', type: 'select', label: 'Ethnicity', options: ['group A','group B','group C','group D','group E'] },
        { name: 'parent_education', type: 'select', label: 'Education Background', options: ['some high school','high school','some college',"associate's degree","bachelor's degree","master's degree"] },
      ]
    },
    academic: {
      label: 'Academic Info', icon: '🎓',
      fields: [
        { name: 'lunch', type: 'select', label: 'Meal Plan', options: ['standard','free/reduced'] },
        { name: 'test_prep', type: 'select', label: 'Test Preparation', options: ['none','completed'] },
        { name: 'target_score', type: 'number', label: 'Target Score', min: 0, max: 100, value: 75 },
      ]
    },
    behavioral: {
      label: 'Behavioral', icon: '📊',
      fields: [
        { name: 'attendance_pct', type: 'range', label: 'Attendance %', min: 0, max: 100, value: 75 },
        { name: 'study_hours_per_day', type: 'range', label: 'Study Hours/Day', min: 0, max: 10, step: 0.5, value: 3 },
        { name: 'assignment_completion_pct', type: 'range', label: 'Assignment Completion %', min: 0, max: 100, value: 70 },
        { name: 'sleep_hours', type: 'range', label: 'Sleep Hours', min: 3, max: 12, step: 0.5, value: 7 },
        { name: 'social_media_hours', type: 'range', label: 'Social Media Hours', min: 0, max: 10, step: 0.5, value: 2 },
        { name: 'stress_level', type: 'range', label: 'Stress Level (1-10)', min: 1, max: 10, value: 5 },
        { name: 'extracurricular_hours', type: 'range', label: 'Extracurricular Hrs/Week', min: 0, max: 15, step: 0.5, value: 2 },
      ]
    },
    subjects: {
      label: 'Subject Scores', icon: '📚',
      fields: [
        { name: 'math', type: 'number', label: 'Math', min: 0, max: 100, value: 65 },
        { name: 'reading', type: 'number', label: 'Reading', min: 0, max: 100, value: 65 },
        { name: 'writing', type: 'number', label: 'Writing', min: 0, max: 100, value: 65 },
        { name: 'science', type: 'number', label: 'Science', min: 0, max: 100, value: 65 },
        { name: 'history', type: 'number', label: 'History', min: 0, max: 100, value: 65 },
      ]
    }
  },

  // Custom fields stored in localStorage
  customFields: JSON.parse(localStorage.getItem('edupilot-custom-fields') || '[]'),
  // Hidden default fields
  hiddenFields: JSON.parse(localStorage.getItem('edupilot-hidden-fields') || '[]'),

  render(container) {
    const hasStudent = !!window.app.currentStudentId;

    container.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h3 class="card-title" id="form-title">${hasStudent ? 'Edit Profile' : 'New Profile'}</h3>
          <span class="card-subtitle" id="form-subtitle">${hasStudent ? 'Edit & save to update' : 'Fill in your details below'}</span>
        </div>

        <!-- Field toggles -->
        <div class="field-toggles" id="field-toggles"></div>

        <form id="student-form" class="form-grid"></form>

        <!-- Custom fields section -->
        <div class="custom-fields-header">
          <h4>Custom Fields</h4>
          <button class="add-field-btn" id="btn-add-custom">+ Add Field</button>
        </div>
        <div id="custom-fields-container"></div>

        <div class="form-actions">
          <button class="btn btn-primary" id="btn-save-student">💾 Save Profile</button>
          <button class="btn btn-secondary" id="btn-predict" ${hasStudent ? '' : 'style="display:none"'}>🔮 Run Prediction</button>
          <button class="btn btn-secondary" id="btn-gen-plan" ${hasStudent ? '' : 'style="display:none"'}>📋 Generate Plan</button>
        </div>
        <div id="prediction-result"></div>
      </div>`;

    this.renderFieldToggles();
    this.renderFormFields();
    this.renderCustomFields();

    document.getElementById('btn-save-student').onclick = () => this.save();
    document.getElementById('btn-predict').onclick = () => this.runPrediction();
    document.getElementById('btn-gen-plan').onclick = () => this.genPlan();
    document.getElementById('btn-add-custom').onclick = () => this.addCustomField();

    if (hasStudent) this.loadStudent(window.app.currentStudentId);
  },

  renderFieldToggles() {
    const container = document.getElementById('field-toggles');
    if (!container) return;
    let html = '';
    for (const [groupKey, group] of Object.entries(this.fieldGroups)) {
      for (const field of group.fields) {
        const isHidden = this.hiddenFields.includes(field.name);
        html += `<span class="field-chip ${isHidden ? '' : 'active'}" data-field="${field.name}">
          ${field.label} <span class="chip-x">${isHidden ? '+' : '×'}</span>
        </span>`;
      }
    }
    container.innerHTML = html;
    container.querySelectorAll('.field-chip').forEach(chip => {
      chip.onclick = () => {
        const fname = chip.dataset.field;
        const idx = this.hiddenFields.indexOf(fname);
        if (idx >= 0) this.hiddenFields.splice(idx, 1);
        else this.hiddenFields.push(fname);
        localStorage.setItem('edupilot-hidden-fields', JSON.stringify(this.hiddenFields));
        this.renderFieldToggles();
        this.renderFormFields();
        if (window.app.currentStudentId) this.loadStudent(window.app.currentStudentId);
      };
    });
  },

  renderFormFields() {
    const form = document.getElementById('student-form');
    if (!form) return;
    let html = '';
    for (const [groupKey, group] of Object.entries(this.fieldGroups)) {
      for (const f of group.fields) {
        if (this.hiddenFields.includes(f.name)) continue;
        html += this.renderField(f);
      }
    }
    form.innerHTML = html;
  },

  renderField(f) {
    const id = `fv-${f.name}`;
    if (f.type === 'select') {
      const opts = f.options.map(o => `<option value="${o}">${o.charAt(0).toUpperCase()+o.slice(1)}</option>`).join('');
      return `<div class="form-group"><label>${f.label}</label><select name="${f.name}">${opts}</select></div>`;
    }
    if (f.type === 'range') {
      return `<div class="form-group"><label>${f.label} <span class="range-val" id="${id}">${f.value}</span></label>
        <input type="range" name="${f.name}" min="${f.min}" max="${f.max}" step="${f.step||1}" value="${f.value}"
          oninput="document.getElementById('${id}').textContent=this.value" /></div>`;
    }
    if (f.type === 'number') {
      return `<div class="form-group"><label>${f.label}</label>
        <input type="number" name="${f.name}" min="${f.min||0}" max="${f.max||100}" value="${f.value||''}" ${f.required?'required':''} /></div>`;
    }
    return `<div class="form-group"><label>${f.label}</label>
      <input type="text" name="${f.name}" placeholder="${f.label}" ${f.required?'required':''} /></div>`;
  },

  renderCustomFields() {
    const container = document.getElementById('custom-fields-container');
    if (!container) return;
    container.innerHTML = this.customFields.map((cf, i) => `
      <div class="custom-field-row">
        <input type="text" value="${cf.label}" placeholder="Field name" data-idx="${i}" class="cf-label" style="flex:.4" />
        <input type="number" name="custom_${cf.key}" value="${cf.value||''}" placeholder="Value" min="0" max="100" style="flex:.4" />
        <button class="remove-field-btn" data-idx="${i}" title="Remove">✕</button>
      </div>
    `).join('');
    container.querySelectorAll('.remove-field-btn').forEach(btn => {
      btn.onclick = () => { this.customFields.splice(parseInt(btn.dataset.idx), 1); this.saveCustomFields(); this.renderCustomFields(); };
    });
    container.querySelectorAll('.cf-label').forEach(input => {
      input.onchange = () => {
        const idx = parseInt(input.dataset.idx);
        this.customFields[idx].label = input.value;
        this.customFields[idx].key = input.value.toLowerCase().replace(/\s+/g,'_');
        this.saveCustomFields();
      };
    });
  },

  addCustomField() {
    const n = this.customFields.length + 1;
    this.customFields.push({ key: `custom_field_${n}`, label: `Custom Field ${n}`, value: '' });
    this.saveCustomFields();
    this.renderCustomFields();
  },

  saveCustomFields() {
    localStorage.setItem('edupilot-custom-fields', JSON.stringify(this.customFields));
  },

  getFormData() {
    const f = document.getElementById('student-form');
    const fd = new FormData(f);
    const d = {};
    const textFields = ['name','gender','ethnicity','parent_education','lunch','test_prep'];
    for (const [k,v] of fd.entries()) {
      d[k] = textFields.includes(k) ? v : Number(v);
    }
    return d;
  },

  async save() {
    try {
      const data = this.getFormData();
      if (!data.name) { utils.toast('Enter a name','error'); return; }
      const id = window.app.currentStudentId;
      let student;
      if (id) {
        student = await api.updateStudent(id, data);
        utils.toast(`Profile updated for "${student.name}"`, 'success');
      } else {
        student = await api.createStudent(data);
        utils.toast(`Profile "${student.name}" created! (ID: ${student.id})`, 'success');
        window.app.currentStudentId = student.id;
      }
      document.getElementById('btn-predict').style.display = '';
      document.getElementById('btn-gen-plan').style.display = '';
      await window.app.loadStudentList();
      this.updateFormTitle(student.name, student.id);
    } catch(e) { utils.toast(e.message, 'error'); }
  },

  updateFormTitle(name, id) {
    const t = document.getElementById('form-title');
    const s = document.getElementById('form-subtitle');
    if (t) t.textContent = name;
    if (s) s.textContent = `ID: ${id} — Edit & save to update`;
  },

  async runPrediction() {
    const id = window.app.currentStudentId;
    if (!id) { utils.toast('Save a profile first','error'); return; }
    try {
      utils.toast('Running prediction...','info');
      const r = await api.predict(id);
      document.getElementById('prediction-result').innerHTML = `
        <div class="card prediction-card">
          <h3 class="card-title">🔮 Prediction Results</h3>
          <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-label">Predicted Score</div><div class="kpi-value">${r.score.predicted_score}</div></div>
            <div class="kpi-card"><div class="kpi-label">Pass Probability</div><div class="kpi-value">${Math.round(r.pass_fail.pass_probability*100)}%</div></div>
            <div class="kpi-card"><div class="kpi-label">Confidence</div><div class="kpi-value">${Math.round(r.score.confidence*100)}%</div></div>
          </div>
          <div class="explanation-section">
            <h4>📝 Why this prediction?</h4>
            <ul class="explanation-list">${r.explanation.explanations.map(e=>`<li class="explanation-item">${e}</li>`).join('')}</ul>
            <p class="key-insight">💡 ${r.explanation.key_insight}</p>
          </div>
        </div>`;
      utils.toast('Prediction complete!','success');
      dashboard.load(id);
    } catch(e) { utils.toast(e.message,'error'); }
  },

  async genPlan() {
    const id = window.app.currentStudentId;
    if (!id) { utils.toast('Save a profile first','error'); return; }
    try {
      utils.toast('Generating study plan...','info');
      await api.generatePlan(id, 4);
      utils.toast('Study plan generated!','success');
      window.app.navigate('plans');
    } catch(e) { utils.toast(e.message,'error'); }
  },

  async loadStudent(id) {
    try {
      const s = await api.getStudent(id);
      const f = document.getElementById('student-form');
      if (!f) return;
      for (const [k,v] of Object.entries(s)) {
        const input = f.querySelector(`[name="${k}"]`);
        if (input && v !== null) {
          input.value = v;
          if (input.type === 'range') {
            const valSpan = input.parentElement.querySelector('.range-val');
            if (valSpan) valSpan.textContent = v;
          }
        }
      }
      this.updateFormTitle(s.name, s.id);
      document.getElementById('btn-predict').style.display = '';
      document.getElementById('btn-gen-plan').style.display = '';
    } catch(e) { console.warn(e); }
  }
};
