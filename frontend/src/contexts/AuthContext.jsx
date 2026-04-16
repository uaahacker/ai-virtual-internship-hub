import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/endpoints';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    console.log('🔍 AuthContext init - user from localStorage:', saved ? 'yes' : 'no');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    console.log('🧹 AuthContext - cleared auth');
  };

  useEffect(() => {
    console.log('🔍 AuthContext useEffect - token verification starting...');
    // Verify token on mount
    const token = localStorage.getItem('access_token');
    console.log('🔍 AuthContext - token exists:', !!token);
    
    // Set a timeout to force-load if getMe() is hanging
    const timeout = setTimeout(() => {
      console.warn('⏱️ AuthContext - getMe() took too long, forcing load');
      if (loading) setLoading(false);
    }, 5000);
    
    if (token && !user) {
      console.log('🔍 AuthContext - calling authService.getMe()...');
      authService.getMe()
        .then((res) => {
          const userData = res.data.data;
          console.log('✅ AuthContext - got user:', userData.id);
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
          clearTimeout(timeout);
        })
        .catch((err) => {
          console.error('❌ AuthContext - getMe() failed:', err.message);
          clearTimeout(timeout);
          clearAuth();
        })
        .finally(() => {
          console.log('🔍 AuthContext - setting loading to false');
          setLoading(false);
        });
    } else {
      console.log('🔍 AuthContext - no token or user exists, setting loading to false');
      clearTimeout(timeout);
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await authService.login({ email, password });
    const { user: userData, tokens } = res.data.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    console.log('✅ AuthContext - login successful, user:', userData.id);
    return userData;
  };

  const register = async (data) => {
    const res = await authService.register(data);
    const { user: userData, tokens } = res.data.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    console.log('✅ AuthContext - register successful, user:', userData.id);
    return userData;
  };

  const logout = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      await authService.logout(refresh);
      console.log('✅ AuthContext - logout API successful');
    } catch (err) {
      console.error('⚠️ AuthContext - logout API failed:', err.message);
    }
    clearAuth();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
};
