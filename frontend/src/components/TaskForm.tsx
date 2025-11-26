import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface TaskFormProps {
  onTaskAdded: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ onTaskAdded }) => {
  const { token } = useAuth();
  const today = new Date().toISOString().split('T')[0];
  
  const [formData, setFormData] = useState({
    date: today,
    difficulty: 'Medium',
    points: 3,
    time_spent: '',
    problem_id: '',
    title: '',
    notes: ''
  });

  const handleDifficultyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const difficulty = e.target.value;
    let points = 3;
    if (difficulty === 'Easy') points = 1;
    if (difficulty === 'Hard') points = 5;
    
    setFormData({ ...formData, difficulty, points });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': `Bearer ${token}`
        },
        body: new URLSearchParams(formData as any).toString()
      });

      if (response.ok) {
        onTaskAdded();
        // Reset form but keep date
        setFormData({
          date: formData.date,
          difficulty: 'Medium',
          points: 3,
          time_spent: '',
          problem_id: '',
          title: '',
          notes: ''
        });
        alert('Задача добавлена!');
      } else {
        alert('Ошибка при добавлении задачи');
      }
    } catch (error) {
      console.error('Failed to add task', error);
    }
  };

  return (
    <section className="form-section">
      <h2>
        <span className="section-icon">➕</span>
        Добавить задачу
      </h2>
      <form onSubmit={handleSubmit} className="task-form">
        <label>
          <span className="label-text">Дата</span>
          <input 
            type="date" 
            name="date" 
            required 
            value={formData.date} 
            onChange={handleChange}
          />
        </label>

        <label>
          <span className="label-text">Сложность</span>
          <select 
            name="difficulty" 
            id="difficultySelect" 
            value={formData.difficulty}
            onChange={handleDifficultyChange}
          >
            <option value="Easy">Easy (1 XP)</option>
            <option value="Medium">Medium (3 XP)</option>
            <option value="Hard">Hard (5 XP)</option>
          </select>
        </label>

        <label>
          <span className="label-text">XP</span>
          <input 
            type="number" 
            name="points" 
            id="pointsInput" 
            value={formData.points} 
            min="1" 
            required 
            onChange={handleChange}
          />
        </label>

        <label>
          <span className="label-text">Время (мин)</span>
          <input 
            type="number" 
            name="time_spent" 
            id="timeSpentInput" 
            placeholder="Сколько минут потратили?" 
            min="1" 
            value={formData.time_spent}
            onChange={handleChange}
          />
        </label>

        <label>
          <span className="label-text">ID задачи</span>
          <input 
            type="text" 
            name="problem_id" 
            placeholder="например 209" 
            value={formData.problem_id}
            onChange={handleChange}
          />
        </label>

        <label className="fullwidth">
          <span className="label-text">Название</span>
          <input 
            type="text" 
            name="title" 
            placeholder="Название задачи (опционально)" 
            value={formData.title}
            onChange={handleChange}
          />
        </label>

        <label className="fullwidth">
          <span className="label-text">Комментарий</span>
          <textarea 
            name="notes" 
            rows={3} 
            placeholder="Что было сложным? Что выучил? Какой подход использовал?"
            value={formData.notes}
            onChange={handleChange}
          ></textarea>
        </label>

        <button type="submit" className="submit-btn">
          <span className="btn-icon">💾</span>
          Сохранить задачу
        </button>
      </form>
    </section>
  );
};

export default TaskForm;
