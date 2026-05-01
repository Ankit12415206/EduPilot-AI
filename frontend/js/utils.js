/** Utility helpers */
window.utils = {
  toast(msg, type='info') {
    let c = document.getElementById('toast-container');
    if (!c) { c = document.createElement('div'); c.id='toast-container'; c.className='toast-container'; document.body.appendChild(c); }
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => { t.style.opacity='0'; setTimeout(()=>t.remove(),300); }, 3500);
  },
  severity(s) { return `<span class="badge badge-${s}">${s}</span>`; },
  pct(v) { return Math.round(v * 100); },
  scoreColor(s) { return s>=80?'var(--good)':s>=60?'var(--mild)':s>=40?'var(--moderate)':'var(--critical)'; },
  severityClass(s) { return s==='critical'?'heatmap-critical':s==='moderate'?'heatmap-moderate':s==='mild'?'heatmap-mild':'heatmap-strong'; },
};
