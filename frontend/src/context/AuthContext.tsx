import { createContext, useState, useEffect, useContext, type ReactNode } from 'react';

interface User {
  username: string;
  avatar_url: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));

  useEffect(() => {
    if (token) {
      localStorage.setItem('auth_token', token);
      // Here you would typically fetch the user profile using the token
      // For now, we'll just simulate it or fetch it if we have an endpoint
      fetchUserProfile(token);
    } else {
      localStorage.removeItem('auth_token');
      setUser(null);
    }
  }, [token]);

  const fetchUserProfile = async (authToken: string) => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // If token is invalid, logout
        logout();
      }
    } catch (error) {
      console.error('Failed to fetch user profile', error);
      logout();
    }
  };

  const login = (newToken: string) => {
    setToken(newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
