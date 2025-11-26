import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const [searchParams] = useSearchParams();
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const error = searchParams.get('error');
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      login(token);
      navigate('/');
    } else if (isAuthenticated) {
      navigate('/');
    }
  }, [token, isAuthenticated, login, navigate]);

  return (
    <div className="login-body">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🚀 LeetCode Tracker</h1>
          <p>Отслеживай прогресс решения задач</p>
          <p style={{ color: '#6b7280', fontSize: '14px', marginTop: '10px' }}>Войти через GitHub</p>
        </div>

        {error && (
          <div className="error-message">
            ❌ Ошибка: {error}
          </div>
        )}

        <div className="security-note">
          🔒 Безопасная авторизация через GitHub OAuth
        </div>

        <a href="/auth/github" className="github-btn">
          <svg height="28" viewBox="0 0 16 16" version="1.1" width="28" aria-hidden="true">
            <path fill="currentColor" fillRule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
          </svg>
          Войти через GitHub
        </a>

        <div className="features">
          <div className="feature-item">
            <span className="feature-icon">✨</span>
            <span>Автоматический вход через GitHub аккаунт</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <span>Персональное отслеживание прогресса</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🏆</span>
            <span>Таблица лидеров и соревнования</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📈</span>
            <span>Графики и детальная статистика</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔐</span>
            <span>Безопасное хранение данных</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
