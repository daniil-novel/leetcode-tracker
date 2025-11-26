import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

interface GoalSectionProps {
  currentYear: number;
  currentMonth: number;
  targetXP: number;
  onGoalUpdate: () => void;
}

const GoalSection: React.FC<GoalSectionProps> = ({ currentYear, currentMonth, targetXP, onGoalUpdate }) => {
  const [goalInput, setGoalInput] = useState(targetXP);
  const { token } = useAuth();

  useEffect(() => {
    setGoalInput(targetXP);
  }, [targetXP]);

  const handleSetGoal = async () => {
    try {
      const response = await fetch('/api/month/goal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          year: currentYear,
          month: currentMonth,
          target_xp: goalInput
        })
      });

      if (response.ok) {
        onGoalUpdate();
        alert('Цель обновлена!');
      }
    } catch (error) {
      console.error('Failed to set goal', error);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Вы уверены, что хотите удалить ВСЕ задачи? Это действие нельзя отменить!')) return;

    try {
      const response = await fetch('/api/tasks/clear', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const result = await response.json();
      alert(result.message);
      onGoalUpdate(); // Refresh data
    } catch (error) {
      console.error('Failed to clear tasks', error);
    }
  };

  return (
    <section className="goal-section">
      <div className="goal-header">
        <h2>
          <span className="section-icon">🎯</span>
          Цель на месяц
        </h2>
        <div className="goal-controls">
          <div className="goal-edit">
            <input 
              type="number" 
              min="1" 
              value={goalInput} 
              onChange={(e) => setGoalInput(parseInt(e.target.value))}
              className="goal-input" 
            />
            <span className="goal-label">XP</span>
            <button onClick={handleSetGoal} className="goal-btn">Установить</button>
          </div>
          <button onClick={handleClearAll} className="clear-all-btn">🗑️ Очистить все задачи</button>
        </div>
      </div>
    </section>
  );
};

export default GoalSection;
