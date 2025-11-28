import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Bar, Line, Doughnut, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

interface ChartsSectionProps {
  monthStats: any;
  dailyStats: any[];
  difficultyStats: any[];
  timeStats: any;
}

interface ExpandedChart {
  type: 'bar' | 'line' | 'doughnut' | 'pie';
  data: any;
  options: any;
  title: string;
}

const ChartsSection: React.FC<ChartsSectionProps> = ({
  monthStats,
  dailyStats,
  difficultyStats,
  timeStats
}) => {
  const [expandedChart, setExpandedChart] = useState<ExpandedChart | null>(null);

  // Common chart options
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 15,
          usePointStyle: true,
          font: { size: 12 },
          color: '#9ca3af'
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#27272f' }
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#27272f' },
        beginAtZero: true
      }
    }
  };

  const pieOptions = {
    ...commonOptions,
    scales: {} // Pie charts don't have scales
  };

  // Prepare data for charts
  const labels = dailyStats.map(d => d.date);
  const tasksData = dailyStats.map(d => d.tasks_count);
  const xpData = dailyStats.map(d => d.xp_sum);
  const xpCumData = dailyStats.map(d => d.xp_cumulative);
  const streakData = dailyStats.map(d => d.streak);

  const easyCount = difficultyStats.filter(t => t.difficulty === 'Easy').length;
  const mediumCount = difficultyStats.filter(t => t.difficulty === 'Medium').length;
  const hardCount = difficultyStats.filter(t => t.difficulty === 'Hard').length;

  const remainingXP = Math.max(0, (monthStats?.target_xp || 0) - (monthStats?.current_xp || 0));

  const monthGoalData = {
    labels: ['Выполнено', 'Осталось'],
    datasets: [{
      data: [monthStats?.current_xp || 0, remainingXP],
      backgroundColor: ['rgba(34, 197, 94, 0.8)', 'rgba(100, 116, 139, 0.3)'],
      borderColor: ['rgba(34, 197, 94, 1)', 'rgba(100, 116, 139, 0.5)'],
      borderWidth: 2
    }]
  };

  const difficultyData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [{
      data: [easyCount, mediumCount, hardCount],
      backgroundColor: ['rgba(34, 197, 94, 0.8)', 'rgba(251, 191, 36, 0.8)', 'rgba(239, 68, 68, 0.8)'],
      borderColor: ['rgba(34, 197, 94, 1)', 'rgba(251, 191, 36, 1)', 'rgba(239, 68, 68, 1)'],
      borderWidth: 2
    }]
  };

  const tasksPerDayData = {
    labels,
    datasets: [{
      label: 'Задач в день',
      data: tasksData,
      backgroundColor: 'rgba(99, 102, 241, 0.6)',
      borderColor: 'rgba(99, 102, 241, 1)',
      borderWidth: 1,
      borderRadius: 6
    }]
  };

  const xpPerDayData = {
    labels,
    datasets: [{
      label: 'XP в день',
      data: xpData,
      backgroundColor: 'rgba(34, 197, 94, 0.6)',
      borderColor: 'rgba(34, 197, 94, 1)',
      borderWidth: 1,
      borderRadius: 6
    }]
  };

  const xpCumulativeData = {
    labels,
    datasets: [{
      label: 'Кумулятивный XP',
      data: xpCumData,
      borderColor: 'rgba(168, 85, 247, 1)',
      backgroundColor: 'rgba(168, 85, 247, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4
    }]
  };

  const streakChartData = {
    labels,
    datasets: [{
      label: 'Streak (дни)',
      data: streakData,
      borderColor: 'rgba(251, 191, 36, 1)',
      backgroundColor: 'rgba(251, 191, 36, 0.1)',
      borderWidth: 2,
      fill: true,
      tension: 0.4
    }]
  };

  // Time stats charts
  const timeLabels = timeStats?.tasks?.map((t: any) => t.title.substring(0, 20) + (t.title.length > 20 ? '...' : '')) || [];
  const timeData = timeStats?.tasks?.map((t: any) => t.time_spent) || [];
  const timeColors = timeStats?.tasks?.map((t: any) => {
    switch(t.difficulty) {
      case 'Easy': return 'rgba(34, 197, 94, 0.6)';
      case 'Medium': return 'rgba(251, 191, 36, 0.6)';
      case 'Hard': return 'rgba(239, 68, 68, 0.6)';
      default: return 'rgba(99, 102, 241, 0.6)';
    }
  }) || [];

  const timePerTaskData = {
    labels: timeLabels,
    datasets: [{
      label: 'Время (мин)',
      data: timeData,
      backgroundColor: timeColors,
      borderColor: timeColors.map((c: string) => c.replace('0.6', '1')),
      borderWidth: 1,
      borderRadius: 6
    }, {
      label: 'Среднее время',
      data: Array(timeData.length).fill(timeStats?.average_time || 0),
      type: 'line' as const,
      borderColor: 'rgba(255, 99, 132, 0.8)',
      borderWidth: 2,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0
    }]
  };

  const avgTimeByDifficultyData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [{
      label: 'Среднее время (мин)',
      data: [
        timeStats?.avg_by_difficulty?.Easy || 0,
        timeStats?.avg_by_difficulty?.Medium || 0,
        timeStats?.avg_by_difficulty?.Hard || 0
      ],
      backgroundColor: ['rgba(34, 197, 94, 0.6)', 'rgba(251, 191, 36, 0.6)', 'rgba(239, 68, 68, 0.6)'],
      borderColor: ['rgba(34, 197, 94, 1)', 'rgba(251, 191, 36, 1)', 'rgba(239, 68, 68, 1)'],
      borderWidth: 2,
      borderRadius: 8
    }]
  };

  const handleExpand = (type: ExpandedChart['type'], data: any, options: any, title: string) => {
    setExpandedChart({ type, data, options, title });
  };

  const closeModal = () => {
    setExpandedChart(null);
  };

  const renderModalChart = () => {
    if (!expandedChart) return null;
    const { type, data, options } = expandedChart;
    const modalOptions = {
      ...options,
      maintainAspectRatio: false,
    };

    switch (type) {
      case 'bar': return <Bar data={data} options={modalOptions} />;
      case 'line': return <Line data={data} options={modalOptions} />;
      case 'doughnut': return <Doughnut data={data} options={modalOptions} />;
      case 'pie': return <Pie data={data} options={modalOptions} />;
      default: return null;
    }
  };

  return (
    <section className="charts">
      <h2>
        <span className="section-icon">📈</span>
        Графики продуктивности
        <button className="import-btn">📥 Импорт из CSV</button>
      </h2>
      <div className="chart-grid">
        <div className="chart-card">
          <h3>
            Прогресс к цели месяца
            <button className="expand-btn" onClick={() => handleExpand('doughnut', monthGoalData, pieOptions, 'Прогресс к цели месяца')}>⤢</button>
          </h3>
          <Doughnut data={monthGoalData} options={pieOptions} />
        </div>
        <div className="chart-card">
          <h3>
            Распределение по сложности
            <button className="expand-btn" onClick={() => handleExpand('pie', difficultyData, pieOptions, 'Распределение по сложности')}>⤢</button>
          </h3>
          <Pie data={difficultyData} options={pieOptions} />
        </div>
        <div className="chart-card">
          <h3>
            Задачи в день
            <button className="expand-btn" onClick={() => handleExpand('bar', tasksPerDayData, commonOptions, 'Задачи в день')}>⤢</button>
          </h3>
          <Bar data={tasksPerDayData} options={commonOptions} />
        </div>
        <div className="chart-card">
          <h3>
            XP в день
            <button className="expand-btn" onClick={() => handleExpand('bar', xpPerDayData, commonOptions, 'XP в день')}>⤢</button>
          </h3>
          <Bar data={xpPerDayData} options={commonOptions} />
        </div>
        <div className="chart-card">
          <h3>
            Кумулятивный XP
            <button className="expand-btn" onClick={() => handleExpand('line', xpCumulativeData, commonOptions, 'Кумулятивный XP')}>⤢</button>
          </h3>
          <Line data={xpCumulativeData} options={commonOptions} />
        </div>
        <div className="chart-card">
          <h3>
            История Streak
            <button className="expand-btn" onClick={() => handleExpand('line', streakChartData, commonOptions, 'История Streak')}>⤢</button>
          </h3>
          <Line data={streakChartData} options={commonOptions} />
        </div>
        <div className="chart-card">
          <h3>
            Время на задачу
            <button className="expand-btn" onClick={() => handleExpand('bar', timePerTaskData, commonOptions, 'Время на задачу')}>⤢</button>
          </h3>
          <Bar data={timePerTaskData as any} options={commonOptions} />
        </div>
        <div className="chart-card">
          <h3>
            Среднее время по сложности
            <button className="expand-btn" onClick={() => handleExpand('bar', avgTimeByDifficultyData, commonOptions, 'Среднее время по сложности')}>⤢</button>
          </h3>
          <Bar data={avgTimeByDifficultyData} options={commonOptions} />
        </div>
      </div>

      {expandedChart && (
        <div className="modal" style={{ display: 'flex' }} onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <span className="close-modal" onClick={closeModal}>&times;</span>
            <h2>{expandedChart.title}</h2>
            <div style={{ height: '500px', width: '100%' }}>
              {renderModalChart()}
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default ChartsSection;
