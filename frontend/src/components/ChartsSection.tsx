import React, { useRef, useCallback, useState } from 'react';
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
  ScatterController,
} from 'chart.js';
import type { ChartOptions } from 'chart.js';
import { Line, Pie, Bar, Doughnut, Scatter } from 'react-chartjs-2';

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
  Filler,
  ScatterController
);

// Interfaces
interface DailyStat {
  date: string;
  tasks_count: number;
  xp_earned?: number;
  xp_sum?: number;
  streak: number;
  xp_cumulative?: number;
}

interface Task {
  id: number;
  title: string;
  difficulty: string;
  time_minutes?: number;
  time_spent?: number;
  solved_at: string;
}

interface CalendarDay {
  date: string;
  tasks: Task[];
  tasks_count: number;
  xp_sum: number;
}

interface TimeStats {
  avg_time_easy: number;
  avg_time_medium: number;
  avg_time_hard: number;
  total_time: number;
}

interface MonthStats {
  easy_count: number;
  medium_count: number;
  hard_count: number;
  total_tasks: number;
  target_xp?: number;
  current_xp?: number;
  calendar_days?: CalendarDay[];
}

interface ChartsSectionProps {
  monthStats: MonthStats;
  dailyStats: DailyStat[];
  difficultyStats: Task[];
  timeStats: TimeStats | null;
}

// Color palette
const COLORS = {
  green: '#4ade80',
  greenBg: 'rgba(74, 222, 128, 0.2)',
  blue: '#3b82f6',
  blueBg: 'rgba(59, 130, 246, 0.2)',
  purple: '#a855f7',
  purpleBg: 'rgba(168, 85, 247, 0.2)',
  yellow: '#facc15',
  yellowBg: 'rgba(250, 204, 21, 0.2)',
  red: '#ef4444',
  redBg: 'rgba(239, 68, 68, 0.2)',
  gray: '#4b5563',
  grayBg: 'rgba(75, 85, 99, 0.3)',
  text: '#ffffff',
  textMuted: '#9ca3af',
  cardBg: '#1e1e2e',
  border: '#2d2d3d',
};

// Chart card styles
const chartCardStyle: React.CSSProperties = {
  background: COLORS.cardBg,
  borderRadius: '12px',
  padding: '16px',
  border: `1px solid ${COLORS.border}`,
  display: 'flex',
  flexDirection: 'column',
  minHeight: '300px',
  transition: 'all 0.3s ease',
};

const chartTitleStyle: React.CSSProperties = {
  color: COLORS.text,
  fontSize: '14px',
  fontWeight: 500,
  marginBottom: '12px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
};

const ChartsSection: React.FC<ChartsSectionProps> = ({
  monthStats,
  dailyStats,
  difficultyStats,
  timeStats,
}) => {
  const [, setFullscreenChart] = useState<string | null>(null);
  
  // Chart refs for export
  const doughnutRef = useRef<ChartJS<'doughnut'>>(null);
  const pieRef = useRef<ChartJS<'pie'>>(null);
  const tasksBarRef = useRef<ChartJS<'bar'>>(null);
  const xpBarRef = useRef<ChartJS<'bar'>>(null);
  const cumulativeLineRef = useRef<ChartJS<'line'>>(null);
  const streakLineRef = useRef<ChartJS<'line'>>(null);
  const timeScatterRef = useRef<ChartJS<'scatter'>>(null);
  const avgTimeBarRef = useRef<ChartJS<'bar'>>(null);

  // Fullscreen handler
  const handleFullscreen = useCallback((chartContainerId: string) => {
    const container = document.getElementById(chartContainerId);
    if (container) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
        setFullscreenChart(null);
      } else {
        container.requestFullscreen();
        setFullscreenChart(chartContainerId);
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

  // Prepare data
  const last30Days = dailyStats.slice(-30);
  const labels = last30Days.map(d => {
    const date = new Date(d.date);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  });

  // Calculate cumulative XP
  let cumulativeXP = 0;
  const cumulativeXPData = last30Days.map(d => {
    cumulativeXP += (d.xp_sum || d.xp_earned || 0);
    return d.xp_cumulative || cumulativeXP;
  });

  // Get time data from tasks
  const tasksWithTime = difficultyStats.filter(t => (t.time_minutes || t.time_spent || 0) > 0);
  const timeDataPoints = tasksWithTime.map((t, index) => ({
    x: index,
    y: t.time_minutes || t.time_spent || 0,
  }));
  const avgTime = tasksWithTime.length > 0 
    ? tasksWithTime.reduce((sum, t) => sum + (t.time_minutes || t.time_spent || 0), 0) / tasksWithTime.length 
    : 0;

  // Common chart options
  const commonOptions: Partial<ChartOptions<'bar' | 'line'>> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: { color: COLORS.textMuted, maxRotation: 45, minRotation: 45 },
        grid: { color: COLORS.grayBg },
      },
      y: {
        ticks: { color: COLORS.textMuted },
        grid: { color: COLORS.grayBg },
      },
    },
  };

  // 1. Progress to Goal (Doughnut)
  const targetXP = monthStats.target_xp || 1000;
  const currentXP = monthStats.current_xp || 0;
  const remainingXP = Math.max(0, targetXP - currentXP);
  
  const doughnutData = {
    labels: ['Выполнено', 'Осталось'],
    datasets: [{
      data: [currentXP, remainingXP],
      backgroundColor: [COLORS.green, COLORS.gray],
      borderColor: [COLORS.green, COLORS.gray],
      borderWidth: 2,
      cutout: '70%',
    }],
  };

  const doughnutOptions: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: COLORS.textMuted, padding: 16, font: { size: 12 } },
      },
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `${ctx.label}: ${ctx.raw} XP`,
        },
      },
    },
  };

  // 2. Difficulty Distribution (Pie)
  const pieData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [{
      data: [monthStats.easy_count, monthStats.medium_count, monthStats.hard_count],
      backgroundColor: [COLORS.greenBg, COLORS.yellowBg, COLORS.redBg],
      borderColor: [COLORS.green, COLORS.yellow, COLORS.red],
      borderWidth: 2,
    }],
  };

  const pieOptions: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: COLORS.textMuted, padding: 16, font: { size: 12 } },
      },
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
      },
    },
  };

  // 3. Tasks per Day (Bar)
  const tasksBarData = {
    labels,
    datasets: [{
      label: 'Задачи',
      data: last30Days.map(d => d.tasks_count),
      backgroundColor: COLORS.blueBg,
      borderColor: COLORS.blue,
      borderWidth: 2,
      borderRadius: 4,
    }],
  };

  const tasksBarOptions: ChartOptions<'bar'> = {
    ...commonOptions as ChartOptions<'bar'>,
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `Задач: ${ctx.raw}`,
        },
      },
    },
  };

  // 4. XP per Day (Bar)
  const xpBarData = {
    labels,
    datasets: [{
      label: 'XP',
      data: last30Days.map(d => d.xp_sum || d.xp_earned || 0),
      backgroundColor: COLORS.greenBg,
      borderColor: COLORS.green,
      borderWidth: 2,
      borderRadius: 4,
    }],
  };

  const xpBarOptions: ChartOptions<'bar'> = {
    ...commonOptions as ChartOptions<'bar'>,
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `XP: ${ctx.raw}`,
        },
      },
    },
  };

  // 5. Cumulative XP (Line)
  const cumulativeLineData = {
    labels,
    datasets: [{
      label: 'Накопленный XP',
      data: cumulativeXPData,
      borderColor: COLORS.purple,
      backgroundColor: COLORS.purpleBg,
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: COLORS.purple,
      pointBorderColor: COLORS.cardBg,
      pointBorderWidth: 2,
    }],
  };

  const cumulativeLineOptions: ChartOptions<'line'> = {
    ...commonOptions as ChartOptions<'line'>,
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `Всего XP: ${ctx.raw}`,
        },
      },
    },
  };

  // 6. Streak History (Line)
  const streakLineData = {
    labels,
    datasets: [{
      label: 'Streak',
      data: last30Days.map(d => d.streak),
      borderColor: COLORS.yellow,
      backgroundColor: COLORS.yellowBg,
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: COLORS.yellow,
      pointBorderColor: COLORS.cardBg,
      pointBorderWidth: 2,
    }],
  };

  const streakLineOptions: ChartOptions<'line'> = {
    ...commonOptions as ChartOptions<'line'>,
    plugins: {
      ...commonOptions.plugins,
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `Streak: ${ctx.raw} дней`,
        },
      },
    },
  };

  // 7. Time per Task (Scatter + Line)
  const timeScatterData = {
    datasets: [
      {
        type: 'scatter' as const,
        label: 'Время задачи',
        data: timeDataPoints,
        backgroundColor: COLORS.grayBg,
        borderColor: COLORS.gray,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
      {
        type: 'line' as const,
        label: 'Среднее время',
        data: timeDataPoints.map(() => avgTime),
        borderColor: COLORS.red,
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
      },
    ],
  };

  const timeScatterOptions: ChartOptions<'scatter'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: COLORS.textMuted, padding: 16, font: { size: 12 } },
      },
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `${ctx.raw && typeof ctx.raw === 'object' && 'y' in ctx.raw ? (ctx.raw as {y: number}).y : ctx.raw} мин`,
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'Задача #', color: COLORS.textMuted },
        ticks: { color: COLORS.textMuted },
        grid: { color: COLORS.grayBg },
      },
      y: {
        title: { display: true, text: 'Минуты', color: COLORS.textMuted },
        ticks: { color: COLORS.textMuted },
        grid: { color: COLORS.grayBg },
      },
    },
  };

  // 8. Average Time by Difficulty (Bar)
  const avgTimeBarData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [{
      label: 'Среднее время (мин)',
      data: [
        timeStats?.avg_time_easy || 0,
        timeStats?.avg_time_medium || 0,
        timeStats?.avg_time_hard || 0,
      ],
      backgroundColor: [COLORS.greenBg, COLORS.yellowBg, COLORS.redBg],
      borderColor: [COLORS.green, COLORS.yellow, COLORS.red],
      borderWidth: 2,
      borderRadius: 8,
    }],
  };

  const avgTimeBarOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: COLORS.cardBg,
        titleColor: COLORS.text,
        bodyColor: COLORS.textMuted,
        borderColor: COLORS.border,
        borderWidth: 1,
        callbacks: {
          label: (ctx) => `${ctx.raw} мин`,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: COLORS.textMuted },
        grid: { color: COLORS.grayBg },
      },
      y: {
        title: { display: true, text: 'Минуты', color: COLORS.textMuted },
        ticks: { color: COLORS.textMuted },
        grid: { color: COLORS.grayBg },
      },
    },
  };

  // Chart action buttons component
  const ChartActions: React.FC<{
    containerId: string;
    chartRef: React.RefObject<ChartJS | null>;
    filename: string;
    csvData: { labels: string[]; values: number[] };
  }> = ({ containerId, chartRef, filename, csvData }) => (
    <div style={{ display: 'flex', gap: '8px' }}>
      <button
        className="chart-btn"
        onClick={() => handleFullscreen(containerId)}
        title="Полноэкранный режим"
        style={{
          padding: '4px 8px',
          borderRadius: '6px',
          border: `1px solid ${COLORS.border}`,
          background: 'transparent',
          color: COLORS.textMuted,
          cursor: 'pointer',
          fontSize: '14px',
        }}
      >
        ⛶
      </button>
      <button
        className="chart-btn"
        onClick={() => exportToPNG(chartRef, filename)}
        title="Экспорт в PNG"
        style={{
          padding: '4px 8px',
          borderRadius: '6px',
          border: `1px solid ${COLORS.border}`,
          background: 'transparent',
          color: COLORS.textMuted,
          cursor: 'pointer',
          fontSize: '14px',
        }}
      >
        📷
      </button>
      <button
        className="chart-btn"
        onClick={() => exportToCSV(csvData, filename)}
        title="Экспорт в CSV"
        style={{
          padding: '4px 8px',
          borderRadius: '6px',
          border: `1px solid ${COLORS.border}`,
          background: 'transparent',
          color: COLORS.textMuted,
          cursor: 'pointer',
          fontSize: '14px',
        }}
      >
        📊
      </button>
    </div>
  );

  return (
    <section className="charts">
      <h2>
        <span className="section-icon">📈</span>
        Графики продуктивности
      </h2>
      
      <div 
        className="charts-grid-8"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '20px',
          marginTop: '20px',
        }}
      >
        {/* 1. Progress to Goal (Doughnut) */}
        <div id="doughnut-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>🎯 Прогресс к цели месяца</span>
            <ChartActions
              containerId="doughnut-chart"
              chartRef={doughnutRef}
              filename="progress-goal"
              csvData={{ labels: ['Выполнено', 'Осталось'], values: [currentXP, remainingXP] }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Doughnut ref={doughnutRef} data={doughnutData} options={doughnutOptions} />
          </div>
          <div style={{ textAlign: 'center', marginTop: '8px', color: COLORS.textMuted, fontSize: '12px' }}>
            {currentXP} / {targetXP} XP ({Math.round((currentXP / targetXP) * 100)}%)
          </div>
        </div>

        {/* 2. Difficulty Distribution (Pie) */}
        <div id="pie-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>📊 Распределение по сложности</span>
            <ChartActions
              containerId="pie-chart"
              chartRef={pieRef}
              filename="difficulty-distribution"
              csvData={{ 
                labels: ['Easy', 'Medium', 'Hard'], 
                values: [monthStats.easy_count, monthStats.medium_count, monthStats.hard_count] 
              }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Pie ref={pieRef} data={pieData} options={pieOptions} />
          </div>
        </div>

        {/* 3. Tasks per Day (Bar) */}
        <div id="tasks-bar-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>📅 Задачи в день</span>
            <ChartActions
              containerId="tasks-bar-chart"
              chartRef={tasksBarRef}
              filename="tasks-per-day"
              csvData={{ labels, values: last30Days.map(d => d.tasks_count) }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Bar ref={tasksBarRef} data={tasksBarData} options={tasksBarOptions} />
          </div>
        </div>

        {/* 4. XP per Day (Bar) */}
        <div id="xp-bar-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>⚡ XP в день</span>
            <ChartActions
              containerId="xp-bar-chart"
              chartRef={xpBarRef}
              filename="xp-per-day"
              csvData={{ labels, values: last30Days.map(d => d.xp_sum || d.xp_earned || 0) }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Bar ref={xpBarRef} data={xpBarData} options={xpBarOptions} />
          </div>
        </div>

        {/* 5. Cumulative XP (Line) */}
        <div id="cumulative-line-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>📈 Кумулятивный XP</span>
            <ChartActions
              containerId="cumulative-line-chart"
              chartRef={cumulativeLineRef}
              filename="cumulative-xp"
              csvData={{ labels, values: cumulativeXPData }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Line ref={cumulativeLineRef} data={cumulativeLineData} options={cumulativeLineOptions} />
          </div>
        </div>

        {/* 6. Streak History (Line) */}
        <div id="streak-line-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>🔥 История Streak</span>
            <ChartActions
              containerId="streak-line-chart"
              chartRef={streakLineRef}
              filename="streak-history"
              csvData={{ labels, values: last30Days.map(d => d.streak) }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Line ref={streakLineRef} data={streakLineData} options={streakLineOptions} />
          </div>
        </div>

        {/* 7. Time per Task (Scatter) */}
        <div id="time-scatter-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>⏱️ Время на задачу</span>
            <ChartActions
              containerId="time-scatter-chart"
              chartRef={timeScatterRef}
              filename="time-per-task"
              csvData={{ 
                labels: timeDataPoints.map((_, i) => `Задача ${i + 1}`), 
                values: timeDataPoints.map(p => p.y) 
              }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Scatter ref={timeScatterRef} data={timeScatterData as any} options={timeScatterOptions} />
          </div>
          <div style={{ textAlign: 'center', marginTop: '8px', color: COLORS.textMuted, fontSize: '12px' }}>
            Среднее: {avgTime.toFixed(1)} мин
          </div>
        </div>

        {/* 8. Average Time by Difficulty (Bar) */}
        <div id="avg-time-bar-chart" style={chartCardStyle}>
          <div style={chartTitleStyle}>
            <span>⏰ Среднее время по сложности</span>
            <ChartActions
              containerId="avg-time-bar-chart"
              chartRef={avgTimeBarRef}
              filename="avg-time-difficulty"
              csvData={{ 
                labels: ['Easy', 'Medium', 'Hard'], 
                values: [
                  timeStats?.avg_time_easy || 0,
                  timeStats?.avg_time_medium || 0,
                  timeStats?.avg_time_hard || 0,
                ] 
              }}
            />
          </div>
          <div style={{ flex: 1, position: 'relative', minHeight: '200px' }}>
            <Bar ref={avgTimeBarRef} data={avgTimeBarData} options={avgTimeBarOptions} />
          </div>
        </div>
      </div>

      {/* CSS for responsive grid and hover effects */}
      <style>{`
        .charts-grid-8 {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 20px;
        }
        
        .charts-grid-8 > div {
          transition: all 0.3s ease;
        }
        
        .charts-grid-8 > div:hover {
          border-color: #4f46e5 !important;
          box-shadow: 0 8px 24px rgba(79, 70, 229, 0.2);
          transform: translateY(-2px);
        }
        
        .chart-btn:hover {
          background: #4f46e5 !important;
          border-color: #4f46e5 !important;
          color: #fff !important;
        }
        
        /* Fullscreen styles */
        .charts-grid-8 > div:fullscreen {
          background: #0b0b10;
          padding: 40px;
          display: flex;
          flex-direction: column;
        }
        
        .charts-grid-8 > div:fullscreen > div:last-child {
          flex: 1;
          min-height: 0;
        }
        
        /* Responsive */
        @media (max-width: 1400px) {
          .charts-grid-8 {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
        
        @media (max-width: 768px) {
          .charts-grid-8 {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};

export default ChartsSection;
