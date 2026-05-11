import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/endpoints';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');

    // Set a timeout to force-complete loading if getMe() hangs
    let timedOut = false;
    const timeout = setTimeout(() => {
      timedOut = true;
      setLoading(false);
    }, 5000);

    if (token) {
      // Always verify token with server — localStorage user may be stale
      authService.getMe()
        .then((res) => {
          if (timedOut) return;
          const userData = res.data.data;
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
          clearTimeout(timeout);
        })
        .catch(() => {
          if (timedOut) return;
          clearTimeout(timeout);
          clearAuth();
        })
        .finally(() => {
          if (!timedOut) setLoading(false);
        });
    } else {
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
    return userData;
  };

  const register = async (data) => {
    const res = await authService.register(data);
    const { user: userData, tokens } = res.data.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  // Returns user data on success, or {needs_onboarding, google_email, google_name} if role not yet set
  const googleLogin = async (idToken, role = null) => {
    const res = await authService.googleAuth(idToken, role);
    const data = res.data.data;
    if (data.needs_onboarding) return data; // caller handles role selection
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      await authService.logout(refresh);
    } catch {
      // best-effort logout
    }
    clearAuth();
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, logout, googleLogin }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
};
