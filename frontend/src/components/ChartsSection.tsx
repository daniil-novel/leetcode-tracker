import React, { useRef, useCallback, useState, useEffect } from 'react';
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
  xp?: number;
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
  orange: '#f97316',
  orangeBg: 'rgba(249, 115, 22, 0.2)',
  cyan: '#06b6d4',
  cyanBg: 'rgba(6, 182, 212, 0.2)',
  pink: '#ec4899',
  pinkBg: 'rgba(236, 72, 153, 0.2)',
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
  minHeight: '280px',
  maxHeight: '320px',
  transition: 'all 0.3s ease',
  overflow: 'hidden',
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

// Chart container style with fixed height
const chartContainerStyle: React.CSSProperties = {
  flex: 1,
  position: 'relative',
  height: '180px',
  maxHeight: '180px',
  minHeight: '150px',
};

// Pie/Doughnut container style (smaller)
const pieContainerStyle: React.CSSProperties = {
  flex: 1,
  position: 'relative',
  height: '160px',
  maxHeight: '160px',
  minHeight: '140px',
};

const ChartsSection: React.FC<ChartsSectionProps> = ({
  monthStats,
  dailyStats,
  difficultyStats,
  timeStats,
}) => {
  const [, setFullscreenChart] = useState<string | null>(null);
  const [chartKey, setChartKey] = useState(0);
  
  // Chart refs for export
  const doughnutRef = useRef<ChartJS<'doughnut'>>(null);
  const pieRef = useRef<ChartJS<'pie'>>(null);
  const tasksBarRef = useRef<ChartJS<'bar'>>(null);
  const xpBarRef = useRef<ChartJS<'bar'>>(null);
  const cumulativeLineRef = useRef<ChartJS<'line'>>(null);
  const streakLineRef = useRef<ChartJS<'line'>>(null);
  const timeScatterRef = useRef<ChartJS<'scatter'>>(null);
  const avgTimeBarRef = useRef<ChartJS<'bar'>>(null);
  // New chart refs
  const weekdayBarRef = useRef<ChartJS<'bar'>>(null);
  const xpByDifficultyRef = useRef<ChartJS<'doughnut'>>(null);
  const timeTrendLineRef = useRef<ChartJS<'line'>>(null);
  const topDaysBarRef = useRef<ChartJS<'bar'>>(null);

  // Handle fullscreen change to reset chart size
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        setFullscreenChart(null);
        // Force re-render charts to reset their size
        setChartKey(prev => prev + 1);
        
        // Resize all charts after exiting fullscreen
        setTimeout(() => {
          const refs = [
            doughnutRef, pieRef, tasksBarRef, xpBarRef,
            cumulativeLineRef, streakLineRef, timeScatterRef, avgTimeBarRef,
            weekdayBarRef, xpByDifficultyRef, timeTrendLineRef, topDaysBarRef
          ];
          refs.forEach(ref => {
            if (ref.current) {
              ref.current.resize();
            }
          });
        }, 100);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

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

  // ===== NEW DATA CALCULATIONS =====
  
  // 1. Activity by weekday
  const weekdayCounts = [0, 0, 0, 0, 0, 0, 0];
  dailyStats.forEach(d => {
    const dayOfWeek = new Date(d.date).getDay();
    weekdayCounts[dayOfWeek] += d.tasks_count;
  });
  // Reorder to start from Monday
  const weekdayLabels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const weekdayData = [
    weekdayCounts[1], weekdayCounts[2], weekdayCounts[3], 
    weekdayCounts[4], weekdayCounts[5], weekdayCounts[6], weekdayCounts[0]
  ];

  // 2. XP by difficulty
  const xpByDifficulty = { easy: 0, medium: 0, hard: 0 };
  difficultyStats.forEach(task => {
    const xp = task.xp || (task.difficulty === 'easy' ? 10 : task.difficulty === 'medium' ? 20 : 30);
    if (task.difficulty === 'easy') xpByDifficulty.easy += xp;
    else if (task.difficulty === 'medium') xpByDifficulty.medium += xp;
    else if (task.difficulty === 'hard') xpByDifficulty.hard += xp;
  });

  // 3. Time trend (average time per week)
  const weeklyAvgTime: { week: string; avgTime: number }[] = [];
  const tasksByWeek: { [key: string]: number[] } = {};
  
  tasksWithTime.forEach(task => {
    const date = new Date(task.solved_at);
    const weekStart = new Date(date);
    weekStart.setDate(date.getDate() - date.getDay());
    const weekKey = weekStart.toISOString().split('T')[0];
    
    if (!tasksByWeek[weekKey]) tasksByWeek[weekKey] = [];
    tasksByWeek[weekKey].push(task.time_minutes || task.time_spent || 0);
  });
  
  Object.entries(tasksByWeek)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-8) // Last 8 weeks
    .forEach(([week, times]) => {
      const avg = times.reduce((a, b) => a + b, 0) / times.length;
      const weekDate = new Date(week);
      weeklyAvgTime.push({
        week: weekDate.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
        avgTime: Math.round(avg * 10) / 10
      });
    });

  // 4. Top 5 days by tasks count
  const topDays = [...dailyStats]
    .filter(d => d.tasks_count > 0)
    .sort((a, b) => b.tasks_count - a.tasks_count)
    .slice(0, 5)
    .map(d => ({
      date: new Date(d.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
      count: d.tasks_count
    }));

  // Common chart options with fixed aspect ratio
  const commonOptions: Partial<ChartOptions<'bar' | 'line'>> = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: { color: COLORS.textMuted, maxRotation: 45, minRotation: 45, font: { size: 10 } },
        grid: { color: COLORS.grayBg },
      },
      y: {
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
        grid: { color: COLORS.grayBg },
      },
    },
  };

  // Base pie/doughnut options
  const basePieOptions = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1.2,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: { color: COLORS.textMuted, padding: 8, font: { size: 10 } },
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
    ...basePieOptions,
    plugins: {
      ...basePieOptions.plugins,
      tooltip: {
        ...basePieOptions.plugins?.tooltip,
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
    ...basePieOptions,
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
      pointRadius: 3,
      pointBackgroundColor: COLORS.purple,
      pointBorderColor: COLORS.cardBg,
      pointBorderWidth: 1,
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
      pointRadius: 3,
      pointBackgroundColor: COLORS.yellow,
      pointBorderColor: COLORS.cardBg,
      pointBorderWidth: 1,
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
        pointRadius: 5,
        pointHoverRadius: 7,
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
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: COLORS.textMuted, padding: 8, font: { size: 10 } },
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
        title: { display: true, text: 'Задача #', color: COLORS.textMuted, font: { size: 10 } },
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
        grid: { color: COLORS.grayBg },
      },
      y: {
        title: { display: true, text: 'Минуты', color: COLORS.textMuted, font: { size: 10 } },
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
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
    maintainAspectRatio: true,
    aspectRatio: 2,
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
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
        grid: { color: COLORS.grayBg },
      },
      y: {
        title: { display: true, text: 'Минуты', color: COLORS.textMuted, font: { size: 10 } },
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
        grid: { color: COLORS.grayBg },
      },
    },
  };

  // ===== NEW CHARTS DATA =====

  // 9. Activity by Weekday (Bar)
  const weekdayBarData = {
    labels: weekdayLabels,
    datasets: [{
      label: 'Задачи',
      data: weekdayData,
      backgroundColor: COLORS.cyanBg,
      borderColor: COLORS.cyan,
      borderWidth: 2,
      borderRadius: 4,
    }],
  };

  const weekdayBarOptions: ChartOptions<'bar'> = {
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

  // 10. XP by Difficulty (Doughnut)
  const xpByDifficultyData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [{
      data: [xpByDifficulty.easy, xpByDifficulty.medium, xpByDifficulty.hard],
      backgroundColor: [COLORS.greenBg, COLORS.yellowBg, COLORS.redBg],
      borderColor: [COLORS.green, COLORS.yellow, COLORS.red],
      borderWidth: 2,
      cutout: '60%',
    }],
  };

  const xpByDifficultyOptions: ChartOptions<'doughnut'> = {
    ...basePieOptions,
    plugins: {
      ...basePieOptions.plugins,
      tooltip: {
        ...basePieOptions.plugins?.tooltip,
        callbacks: {
          label: (ctx) => `${ctx.label}: ${ctx.raw} XP`,
        },
      },
    },
  };

  // 11. Time Trend (Line)
  const timeTrendData = {
    labels: weeklyAvgTime.map(w => w.week),
    datasets: [{
      label: 'Среднее время',
      data: weeklyAvgTime.map(w => w.avgTime),
      borderColor: COLORS.orange,
      backgroundColor: COLORS.orangeBg,
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: COLORS.orange,
      pointBorderColor: COLORS.cardBg,
      pointBorderWidth: 2,
    }],
  };

  const timeTrendOptions: ChartOptions<'line'> = {
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
          label: (ctx) => `Среднее: ${ctx.raw} мин`,
        },
      },
    },
  };

  // 12. Top Days (Horizontal Bar)
  const topDaysBarData = {
    labels: topDays.map(d => d.date),
    datasets: [{
      label: 'Задачи',
      data: topDays.map(d => d.count),
      backgroundColor: COLORS.pinkBg,
      borderColor: COLORS.pink,
      borderWidth: 2,
      borderRadius: 4,
    }],
  };

  const topDaysBarOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
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
    scales: {
      x: {
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
        grid: { color: COLORS.grayBg },
      },
      y: {
        ticks: { color: COLORS.textMuted, font: { size: 10 } },
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
    <div style={{ display: 'flex', gap: '6px' }}>
      <button
        className="chart-btn"
        onClick={() => handleFullscreen(containerId)}
        title="Полноэкранный режим"
        style={{
          padding: '3px 6px',
          borderRadius: '4px',
          border: `1px solid ${COLORS.border}`,
          background: 'transparent',
          color: COLORS.textMuted,
          cursor: 'pointer',
          fontSize: '12px',
        }}
      >
        ⛶
      </button>
      <button
        className="chart-btn"
        onClick={() => exportToPNG(chartRef, filename)}
        title="Экспорт в PNG"
        style={{
          padding: '3px 6px',
          borderRadius: '4px',
          border: `1px solid ${COLORS.border}`,
          background: 'transparent',
          color: COLORS.textMuted,
          cursor: 'pointer',
          fontSize: '12px',
        }}
      >
        📷
      </button>
      <button
        className="chart-btn"
        onClick={() => exportToCSV(csvData, filename)}
        title="Экспорт в CSV"
        style={{
          padding: '3px 6px',
          borderRadius: '4px',
          border: `1px solid ${COLORS.border}`,
          background: 'transparent',
          color: COLORS.textMuted,
          cursor: 'pointer',
          fontSize: '12px',
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
        className="charts-grid-12"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '16px',
          marginTop: '20px',
        }}
      >
        {/* Row 1 */}
        
        {/* 1. Progress to Goal (Doughnut) */}
        <div id="doughnut-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>🎯 Прогресс к цели</span>
            <ChartActions
              containerId="doughnut-chart"
              chartRef={doughnutRef}
              filename="progress-goal"
              csvData={{ labels: ['Выполнено', 'Осталось'], values: [currentXP, remainingXP] }}
            />
          </div>
          <div style={pieContainerStyle}>
            <Doughnut key={`doughnut-${chartKey}`} ref={doughnutRef} data={doughnutData} options={doughnutOptions} />
          </div>
          <div style={{ textAlign: 'center', marginTop: '4px', color: COLORS.textMuted, fontSize: '11px' }}>
            {currentXP} / {targetXP} XP ({Math.round((currentXP / targetXP) * 100)}%)
          </div>
        </div>

        {/* 2. Difficulty Distribution (Pie) */}
        <div id="pie-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>📊 По сложности</span>
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
          <div style={pieContainerStyle}>
            <Pie key={`pie-${chartKey}`} ref={pieRef} data={pieData} options={pieOptions} />
          </div>
        </div>

        {/* 3. Tasks per Day (Bar) */}
        <div id="tasks-bar-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>📅 Задачи в день</span>
            <ChartActions
              containerId="tasks-bar-chart"
              chartRef={tasksBarRef}
              filename="tasks-per-day"
              csvData={{ labels, values: last30Days.map(d => d.tasks_count) }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Bar key={`tasks-bar-${chartKey}`} ref={tasksBarRef} data={tasksBarData} options={tasksBarOptions} />
          </div>
        </div>

        {/* 4. XP per Day (Bar) */}
        <div id="xp-bar-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>⚡ XP в день</span>
            <ChartActions
              containerId="xp-bar-chart"
              chartRef={xpBarRef}
              filename="xp-per-day"
              csvData={{ labels, values: last30Days.map(d => d.xp_sum || d.xp_earned || 0) }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Bar key={`xp-bar-${chartKey}`} ref={xpBarRef} data={xpBarData} options={xpBarOptions} />
          </div>
        </div>

        {/* Row 2 */}

        {/* 5. Cumulative XP (Line) */}
        <div id="cumulative-line-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>📈 Кумулятивный XP</span>
            <ChartActions
              containerId="cumulative-line-chart"
              chartRef={cumulativeLineRef}
              filename="cumulative-xp"
              csvData={{ labels, values: cumulativeXPData }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Line key={`cumulative-${chartKey}`} ref={cumulativeLineRef} data={cumulativeLineData} options={cumulativeLineOptions} />
          </div>
        </div>

        {/* 6. Streak History (Line) */}
        <div id="streak-line-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>🔥 История Streak</span>
            <ChartActions
              containerId="streak-line-chart"
              chartRef={streakLineRef}
              filename="streak-history"
              csvData={{ labels, values: last30Days.map(d => d.streak) }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Line key={`streak-${chartKey}`} ref={streakLineRef} data={streakLineData} options={streakLineOptions} />
          </div>
        </div>

        {/* 7. Time per Task (Scatter) */}
        <div id="time-scatter-chart" style={chartCardStyle} className="chart-card">
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
          <div style={chartContainerStyle}>
            <Scatter key={`scatter-${chartKey}`} ref={timeScatterRef} data={timeScatterData as any} options={timeScatterOptions} />
          </div>
          <div style={{ textAlign: 'center', marginTop: '4px', color: COLORS.textMuted, fontSize: '11px' }}>
            Среднее: {avgTime.toFixed(1)} мин
          </div>
        </div>

        {/* 8. Average Time by Difficulty (Bar) */}
        <div id="avg-time-bar-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>⏰ Время по сложности</span>
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
          <div style={chartContainerStyle}>
            <Bar key={`avg-time-${chartKey}`} ref={avgTimeBarRef} data={avgTimeBarData} options={avgTimeBarOptions} />
          </div>
        </div>

        {/* Row 3 - NEW CHARTS */}

        {/* 9. Activity by Weekday (Bar) */}
        <div id="weekday-bar-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>📆 По дням недели</span>
            <ChartActions
              containerId="weekday-bar-chart"
              chartRef={weekdayBarRef}
              filename="weekday-activity"
              csvData={{ labels: weekdayLabels, values: weekdayData }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Bar key={`weekday-${chartKey}`} ref={weekdayBarRef} data={weekdayBarData} options={weekdayBarOptions} />
          </div>
        </div>

        {/* 10. XP by Difficulty (Doughnut) */}
        <div id="xp-difficulty-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>💎 XP по сложности</span>
            <ChartActions
              containerId="xp-difficulty-chart"
              chartRef={xpByDifficultyRef}
              filename="xp-by-difficulty"
              csvData={{ 
                labels: ['Easy', 'Medium', 'Hard'], 
                values: [xpByDifficulty.easy, xpByDifficulty.medium, xpByDifficulty.hard] 
              }}
            />
          </div>
          <div style={pieContainerStyle}>
            <Doughnut key={`xp-diff-${chartKey}`} ref={xpByDifficultyRef} data={xpByDifficultyData} options={xpByDifficultyOptions} />
          </div>
          <div style={{ textAlign: 'center', marginTop: '4px', color: COLORS.textMuted, fontSize: '11px' }}>
            Всего: {xpByDifficulty.easy + xpByDifficulty.medium + xpByDifficulty.hard} XP
          </div>
        </div>

        {/* 11. Time Trend (Line) */}
        <div id="time-trend-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>📉 Тренд времени</span>
            <ChartActions
              containerId="time-trend-chart"
              chartRef={timeTrendLineRef}
              filename="time-trend"
              csvData={{ 
                labels: weeklyAvgTime.map(w => w.week), 
                values: weeklyAvgTime.map(w => w.avgTime) 
              }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Line key={`time-trend-${chartKey}`} ref={timeTrendLineRef} data={timeTrendData} options={timeTrendOptions} />
          </div>
        </div>

        {/* 12. Top Days (Horizontal Bar) */}
        <div id="top-days-chart" style={chartCardStyle} className="chart-card">
          <div style={chartTitleStyle}>
            <span>🏆 Лучшие дни</span>
            <ChartActions
              containerId="top-days-chart"
              chartRef={topDaysBarRef}
              filename="top-days"
              csvData={{ 
                labels: topDays.map(d => d.date), 
                values: topDays.map(d => d.count) 
              }}
            />
          </div>
          <div style={chartContainerStyle}>
            <Bar key={`top-days-${chartKey}`} ref={topDaysBarRef} data={topDaysBarData} options={topDaysBarOptions} />
          </div>
        </div>
      </div>

      {/* CSS for responsive grid and hover effects */}
      <style>{`
        .charts-grid-12 {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
        }
        
        .charts-grid-12 > div {
          transition: all 0.3s ease;
        }
        
        .charts-grid-12 > div:hover {
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
        .charts-grid-12 > div:fullscreen,
        .chart-card:fullscreen {
          background: #0b0b10;
          padding: 40px;
          display: flex;
          flex-direction: column;
          max-height: none !important;
          min-height: 100vh;
        }
        
        .charts-grid-12 > div:fullscreen > div:nth-child(2),
        .chart-card:fullscreen > div:nth-child(2) {
          flex: 1;
          min-height: 0;
          max-height: none !important;
          height: auto !important;
        }
        
        /* Responsive */
        @media (max-width: 1600px) {
          .charts-grid-12 {
            grid-template-columns: repeat(3, 1fr) !important;
          }
        }
        
        @media (max-width: 1200px) {
          .charts-grid-12 {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
        
        @media (max-width: 768px) {
          .charts-grid-12 {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};

export default ChartsSection;
