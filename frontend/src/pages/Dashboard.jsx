import "../App.css";

function Dashboard() {
  return (
    <div className="dashboard">
      <header className="header">
        <h1>🌾 GramSwaram Farmer</h1>
        <p>AI-powered assistant for farmers</p>
      </header>

      <main className="dashboard-content">
        <section className="welcome-section">
          <h2>Welcome, Farmer 👋</h2>

          <p>
            Your AI-powered farming assistant is here to help
            with crops, farm data, research, and agricultural
            questions.
          </p>

          <button className="ask-button">
            💬 Ask AI Assistant
          </button>
        </section>

        <section className="dashboard-cards">
          <div className="dashboard-card">
            <div className="card-icon">🌱</div>
            <h3>Crop Assistance</h3>
            <p>
              Get AI-based assistance for crop-related
              questions and farming practices.
            </p>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📊</div>
            <h3>Farm Analytics</h3>
            <p>
              View agricultural production data and
              understand farm insights.
            </p>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🔎</div>
            <h3>Agricultural Research</h3>
            <p>
              Research farming topics using the AI research
              agent.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;