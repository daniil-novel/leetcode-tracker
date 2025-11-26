import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

interface Task {
  id: number;
  date: string;
  problem_id: string | null;
  title: string | null;
  difficulty: string;
  points: number;
  notes: string | null;
}

interface RecentTasksTableProps {
  tasks: Task[];
  onTasksUpdated?: () => void;
}

const RecentTasksTable: React.FC<RecentTasksTableProps> = ({ tasks, onTasksUpdated }) => {
  const { token } = useAuth();
  const [isImporting, setIsImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/import/csv', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        alert(result.message || `Успешно импортировано ${result.imported} задач`);
        if (onTasksUpdated) {
          onTasksUpdated();
        }
      } else {
        alert('Ошибка: ' + (result.error || 'Неизвестная ошибка'));
      }
    } catch (error) {
      alert('Ошибка загрузки файла: ' + (error as Error).message);
    } finally {
      setIsImporting(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <section className="table-section">
      <h2>
        <span className="section-icon">📝</span>
        Последние задачи
        <span className="task-counter" id="taskCounter">{tasks.length} задач</span>
      </h2>
      <div style={{ marginBottom: '15px' }}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <button
          onClick={handleImportClick}
          disabled={isImporting}
          style={{
            padding: '10px 20px',
            background: 'rgba(59, 130, 246, 0.2)',
            color: '#60a5fa',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '6px',
            cursor: isImporting ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>📥</span>
          {isImporting ? 'Импорт...' : 'Импорт из CSV'}
        </button>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>ID</th>
              <th>Название</th>
              <th>Сложность</th>
              <th>XP</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => (
              <tr key={t.id} className={`difficulty-${t.difficulty.toLowerCase()}`}>
                <td className="date-cell">{t.date}</td>
                <td className="id-cell">
                  {t.problem_id ? (
                    <a 
                      href={`https://leetcode.com/problems/${t.problem_id}`} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="problem-link"
                    >
                      {t.problem_id}
                    </a>
                  ) : (
                    '—'
                  )}
                </td>
                <td className="title-cell">{t.title || "—"}</td>
                <td className="difficulty-cell">
                  <span className={`difficulty-badge ${t.difficulty.toLowerCase()}`}>
                    {t.difficulty}
                  </span>
                </td>
                <td className="xp-cell">
                  <span className="xp-badge">{t.points} XP</span>
                </td>
                <td className="notes-cell">{t.notes || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default RecentTasksTable;
