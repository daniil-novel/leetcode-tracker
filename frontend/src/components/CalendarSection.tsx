import React from 'react';

interface CalendarDay {
  date: string;
  tasks_count: number;
  xp_sum: number;
  easy_count: number;
  medium_count: number;
  hard_count: number;
  tasks: any[]; // Define a proper Task interface later
}

interface CalendarSectionProps {
  currentYear: number;
  currentMonth: number;
  calendarDays: CalendarDay[];
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onDayClick: (day: CalendarDay) => void;
}

const CalendarSection: React.FC<CalendarSectionProps> = ({
  currentYear,
  currentMonth,
  calendarDays,
  onPrevMonth,
  onNextMonth,
  onDayClick
}) => {
  const monthNames = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

  const firstDayOfMonth = new Date(currentYear, currentMonth - 1, 1);
  let startDayOfWeek = firstDayOfMonth.getDay() - 1;
  if (startDayOfWeek < 0) startDayOfWeek = 6;

  const emptyDays = Array.from({ length: startDayOfWeek });

  return (
    <section className="calendar-section">
      <div className="calendar-header">
        <h2>
          <span className="section-icon">📅</span>
          Календарь активности
        </h2>
        <div className="calendar-nav">
          <button className="nav-btn" onClick={onPrevMonth}>◀</button>
          <span className="calendar-month-title">
            {monthNames[currentMonth]} {currentYear}
          </span>
          <button className="nav-btn" onClick={onNextMonth}>▶</button>
        </div>
      </div>
      <div className="calendar-container">
        <div className="calendar-weekdays">
          <div className="weekday">Пн</div>
          <div className="weekday">Вт</div>
          <div className="weekday">Ср</div>
          <div className="weekday">Чт</div>
          <div className="weekday">Пт</div>
          <div className="weekday">Сб</div>
          <div className="weekday">Вс</div>
        </div>
        <div className="calendar-grid">
          {emptyDays.map((_, index) => (
            <div key={`empty-${index}`} className="calendar-day empty"></div>
          ))}
          {calendarDays.map((day) => {
            const intensity = Math.min(day.xp_sum / 5, 5);
            const isToday = day.date === new Date().toISOString().split('T')[0];
            
            return (
              <div 
                key={day.date} 
                className={`calendar-day ${day.tasks_count > 0 ? 'has-tasks' : ''} ${isToday ? 'today' : ''} ${day.tasks_count > 0 ? `xp-intensity-${Math.ceil(intensity)}` : ''}`}
                onClick={() => day.tasks_count > 0 && onDayClick(day)}
              >
                <div className="day-number">{new Date(day.date).getDate()}</div>
                {day.tasks_count > 0 && (
                  <div className="day-stats">
                    <div className="day-xp">{day.xp_sum} XP</div>
                    <div className="day-tasks">
                      {day.easy_count > 0 && <span className="task-dot easy" title={`${day.easy_count} Easy`}></span>}
                      {day.medium_count > 0 && <span className="task-dot medium" title={`${day.medium_count} Medium`}></span>}
                      {day.hard_count > 0 && <span className="task-dot hard" title={`${day.hard_count} Hard`}></span>}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default CalendarSection;
