import React from 'react';

interface MetricsSectionProps {
  progressPercent: number;
  currentXP: number;
  targetXP: number;
  totalTasks: number;
  easyCount: number;
  mediumCount: number;
  hardCount: number;
  currentStreak: number;
}

const MetricsSection: React.FC<MetricsSectionProps> = ({
  progressPercent,
  currentXP,
  targetXP,
  totalTasks,
  easyCount,
  mediumCount,
  hardCount,
  currentStreak
}) => {
  return (
    <section className="metrics-section">
      <div className="metric-card gradient-blue">
        <div className="metric-icon">📊</div>
        <div className="metric-content">
          <div className="metric-label">Прогресс</div>
          <div className="metric-value">{Math.round(progressPercent)}%</div>
          <div className="metric-subtitle">{currentXP} / {targetXP} XP</div>
        </div>
      </div>
      <div className="metric-card gradient-green">
        <div className="metric-icon">✅</div>
        <div className="metric-content">
          <div className="metric-label">Решено задач</div>
          <div className="metric-value">{totalTasks}</div>
          <div className="metric-subtitle">в этом месяце</div>
        </div>
      </div>
      <div className="metric-card gradient-purple">
        <div className="metric-icon">📚</div>
        <div className="metric-content">
          <div className="metric-label">Распределение</div>
          <div className="metric-value metric-distribution">
            <span className="diff-indicator easy">{easyCount}</span>
            <span className="diff-indicator medium">{mediumCount}</span>
            <span className="diff-indicator hard">{hardCount}</span>
          </div>
          <div className="metric-subtitle">Easy / Medium / Hard</div>
        </div>
      </div>
      <div className="metric-card gradient-orange">
        <div className="metric-icon">🔥</div>
        <div className="metric-content">
          <div className="metric-label">Текущий Streak</div>
          <div className="metric-value">{currentStreak}</div>
          <div className="metric-subtitle">дней подряд</div>
        </div>
      </div>
    </section>
  );
};

export default MetricsSection;
