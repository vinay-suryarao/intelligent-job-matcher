import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatInterface from '../components/ChatInterface';
import { useAuth } from '../hooks/useAuth.jsx';
import api from '../services/api';
import { User, Mail, Phone, MapPin, Save, Upload, X, Plus, Briefcase, Target, MessageCircle, CheckCircle } from 'lucide-react';

const Settings = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    full_name: '',
    email: '',
    skills: [],
    experience_level: 'entry',
    interests: '',
    career_goals: '',
    phone: '',
    location: '',
  });
  const [newSkill, setNewSkill] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [resumeFile, setResumeFile] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await api.getProfile();
      if (data && !data.error) {
        setProfile({
          full_name: data.full_name || '',
          email: data.email || '',
          skills: data.skills || [],
          experience_level: data.experience_level || 'entry',
          interests: data.interests || '',
          career_goals: data.career_goals || '',
          phone: data.phone || '',
          location: data.location || '',
        });
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSkill = () => {
    if (newSkill.trim() && !profile.skills.includes(newSkill.trim())) {
      setProfile({ ...profile, skills: [...profile.skills, newSkill.trim()] });
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setProfile({ ...profile, skills: profile.skills.filter((skill) => skill !== skillToRemove) });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await api.updateProfile({
        full_name: profile.full_name,
        email: profile.email,
        skills: profile.skills,
        experience_level: profile.experience_level,
        interests: profile.interests,
        career_goals: profile.career_goals,
        phone: profile.phone,
        location: profile.location,
      });

      if (result && !result.error) {
        setMessage({ type: 'success', text: 'Profile updated successfully!' });
        setShowSuccessAlert(true);
        setTimeout(() => setShowSuccessAlert(false), 4000);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to update profile' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Network error' });
    } finally {
      setSaving(false);
    }
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) return;
    
    setUploadingResume(true);
    try {
      const result = await api.uploadResume(resumeFile);
      if (result && !result.error && result.parsed_data) {
        setProfile(prev => ({
          ...prev,
          skills: result.parsed_data.skills || prev.skills,
        }));
        setMessage({ type: 'success', text: 'Resume uploaded and parsed successfully!' });
        setResumeFile(null);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to upload resume' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to upload resume' });
    } finally {
      setUploadingResume(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-brand-bg">
        <Sidebar />
        <main className="flex-1 ml-64 flex items-center justify-center">
          <div className="w-16 h-16 border-4 border-brand-accent border-t-transparent rounded-full animate-spin"></div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-brand-bg">
      <Sidebar />
      
      {/* Chat Button */}
      <button 
        onClick={() => setShowChat(true)}
        className="fixed bottom-8 right-8 p-4 rounded-full bg-brand-accent text-white shadow-lg shadow-brand-accent/30 hover:scale-110 transition-transform z-50"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chat Interface */}
      {showChat && (
        <ChatInterface onClose={() => setShowChat(false)} />
      )}

      {/* Success Alert Popup */}
      {showSuccessAlert && (
        <div className="fixed top-8 right-8 bg-green-500 text-white px-6 py-4 rounded-2xl shadow-2xl z-50 flex items-center gap-3 animate-in slide-in-from-right">
          <CheckCircle size={24} />
          <div>
            <p className="font-black uppercase tracking-widest text-sm">Success!</p>
            <p className="text-green-100 text-sm">Your profile has been updated successfully</p>
          </div>
          <button onClick={() => setShowSuccessAlert(false)} className="ml-4 hover:bg-green-600 p-1 rounded-lg">
            <X size={18} />
          </button>
        </div>
      )}
      
      <main className="flex-1 ml-64 p-10">
        <div className="max-w-4xl">
          <div className="mb-10">
            <h1 className="text-5xl font-black text-brand-dark tracking-tighter uppercase mb-2">Settings</h1>
            <p className="text-slate-400 font-medium text-lg">Manage your profile and preferences</p>
          </div>

          {message.text && (
            <div className={`p-4 rounded-2xl mb-6 font-bold flex items-center gap-3 ${
              message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              {message.type === 'success' && <CheckCircle size={20} />}
              {message.text}
            </div>
          )}

          {/* Personal Information */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 mb-6">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight mb-6 flex items-center gap-2">
              <User className="text-brand-accent" size={20} /> Personal Information
            </h2>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Full Name</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="text"
                    value={profile.full_name}
                    onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                    className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                    placeholder="Your full name"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Email</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                    placeholder="your@email.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Phone</label>
                <div className="relative">
                  <Phone className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="tel"
                    value={profile.phone}
                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                    className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                    placeholder="+91 98765 43210"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-600 font-bold text-sm uppercase tracking-wider mb-2">Location</label>
                <div className="relative">
                  <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="text"
                    value={profile.location}
                    onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                    className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 pl-12 pr-4 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
                    placeholder="City, Country"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Resume Upload */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 mb-6">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight mb-6 flex items-center gap-2">
              <Upload className="text-brand-accent" size={20} /> Update Resume
            </h2>
            
            <div className="flex items-center gap-4">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files[0])}
                className="hidden"
                id="resume-upload"
              />
              <label
                htmlFor="resume-upload"
                className="flex-1 border-2 border-dashed border-slate-300 rounded-2xl p-8 text-center cursor-pointer hover:border-brand-accent transition-colors"
              >
                {resumeFile ? (
                  <p className="font-bold text-brand-dark">{resumeFile.name}</p>
                ) : (
                  <p className="text-slate-400">Click to upload PDF resume</p>
                )}
              </label>
              {resumeFile && (
                <button
                  onClick={handleResumeUpload}
                  disabled={uploadingResume}
                  className="bg-brand-accent text-white px-8 py-4 rounded-2xl font-black uppercase tracking-widest hover:bg-brand-dark transition-colors disabled:opacity-50"
                >
                  {uploadingResume ? 'Uploading...' : 'Upload'}
                </button>
              )}
            </div>
          </div>

          {/* Skills */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 mb-6">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight mb-6 flex items-center gap-2">
              <Target className="text-brand-accent" size={20} /> Skills
            </h2>
            
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                placeholder="Add a skill (e.g., Python, React)"
                className="flex-1 bg-brand-bg border border-slate-200 rounded-2xl py-4 px-6 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
              />
              <button
                onClick={handleAddSkill}
                className="bg-brand-dark text-white px-6 py-4 rounded-2xl hover:bg-brand-accent transition-colors"
              >
                <Plus size={20} />
              </button>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill, index) => (
                <span key={index} className="px-4 py-2 bg-brand-bg text-brand-dark rounded-xl font-bold text-sm border border-slate-200 flex items-center gap-2">
                  {skill}
                  <button onClick={() => handleRemoveSkill(skill)} className="text-red-500 hover:text-red-700">
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Experience Level */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 mb-6">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight mb-6 flex items-center gap-2">
              <Briefcase className="text-brand-accent" size={20} /> Experience
            </h2>
            
            <select
              value={profile.experience_level}
              onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
              className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 px-6 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none"
            >
              <option value="entry">Entry Level (0-1 years)</option>
              <option value="mid">Mid Level (2-5 years)</option>
              <option value="senior">Senior Level (5+ years)</option>
            </select>
          </div>

          {/* Career Goals */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 mb-6">
            <h2 className="text-xl font-black text-brand-dark uppercase tracking-tight mb-6">Career Goals</h2>
            <textarea
              value={profile.career_goals}
              onChange={(e) => setProfile({ ...profile, career_goals: e.target.value })}
              placeholder="What are your career aspirations?"
              className="w-full bg-brand-bg border border-slate-200 rounded-2xl py-4 px-6 font-medium focus:ring-2 focus:ring-brand-accent focus:border-transparent outline-none resize-none"
              rows={4}
            />
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-brand-dark text-white py-5 rounded-2xl font-black uppercase tracking-widest hover:bg-brand-accent transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Save size={20} />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </main>
    </div>
  );
};

export default Settings;
