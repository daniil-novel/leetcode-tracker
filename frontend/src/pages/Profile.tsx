import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './Profile.css';

interface UserProfile {
  id: number;
  username: string;
  email: string | null;
  avatar_url: string | null;
  leetcode_username: string | null;
  oauth_provider: string;
  created_at: string;
}

export default function Profile() {
  const { token } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('/api/profile/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setLeetcodeUsername(data.leetcode_username || '');
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveLeetCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('leetcode_username', leetcodeUsername);

      const response = await fetch('/api/profile/leetcode', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', text: data.message });
        await fetchProfile();
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to update LeetCode username' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveLeetCode = async () => {
    if (!confirm('Are you sure you want to remove LeetCode integration? This will stop automatic synchronization.')) {
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      const response = await fetch('/api/profile/leetcode', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ type: 'success', text: data.message });
        setLeetcodeUsername('');
        await fetchProfile();
      } else {
        setMessage({ type: 'error', text: data.detail || 'Failed to remove LeetCode username' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          Loading profile...
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-content">
        <div className="profile-header">
          <h1 className="profile-title">Profile Settings</h1>
          <p className="profile-subtitle">Manage your account and LeetCode integration</p>
        </div>

        {/* User Info Card */}
        <div className="profile-card">
          <h2 className="card-title">
            <span className="card-title-icon">👤</span>
            Account Information
          </h2>
          <div className="user-avatar-section">
            <div className="user-info">
              <p className="user-name">{profile?.username}</p>
              {profile?.email && (
                <p className="user-email">{profile.email}</p>
              )}
              <span className="user-provider">
                🔐 {profile?.oauth_provider}
              </span>
            </div>
            {profile?.avatar_url && (
              <img 
                src={profile.avatar_url} 
                alt="Avatar" 
                className="user-avatar"
              />
            )}
          </div>
        </div>

        {/* LeetCode Integration Card */}
        <div className="profile-card">
          <h2 className="card-title">
            <span className="card-title-icon">🔗</span>
            LeetCode Integration
          </h2>

          {message && (
            <div className={`alert ${message.type === 'success' ? 'alert-success' : 'alert-error'}`}>
              {message.text}
            </div>
          )}

          <div className="info-box info-box-blue">
            <h3 className="info-box-title">📖 How to find your LeetCode username:</h3>
            <ol className="info-list">
              <li>Go to <a href="https://leetcode.com" target="_blank" rel="noopener noreferrer" className="link-underline">leetcode.com</a></li>
              <li>Click on your profile picture in the top right corner</li>
              <li>Your username is displayed in the URL: <code className="code-snippet">leetcode.com/u/YOUR_USERNAME/</code></li>
              <li>Make sure your profile is set to <strong>Public</strong> in Settings</li>
            </ol>
          </div>
          
          <div className="info-box info-box-yellow">
            <p>
              <span className="warning-icon">⚠️</span>
              <strong>Important:</strong> Your LeetCode profile must be public for synchronization to work!
            </p>
          </div>

          <form onSubmit={handleSaveLeetCode}>
            <div className="form-group">
              <label htmlFor="leetcode_username" className="form-label">
                LeetCode Username
              </label>
              <input
                type="text"
                id="leetcode_username"
                value={leetcodeUsername}
                onChange={(e) => setLeetcodeUsername(e.target.value)}
                placeholder="Enter your LeetCode username (e.g., user0934Nf)"
                className="form-input"
                required
              />
              <p className="form-hint">
                Example: if your profile is <code className="code-snippet">leetcode.com/u/user0934Nf/</code>, enter <strong>"user0934Nf"</strong>
              </p>
            </div>

            <div className="button-group">
              <button
                type="submit"
                disabled={saving || !leetcodeUsername}
                className="btn btn-primary"
              >
                {saving ? '⏳ Saving...' : profile?.leetcode_username ? '🔄 Update Username' : '🔗 Connect LeetCode'}
              </button>

              {profile?.leetcode_username && (
                <button
                  type="button"
                  onClick={handleRemoveLeetCode}
                  disabled={saving}
                  className="btn btn-danger"
                >
                  🗑️ Disconnect
                </button>
              )}
            </div>
          </form>

          {profile?.leetcode_username && (
            <div className="info-box info-box-green">
              <h3 className="info-box-title">✅ LeetCode Connected</h3>
              <p className="connected-text">
                Currently syncing with: <strong>{profile.leetcode_username}</strong>
              </p>
              <p>
                🔄 Automatic synchronization is active! Your solved problems will appear in the calendar within 10 seconds.
              </p>
            </div>
          )}

          <div className="info-box info-box-gray">
            <h3 className="info-box-title">ℹ️ How it works:</h3>
            <ul className="info-list">
              <li>Enter your LeetCode username and click "Connect LeetCode"</li>
              <li>The system will verify your username exists on LeetCode</li>
              <li>Once connected, automatic synchronization starts immediately</li>
              <li>Every 10 seconds, your latest solved problems are synced</li>
              <li>Problems appear in your calendar and statistics automatically</li>
              <li>No manual import needed - just solve problems on LeetCode!</li>
            </ul>
          </div>
        </div>

        <div className="back-link-container">
          <a href="/" className="back-link">
            ← Back to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
