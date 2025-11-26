import React from 'react';

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
}

const RecentTasksTable: React.FC<RecentTasksTableProps> = ({ tasks }) => {
  return (
    <section className="table-section">
      <h2>
        <span className="section-icon">📝</span>
        Последние задачи
        <span className="task-counter" id="taskCounter">{tasks.length} задач</span>
      </h2>
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
