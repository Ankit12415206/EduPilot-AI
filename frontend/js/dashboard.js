/** Dashboard charts & analytics module — enhanced with extra charts */
window.dashboard = {
  charts: {},

  async load(studentId) {
    try {
      const [overview, heatmap] = await Promise.all([
        api.getOverview(studentId),
        api.getHeatmap(studentId),
      ]);
      this.renderKPIs(overview);
      this.renderRadar(overview.current_scores);
      this.renderHeatmap(heatmap.heatmap);
      this.renderGauge(overview.predicted_score, overview.pass_probability);
      this.renderBarChart(overview.current_scores);
      this.renderPieChart(overview);
      try {
        const trends = await api.getTrends(studentId);
        if (trends.study_trend.length) this.renderTrendLine(trends.study_trend);
      } catch(e) {}
    } catch (e) {
      console.warn('Dashboard load:', e.message);
      this.renderEmpty();
    }
  },

  renderKPIs(d) {
    const el = document.getElementById('kpi-grid');
    if (!el) return;
    el.innerHTML = `
      <div class="kpi-card animate-in">
        <div class="kpi-label">Predicted Score</div>
        <div class="kpi-value">${d.predicted_score ?? '—'}</div>
        <div class="kpi-detail">Target: ${d.target_score}</div>
      </div>
      <div class="kpi-card animate-in" style="animation-delay:.08s">
        <div class="kpi-label">Pass Probability</div>
        <div class="kpi-value">${d.pass_probability != null ? Math.round(d.pass_probability*100)+'%' : '—'}</div>
        <div class="kpi-detail">${d.prediction_label || 'Run prediction first'}</div>
      </div>
      <div class="kpi-card animate-in" style="animation-delay:.16s">
        <div class="kpi-label">Study Streak</div>
        <div class="kpi-value"><span class="streak-fire">🔥</span> ${d.study_streak}</div>
        <div class="kpi-detail">${d.weekly_study_hours}h studied this week</div>
      </div>
      <div class="kpi-card animate-in" style="animation-delay:.24s">
        <div class="kpi-label">Weak Subjects</div>
        <div class="kpi-value" style="color:var(--critical)">${d.weak_subjects_count}</div>
        <div class="kpi-detail">${d.strong_subjects_count} strong subjects</div>
      </div>
      <div class="kpi-card animate-in" style="animation-delay:.32s">
        <div class="kpi-label">Tasks Completed</div>
        <div class="kpi-value">${d.tasks_completion_rate ? Math.round(d.tasks_completion_rate*100)+'%' : '—'}</div>
        <div class="kpi-detail">Assignment completion rate</div>
      </div>
    `;
  },

  renderRadar(scores) {
    const ctx = document.getElementById('radar-chart');
    if (!ctx) return;
    if (this.charts.radar) this.charts.radar.destroy();
    const labels = Object.keys(scores).map(s => s.charAt(0).toUpperCase()+s.slice(1));
    const values = Object.values(scores);
    this.charts.radar = new Chart(ctx, {
      type: 'radar',
      data: {
        labels,
        datasets: [{
          label: 'Scores',
          data: values,
          backgroundColor: 'rgba(124,110,240,0.15)',
          borderColor: '#7c6ef0',
          pointBackgroundColor: '#7c6ef0',
          pointBorderColor: 'rgba(255,255,255,.6)',
          borderWidth: 2, pointRadius: 4,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { r: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, pointLabels: { color: '#8b97b0', font: { size: 11 } }, ticks: { display: false } } },
        plugins: { legend: { display: false } }
      }
    });
  },

  renderGauge(score, passProbability) {
    const ctx = document.getElementById('gauge-chart');
    if (!ctx || score == null) return;
    if (this.charts.gauge) this.charts.gauge.destroy();
    const color = score >= 80 ? '#40c9a2' : score >= 60 ? '#5b8def' : score >= 40 ? '#f0a05e' : '#e85d6f';
    this.charts.gauge = new Chart(ctx, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [score, 100 - score],
          backgroundColor: [color, 'rgba(255,255,255,0.04)'],
          borderWidth: 0, circumference: 270, rotation: 225,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '80%',
        plugins: { legend: { display: false }, tooltip: { enabled: false } }
      },
      plugins: [{
        id: 'gaugeText',
        afterDraw(chart) {
          const { ctx: c, width, height } = chart;
          c.save();
          c.textAlign = 'center';
          c.fillStyle = '#e8ecf4';
          c.font = 'bold 2rem Inter, sans-serif';
          c.fillText(score, width/2, height/2 + 10);
          c.font = '0.75rem Inter, sans-serif';
          c.fillStyle = '#8b97b0';
          c.fillText('Predicted Score', width/2, height/2 + 32);
          c.restore();
        }
      }]
    });
  },

  renderBarChart(scores) {
    const ctx = document.getElementById('bar-chart');
    if (!ctx || !scores) return;
    if (this.charts.bar) this.charts.bar.destroy();
    const labels = Object.keys(scores).map(s => s.charAt(0).toUpperCase()+s.slice(1));
    const values = Object.values(scores);
    const colors = values.map(v => v >= 80 ? '#40c9a2' : v >= 60 ? '#5b8def' : v >= 40 ? '#f0a05e' : '#e85d6f');
    this.charts.bar = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ label: 'Score', data: values, backgroundColor: colors, borderRadius: 6, borderSkipped: false, barPercentage: 0.6 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { color: '#8b97b0' } },
          y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#8b97b0' } }
        },
        plugins: { legend: { display: false } }
      }
    });
  },

  renderPieChart(overview) {
    const ctx = document.getElementById('pie-chart');
    if (!ctx) return;
    if (this.charts.pie) this.charts.pie.destroy();
    const studyH = overview.weekly_study_hours || 0;
    const sleepH = 49; // 7h * 7 days estimated
    const socialH = 14;
    const otherH = Math.max(0, 168 - studyH - sleepH - socialH);
    this.charts.pie = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Study', 'Sleep', 'Social/Leisure', 'Other'],
        datasets: [{
          data: [studyH, sleepH, socialH, otherH],
          backgroundColor: ['#7c6ef0', '#5b8def', '#f0a05e', 'rgba(255,255,255,0.06)'],
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '55%',
        plugins: { legend: { position: 'bottom', labels: { color: '#8b97b0', font: { size: 11 }, padding: 12 } } }
      }
    });
  },

  renderHeatmap(data) {
    const el = document.getElementById('heatmap-grid');
    if (!el) return;
    el.innerHTML = data.map(d => `
      <div class="heatmap-cell ${utils.severityClass(d.severity)}">
        <div class="subject">${d.subject}</div>
        <div class="score">${d.score}</div>
        <div>${utils.severity(d.severity)}</div>
      </div>
    `).join('');
  },

  renderTrendLine(data) {
    const ctx = document.getElementById('trend-chart');
    if (!ctx || !data.length) return;
    if (this.charts.trend) this.charts.trend.destroy();
    this.charts.trend = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(d => d.date),
        datasets: [{
          label: 'Hours Studied',
          data: data.map(d => d.hours),
          borderColor: '#7c6ef0',
          backgroundColor: 'rgba(124,110,240,0.08)',
          fill: true, tension: 0.4, borderWidth: 2, pointRadius: 3,
        }, {
          label: 'Self Rating',
          data: data.map(d => d.avg_rating),
          borderColor: '#40c9c6',
          borderWidth: 2, tension: 0.4, pointRadius: 3,
          yAxisID: 'y1',
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#576174', maxTicksLimit: 7 } },
          y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#576174' }, title: { display: true, text: 'Hours', color: '#576174' } },
          y1: { position: 'right', grid: { display: false }, ticks: { color: '#40c9c6' }, title: { display: true, text: 'Rating', color: '#40c9c6' }, min: 1, max: 5 },
        },
        plugins: { legend: { labels: { color: '#8b97b0' } } }
      }
    });
  },

  renderEmpty() {
    const el = document.getElementById('kpi-grid');
    if (el) el.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="icon">📊</div><p>Create a profile to see analytics</p></div>';
  }
};
