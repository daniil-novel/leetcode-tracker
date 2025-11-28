import React from 'react';

interface ChartsSectionProps {
  monthStats: any;
  dailyStats: any[];
  difficultyStats: any[];
  timeStats: any;
}

const ChartsSection: React.FC<ChartsSectionProps> = () => {
  return (
    <section className="charts">
      <h2>
        <span className="section-icon">📈</span>
        Графики продуктивности (Grafana)
        <button className="import-btn">📥 Импорт из CSV</button>
      </h2>
      <div className="chart-container" style={{ height: '800px', width: '100%', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border)' }}>
        <iframe
          src="/grafana/d/leetcode-tracker/leetcode-tracker?orgId=1&kiosk"
          width="100%"
          height="100%"
          frameBorder="0"
          title="Grafana Dashboard"
        ></iframe>
      </div>
    </section>
  );
};

export default ChartsSection;
