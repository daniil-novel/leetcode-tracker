import React, { useRef, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Pie, Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface DailyStat {
  date: string;
  tasks_count: number;
  xp_earned: number;
  streak: number;
}

interface Task {
  id: number;
  title: string;
  difficulty: string;
  time_minutes: number;
  solved_at: string;
}

interface TimeStats {
  avg_time_easy: number;
  avg_time_medium: number;
  avg_time_hard: number;
  total_time: number;
}

interface ChartsSectionProps {
  monthStats: {
    easy_count: number;
    medium_count: number;
    hard_count: number;
    total_tasks: number;
  };
  dailyStats: DailyStat[];
  difficultyStats: Task[];
  timeStats: TimeStats | null;
}

const ChartsSection: React.FC<ChartsSectionProps> = ({
  dailyStats,
  difficultyStats,
  timeStats,
}) => {
  const lineChartRef = useRef<ChartJS<'line'>>(null);
  const pieChartRef = useRef<ChartJS<'pie'>>(null);
  const barChartRef = useRef<ChartJS<'bar'>>(null);

  // Fullscreen handler
  const handleFullscreen = useCallback((chartContainerId: string) => {
    const container = document.getElementById(chartContainerId);
    if (container) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        container.requestFullscreen();
      }
    }
  }, []);

  // Export to PNG
  const exportToPNG = useCallback((chartRef: React.RefObject<ChartJS | null>, filename: string) => {
    if (chartRef.current) {
      const url = chartRef.current.toBase64Image();
      const link = document.createElement('a');
      link.download = `${filename}.png`;
      link.href = url;
      link.click();
    }
  }, []);

  // Export to CSV
  const exportToCSV = useCallback((data: { labels: string[]; values: number[] }, filename: string) => {
    const csvContent = 'data:text/csv;charset=utf-8,' 
      + 'Label,Value\n'
      + data.labels.map((label, i) => `${label},${data.values[i]}`).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${filename}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, []);

  // Prepare data for Line Chart (Tasks by Day)
  const last30Days = dailyStats.slice(-30);
  const lineChartData = {
    labels: last30Days.map(d => {
      const date = new Date(d.date);
      return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
    }),
    datasets: [
      {
        label: 'Задачи',
        data: last30Days.map(d => d.tasks_count),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'XP',
        data: last30Days.map(d => d.xp_earned),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#9ca3af',
        },
      },
      title: {
        display: true,
        text: 'Активность за последние 30 дней',
        color: '#f3f4f6',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(75, 85, 99, 0.3)' },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(75, 85, 99, 0.3)' },
        title: {
          display: true,
          text: 'Задачи',
          color: '#9ca3af',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        ticks: { color: '#9ca3af' },
        grid: { drawOnChartArea: false },
        title: {
          display: true,
          text: 'XP',
          color: '#9ca3af',
        },
      },
    },
  };

  // Prepare data for Pie Chart (Difficulty Distribution)
  const difficultyCount = {
    Easy: difficultyStats.filter(t => t.difficulty === 'Easy').length,
    Medium: difficultyStats.filter(t => t.difficulty === 'Medium').length,
    Hard: difficultyStats.filter(t => t.difficulty === 'Hard').length,
  };

  const pieChartData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [
      {
        data: [difficultyCount.Easy, difficultyCount.Medium, difficultyCount.Hard],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#9ca3af',
          padding: 20,
          font: {
            size: 14,
          },
        },
      },
      title: {
        display: true,
        text: 'Распределение по сложности',
        color: '#f3f4f6',
        font: {
          size: 16,
        },
      },
    },
  };

  // Prepare data for Bar Chart (Average Time by Difficulty)
  const barChartData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [
      {
        label: 'Среднее время (мин)',
        data: [
          timeStats?.avg_time_easy || 0,
          timeStats?.avg_time_medium || 0,
          timeStats?.avg_time_hard || 0,
        ],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Среднее время решения по сложности',
        color: '#f3f4f6',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(75, 85, 99, 0.3)' },
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(75, 85, 99, 0.3)' },
        title: {
          display: true,
          text: 'Минуты',
          color: '#9ca3af',
        },
      },
    },
  };

  return (
    <section className="charts">
      <h2>
        <span className="section-icon">📈</span>
        Графики продуктивности
      </h2>
      
      <div className="charts-grid">
        {/* Line Chart - Tasks by Day */}
        <div className="chart-card" id="line-chart-container">
          <div className="chart-header">
            <div className="chart-actions">
              <button 
                className="chart-btn" 
                onClick={() => handleFullscreen('line-chart-container')}
                title="Полноэкранный режим"
              >
                ⛶
              </button>
              <button 
                className="chart-btn" 
                onClick={() => exportToPNG(lineChartRef, 'tasks-by-day')}
                title="Экспорт в PNG"
              >
                📷
              </button>
              <button 
                className="chart-btn" 
                onClick={() => exportToCSV({
                  labels: last30Days.map(d => d.date),
                  values: last30Days.map(d => d.tasks_count)
                }, 'tasks-by-day')}
                title="Экспорт в CSV"
              >
                📊
              </button>
            </div>
          </div>
          <div className="chart-wrapper">
            <Line ref={lineChartRef} data={lineChartData} options={lineChartOptions} />
          </div>
        </div>

        {/* Pie Chart - Difficulty Distribution */}
        <div className="chart-card" id="pie-chart-container">
          <div className="chart-header">
            <div className="chart-actions">
              <button 
                className="chart-btn" 
                onClick={() => handleFullscreen('pie-chart-container')}
                title="Полноэкранный режим"
              >
                ⛶
              </button>
              <button 
                className="chart-btn" 
                onClick={() => exportToPNG(pieChartRef, 'difficulty-distribution')}
                title="Экспорт в PNG"
              >
                📷
              </button>
              <button 
                className="chart-btn" 
                onClick={() => exportToCSV({
                  labels: ['Easy', 'Medium', 'Hard'],
                  values: [difficultyCount.Easy, difficultyCount.Medium, difficultyCount.Hard]
                }, 'difficulty-distribution')}
                title="Экспорт в CSV"
              >
                📊
              </button>
            </div>
          </div>
          <div className="chart-wrapper">
            <Pie ref={pieChartRef} data={pieChartData} options={pieChartOptions} />
          </div>
        </div>

        {/* Bar Chart - Time by Difficulty */}
        <div className="chart-card" id="bar-chart-container">
          <div className="chart-header">
            <div className="chart-actions">
              <button 
                className="chart-btn" 
                onClick={() => handleFullscreen('bar-chart-container')}
                title="Полноэкранный режим"
              >
                ⛶
              </button>
              <button 
                className="chart-btn" 
                onClick={() => exportToPNG(barChartRef, 'time-by-difficulty')}
                title="Экспорт в PNG"
              >
                📷
              </button>
              <button 
                className="chart-btn" 
                onClick={() => exportToCSV({
                  labels: ['Easy', 'Medium', 'Hard'],
                  values: [
                    timeStats?.avg_time_easy || 0,
                    timeStats?.avg_time_medium || 0,
                    timeStats?.avg_time_hard || 0
                  ]
                }, 'time-by-difficulty')}
                title="Экспорт в CSV"
              >
                📊
              </button>
            </div>
          </div>
          <div className="chart-wrapper">
            <Bar ref={barChartRef} data={barChartData} options={barChartOptions} />
          </div>
        </div>

        {/* Summary Stats Card */}
        <div className="chart-card stats-summary">
          <h3>📊 Сводная статистика</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Всего задач</span>
              <span className="stat-value">{difficultyStats.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Общее время</span>
              <span className="stat-value">{Math.round((timeStats?.total_time || 0) / 60)} ч</span>
            </div>
            <div className="stat-item easy">
              <span className="stat-label">Easy</span>
              <span className="stat-value">{difficultyCount.Easy}</span>
            </div>
            <div className="stat-item medium">
              <span className="stat-label">Medium</span>
              <span className="stat-value">{difficultyCount.Medium}</span>
            </div>
            <div className="stat-item hard">
              <span className="stat-label">Hard</span>
              <span className="stat-value">{difficultyCount.Hard}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Текущий streak</span>
              <span className="stat-value">{dailyStats.length > 0 ? dailyStats[dailyStats.length - 1].streak : 0} 🔥</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ChartsSection;
