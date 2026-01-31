/* eslint-disable react-refresh/only-export-components */
/* eslint-disable no-unused-vars */
import { createContext, useContext, useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      try { setUser(JSON.parse(savedUser)); } catch (e) { console.error(e); }
    }
    setLoading(false);
  }, []);

  const register = async (email, password, fullName) => {
    try {
      const res = await fetch(API_URL + '/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user_data));
        localStorage.setItem('user_id', data.user_id);
        setToken(data.access_token);
        setUser({ ...data.user_data, id: data.user_id });
        return { success: true, data };
      }
      return { success: false, error: data.detail || 'Registration failed' };
    // eslint-disable-next-line no-unused-vars
    } catch (err) { return { success: false, error: 'Network error' }; }
  };

  const login = async (email, password) => {
    try {
      const res = await fetch(API_URL + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user_data));
        localStorage.setItem('user_id', data.user_id);
        setToken(data.access_token);
        setUser({ ...data.user_data, id: data.user_id });
        return { success: true, data };
      }
      return { success: false, error: data.detail || 'Invalid credentials' };
    } catch (err) { return { success: false, error: 'Network error' }; }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_id');
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = () => token !== null && user !== null;
  const getUserId = () => localStorage.getItem('user_id');

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated, getUserId }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

export default useAuth;