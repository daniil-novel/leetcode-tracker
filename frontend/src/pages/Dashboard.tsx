import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import GoalSection from '../components/GoalSection';
import MetricsSection from '../components/MetricsSection';
import CalendarSection from '../components/CalendarSection';
import TaskForm from '../components/TaskForm';
import ChartsSection from '../components/ChartsSection';
import RecentTasksTable from '../components/RecentTasksTable';

const Dashboard = () => {
  const { user, logout, token } = useAuth();
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  
  const [monthStats, setMonthStats] = useState<any>(null);
  const [dailyStats, setDailyStats] = useState<any[]>([]);
  const [difficultyStats, setDifficultyStats] = useState<any[]>([]);
  const [timeStats, setTimeStats] = useState<any>(null);
  const [recentTasks, setRecentTasks] = useState<any[]>([]);

  const fetchData = useCallback(async () => {
    if (!token) return;

    const headers = { 'Authorization': `Bearer ${token}` };

    try {
      // Fetch month stats
      const monthRes = await fetch(`/api/month/stats/${currentYear}/${currentMonth}`, { headers });
      const monthData = await monthRes.json();
      setMonthStats(monthData);

      // Fetch daily stats
      const dailyRes = await fetch('/api/stats/daily', { headers });
      const dailyData = await dailyRes.json();
      setDailyStats(Array.isArray(dailyData) ? dailyData : []);

      // Fetch difficulty stats (all tasks)
      const tasksRes = await fetch('/api/tasks', { headers });
      const tasksData = await tasksRes.json();
      setDifficultyStats(tasksData);
      setRecentTasks(tasksData); // Assuming /api/tasks returns all tasks, we might want to limit this or use a different endpoint for recent tasks

      // Fetch time stats
      const timeRes = await fetch('/api/stats/time', { headers });
      const timeData = await timeRes.json();
      setTimeStats(timeData);

    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }, [token, currentYear, currentMonth]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePrevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const handleDayClick = (day: any) => {
    // Implement day details modal logic here if needed
    console.log('Day clicked:', day);
    alert(`Tasks for ${day.date}: ${day.tasks_count}`);
  };

  if (!monthStats) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <header className="header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>LeetCode Tracker</h1>
          {user && (
            <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
              <span style={{ color: '#9ca3af' }}>Привет, {user.username}!</span>
              <button 
                onClick={logout} 
                style={{ 
                  padding: '8px 16px', 
                  background: 'rgba(239, 68, 68, 0.2)', 
                  color: '#f87171', 
                  border: '1px solid rgba(239, 68, 68, 0.3)', 
                  borderRadius: '6px', 
                  cursor: 'pointer' 
                }}
              >
                Выйти
              </button>
            </div>
          )}
        </div>
      </header>

      <GoalSection 
        currentYear={currentYear}
        currentMonth={currentMonth}
        targetXP={monthStats.target_xp}
        onGoalUpdate={fetchData}
      />

      <MetricsSection 
        progressPercent={monthStats.progress_percent}
        currentXP={monthStats.current_xp}
        targetXP={monthStats.target_xp}
        totalTasks={monthStats.total_tasks}
        easyCount={monthStats.easy_count}
        mediumCount={monthStats.medium_count}
        hardCount={monthStats.hard_count}
        currentStreak={dailyStats.length > 0 ? dailyStats[dailyStats.length - 1].streak : 0}
      />

      <CalendarSection 
        currentYear={currentYear}
        currentMonth={currentMonth}
        calendarDays={monthStats.calendar_days}
        onPrevMonth={handlePrevMonth}
        onNextMonth={handleNextMonth}
        onDayClick={handleDayClick}
      />

      <TaskForm onTaskAdded={fetchData} />

      <ChartsSection 
        monthStats={monthStats}
        dailyStats={dailyStats}
        difficultyStats={difficultyStats}
        timeStats={timeStats}
      />

      <RecentTasksTable tasks={recentTasks} />
    </div>
  );
};

export default Dashboard;
