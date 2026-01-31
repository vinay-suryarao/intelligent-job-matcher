/* eslint-disable no-unused-vars */
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../services/api';
import { BrainCircuit, Mail, Lock, ArrowRight, KeyRound } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetMessage, setResetMessage] = useState('');
  const [resetLoading, setResetLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(email, password);

      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Login failed. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setResetLoading(true);
    setResetMessage('');

    try {
      const result = await api.forgotPassword(resetEmail);
      if (result && !result.error) {
        setResetMessage('Password reset link sent to your email!');
      } else {
        setResetMessage(result.error || 'Failed to send reset link');
      }
    } catch (err) {
      setResetMessage('Network error. Please try again.');
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo Section */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <div className="bg-brand-dark p-3 rounded-2xl shadow-lg">
            <BrainCircuit className="text-white w-8 h-8" />
          </div>
          <span className="text-3xl font-black tracking-tighter text-brand-dark uppercase">
            HireStorm
          </span>
        </div>

        <div className="bg-white rounded-3xl shadow-xl p-8">
          {!showForgotPassword ? (
            <>
              <h2 className="text-2xl font-black text-brand-dark text-center mb-2 uppercase tracking-tight">
                Welcome Back
              </h2>
              <p className="text-slate-400 text-center mb-8">
                Sign in to continue your job search
              </p>

              {error && (
                <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-2xl mb-6 font-medium">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                      placeholder="you@example.com"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                      placeholder="••••••••"
                      required
                    />
                  </div>
                </div>

                <div className="text-right">
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(true)}
                    className="text-brand-accent font-bold text-sm hover:underline"
                  >
                    Forgot Password?
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-dark text-white py-4 rounded-2xl font-black uppercase tracking-widest hover:bg-brand-accent transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? 'Signing in...' : 'Sign In'}
                  <ArrowRight size={18} />
                </button>
              </form>

              <p className="text-center mt-6 text-slate-500">
                Don't have an account?{' '}
                <Link to="/register" className="text-brand-accent font-bold hover:underline">
                  Register here
                </Link>
              </p>
            </>
          ) : (
            <>
              <h2 className="text-2xl font-black text-brand-dark text-center mb-2 uppercase tracking-tight">
                Reset Password
              </h2>
              <p className="text-slate-400 text-center mb-8">
                Enter your email to receive reset link
              </p>

              {resetMessage && (
                <div
                  className={`px-4 py-3 rounded-2xl mb-6 font-medium ${
                    resetMessage.includes('sent') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}
                >
                  {resetMessage}
                </div>
              )}

              <form onSubmit={handleForgotPassword} className="space-y-4">
                <div>
                  <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                      type="email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                      placeholder="you@example.com"
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={resetLoading}
                  className="w-full bg-brand-dark text-white py-4 rounded-2xl font-black uppercase tracking-widest hover:bg-brand-accent transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <KeyRound size={18} />
                  {resetLoading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </form>

              <button
                onClick={() => setShowForgotPassword(false)}
                className="w-full mt-4 text-slate-500 font-bold hover:text-brand-dark"
              >
                ← Back to Login
              </button>
            </>
          )}
        </div>

        <p className="text-center mt-6 text-slate-400">
          <Link to="/" className="hover:text-brand-accent">
            ← Back to Home
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;