import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../services/api';
import { BrainCircuit, Mail, Lock, User, Upload, ArrowRight, FileText } from 'lucide-react';

const Register = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [resumeFile, setResumeFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!resumeFile) {
      setError('Please upload your resume!');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match!');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters!');
      return;
    }

    setLoading(true);
    setUploadProgress('Creating account...');

    try {
      const result = await register(formData.email, formData.password, formData.fullName);

      if (result.success) {
        setUploadProgress('Uploading resume...');
        
        // Upload resume
        const uploadResult = await api.uploadResume(resumeFile);
        
        if (uploadResult && !uploadResult.error) {
          setUploadProgress('Analyzing your skills...');
          setParsedData(uploadResult.parsed_data);
          
          setTimeout(() => {
            setUploadProgress('✅ All set! Redirecting...');
            setTimeout(() => navigate('/dashboard'), 1000);
          }, 1000);
        } else {
          // Even if resume upload fails, still redirect
          navigate('/dashboard');
        }
      } else {
        setError(result.error || 'Registration failed');
        setLoading(false);
      }
    } catch (err) {
      setError('Network error');
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.endsWith('.pdf')) {
        setError('Only PDF files are allowed!');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB!');
        return;
      }
      setResumeFile(file);
      setError('');
    }
  };

  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <div className="bg-brand-dark p-3 rounded-2xl shadow-lg">
            <BrainCircuit className="text-white w-8 h-8" />
          </div>
          <span className="text-3xl font-black tracking-tighter text-brand-dark uppercase">HireStorm</span>
        </div>

        <div className="bg-white rounded-3xl shadow-xl p-8">
          <h2 className="text-2xl font-black text-brand-dark text-center mb-2 uppercase tracking-tight">Create Account</h2>
          <p className="text-slate-400 text-center mb-8">Join the smart job matching revolution</p>

          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-2xl mb-6 font-medium">
              {error}
            </div>
          )}

          {uploadProgress && (
            <div className="bg-blue-100 border border-blue-300 text-blue-700 px-4 py-3 rounded-2xl mb-6 font-medium text-center">
              {uploadProgress}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Full Name</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                  className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Resume Upload - COMPULSORY */}
            <div>
              <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">
                Resume (Required) <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                id="resume-input"
              />
              <label
                htmlFor="resume-input"
                className={`flex items-center justify-center gap-3 w-full border-2 border-dashed rounded-2xl p-6 cursor-pointer transition-colors ${
                  resumeFile ? 'border-green-400 bg-green-50' : 'border-slate-300 hover:border-brand-accent'
                }`}
              >
                {resumeFile ? (
                  <>
                    <FileText className="text-green-600" size={24} />
                    <span className="font-bold text-green-700">{resumeFile.name}</span>
                  </>
                ) : (
                  <>
                    <Upload className="text-slate-400" size={24} />
                    <span className="text-slate-400">Click to upload PDF resume</span>
                  </>
                )}
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-dark text-white py-4 rounded-2xl font-black uppercase tracking-widest hover:bg-brand-accent transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
              <ArrowRight size={18} />
            </button>
          </form>

          <p className="text-center mt-6 text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-accent font-bold hover:underline">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
