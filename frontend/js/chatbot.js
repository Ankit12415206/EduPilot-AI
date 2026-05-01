/**
 * EduPilot AI — Help Chatbot
 * Rule-based chatbot with predefined knowledge about the system.
 */
window.chatbot = {
  isOpen: false,
  messages: [],

  init() {
    this.createWidget();
    this.addBotMessage("Hi! I'm your EduPilot AI assistant. How can I help you today? Try asking about predictions, study plans, or how to use the app.");
  },

  createWidget() {
    // Chat button
    const btn = document.createElement('button');
    btn.id = 'chat-btn';
    btn.className = 'chat-toggle-btn';
    btn.innerHTML = '💬';
    btn.title = 'Help Chat';
    btn.onclick = () => this.toggle();
    document.body.appendChild(btn);

    // Chat panel
    const panel = document.createElement('div');
    panel.id = 'chat-panel';
    panel.className = 'chat-panel';
    panel.innerHTML = `
      <div class="chat-header">
        <div style="display:flex;align-items:center;gap:.5rem">
          <span style="font-size:1.2rem">🤖</span>
          <div>
            <div style="font-weight:700;font-size:.9rem">EduPilot Assistant</div>
            <div style="font-size:.7rem;color:var(--good)">● Online</div>
          </div>
        </div>
        <button class="chat-close" onclick="chatbot.toggle()">✕</button>
      </div>
      <div class="chat-messages" id="chat-messages"></div>
      <div class="chat-quick">
        <button class="chat-chip" onclick="chatbot.sendQuick('How do I get a prediction?')">🔮 Get Prediction</button>
        <button class="chat-chip" onclick="chatbot.sendQuick('How does the study plan work?')">📋 Study Plans</button>
        <button class="chat-chip" onclick="chatbot.sendQuick('What features does this app have?')">✨ Features</button>
      </div>
      <form class="chat-input" onsubmit="chatbot.send(event)">
        <input type="text" id="chat-input" placeholder="Ask me anything..." autocomplete="off" />
        <button type="submit">➤</button>
      </form>
    `;
    document.body.appendChild(panel);
  },

  toggle() {
    this.isOpen = !this.isOpen;
    document.getElementById('chat-panel').classList.toggle('open', this.isOpen);
    document.getElementById('chat-btn').classList.toggle('active', this.isOpen);
    if (this.isOpen) document.getElementById('chat-input').focus();
  },

  addBotMessage(text) {
    this.messages.push({ role: 'bot', text });
    this.renderMessages();
  },

  addUserMessage(text) {
    this.messages.push({ role: 'user', text });
    this.renderMessages();
  },

  renderMessages() {
    const el = document.getElementById('chat-messages');
    if (!el) return;
    el.innerHTML = this.messages.map(m => `
      <div class="chat-msg chat-${m.role}">
        <div class="chat-bubble">${m.text}</div>
      </div>
    `).join('');
    el.scrollTop = el.scrollHeight;
  },

  send(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    this.addUserMessage(text);
    setTimeout(() => this.respond(text), 400);
  },

  sendQuick(text) {
    this.addUserMessage(text);
    setTimeout(() => this.respond(text), 400);
  },

  respond(input) {
    const q = input.toLowerCase();
    let answer = this.findAnswer(q);
    this.addBotMessage(answer);
  },

  findAnswer(q) {
    // Prediction related
    if (q.includes('predict') || q.includes('score') || q.includes('performance')) {
      return "🔮 <b>Getting a Prediction:</b><br>1. Go to <b>Student Profile</b> tab<br>2. Fill in your academic data (scores, attendance, study hours, etc.)<br>3. Click <b>Save Student</b><br>4. Click <b>Run Prediction</b><br><br>Our ML model (Random Forest + XGBoost ensemble) will predict your final score and pass/fail probability with ~97% accuracy!";
    }
    // Study plan
    if (q.includes('study plan') || q.includes('schedule') || q.includes('plan')) {
      return "📋 <b>Study Plans:</b><br>1. Save your profile and run a prediction first<br>2. Click <b>Generate Study Plan</b> on the profile page, or go to the <b>Study Plan</b> tab<br>3. You'll get a personalized weekly schedule prioritized by your weak subjects<br>4. Check off daily tasks as you complete them<br>5. The plan uses <b>spaced repetition</b> for better retention!";
    }
    // Weakness
    if (q.includes('weak') || q.includes('strength') || q.includes('improve')) {
      return "🎯 <b>Weakness Detection:</b><br>The system automatically identifies your weak subjects by comparing each score against your average and target. Weaknesses are rated:<br>• 🔴 <b>Critical</b> — significantly below average<br>• 🟡 <b>Moderate</b> — somewhat below<br>• 🔵 <b>Mild</b> — slightly below<br>• 🟢 <b>Strong</b> — at or above target<br><br>Check the <b>Dashboard heatmap</b> for a visual overview!";
    }
    // Progress
    if (q.includes('progress') || q.includes('log') || q.includes('track') || q.includes('streak')) {
      return "📈 <b>Progress Tracking:</b><br>1. Go to the <b>Progress</b> tab<br>2. Click <b>Log Progress</b> to record a study session<br>3. Enter subject, hours, topics, and self-rating<br>4. Build your 🔥 study streak by logging daily!<br>5. The adaptive engine monitors your progress and adjusts your plan automatically.";
    }
    // Features
    if (q.includes('feature') || q.includes('what can') || q.includes('what does')) {
      return "✨ <b>EduPilot AI Features:</b><br>• 🔮 ML Performance Prediction (97% accuracy)<br>• 📊 SHAP Explainable AI (understand WHY)<br>• 📋 Personalized Study Plans with spaced repetition<br>• 🧠 Adaptive Learning Engine<br>• 📈 Progress Tracking & Streaks<br>• 🗺️ Weakness Heatmap & Radar Charts<br>• 🎤 Voice Commands<br>• 🌙 Dark/Light Theme<br>• 👥 Multi-student Support<br>• 💡 Smart Recommendations";
    }
    // SHAP / explain
    if (q.includes('shap') || q.includes('explain') || q.includes('why')) {
      return "🧠 <b>Explainable AI (SHAP):</b><br>After running a prediction, you'll see explanations like:<br>• ✅ 'Daily Study Hours is boosting your score by +5.2 points'<br>• ⚠️ 'Social Media Usage is reducing your score by -3.1 points'<br><br>This uses SHAP (SHapley Additive exPlanations) to show the impact of each factor on your predicted score.";
    }
    // Voice
    if (q.includes('voice') || q.includes('speak') || q.includes('microphone')) {
      return "🎤 <b>Voice Commands:</b><br>Click the 🎤 button (bottom-right) and try saying:<br>• 'What should I study today?' → Opens Study Plan<br>• 'Am I improving?' → Opens Progress<br>• 'Show my dashboard' → Opens Dashboard<br>• 'Run prediction' → Triggers prediction<br><br>Note: Works in Chrome/Edge browsers.";
    }
    // Login / auth
    if (q.includes('login') || q.includes('account') || q.includes('register') || q.includes('password')) {
      return "🔐 <b>Login & Accounts:</b><br>• Create an account on the login page with username + password<br>• Demo account: <code>demo</code> / <code>demo123</code><br>• Each user can manage multiple student profiles<br>• Click the logout button in the sidebar to switch accounts";
    }
    // ML / model
    if (q.includes('model') || q.includes('algorithm') || q.includes('machine learning') || q.includes('ml')) {
      return "🤖 <b>ML Models Used:</b><br>• <b>Random Forest</b> — 200 trees, max_depth=12<br>• <b>XGBoost</b> — 200 estimators, learning_rate=0.1<br>• <b>Ensemble</b> — RF(40%) + XGB(60%) weighted average<br>• <b>Metrics:</b> RMSE=0.82, Accuracy=97.25%, F1=0.98<br>• Trained on 2000 students (1000 Kaggle + 1000 synthetic)<br>• 17 features including demographics, behavior, and scores";
    }
    // Data
    if (q.includes('data') || q.includes('dataset') || q.includes('student')) {
      return "📊 <b>Dataset:</b><br>Our model is trained on 2000 students:<br>• 1000 from <b>Kaggle StudentsPerformance</b> dataset<br>• 1000 <b>synthetically generated</b> with realistic correlations<br>• <b>17 features:</b> gender, ethnicity, parental education, lunch type, test prep, attendance, study hours, assignments, sleep, social media, stress, extracurriculars, and 5 subject scores";
    }
    // Help
    if (q.includes('help') || q.includes('how to') || q.includes('guide') || q.includes('start')) {
      return "🚀 <b>Getting Started:</b><br>1. Go to <b>Student Profile</b> → enter your data → <b>Save</b><br>2. Click <b>Run Prediction</b> → see your predicted score<br>3. Click <b>Generate Study Plan</b> → get a personalized schedule<br>4. Use <b>Progress</b> tab → log daily study sessions<br>5. Check <b>Dashboard</b> → view charts and analytics<br><br>The system adapts your plan as you make progress!";
    }
    // Greeting
    if (q.includes('hello') || q.includes('hi') || q.includes('hey')) {
      return "Hello! 👋 Welcome to EduPilot AI! I can help you with predictions, study plans, progress tracking, and more. What would you like to know?";
    }
    // Thanks
    if (q.includes('thank') || q.includes('thanks')) {
      return "You're welcome! 😊 Happy studying! Remember, consistency is key — even 30 minutes daily makes a huge difference. Good luck!";
    }
    // Default
    return "I'm not sure about that, but here are things I can help with:<br>• 🔮 How predictions work<br>• 📋 Study plan generation<br>• 📈 Progress tracking<br>• 🎯 Weakness detection<br>• 🧠 SHAP explanations<br>• 🎤 Voice commands<br>• 🔐 Login & accounts<br><br>Try asking about any of these topics!";
  }
};

// Auto-init when DOM ready
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.main-content')) chatbot.init();
});
