import React, { useState } from 'react';
import { Upload, FileText, Check, X, Loader2 } from 'lucide-react';
import api from '../services/api';

const ResumeUploadModal = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [parsedData, setParsedData] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.pdf')) {
        setError('Only PDF files are allowed');
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('File size should be less than 5MB');
        return;
      }
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const result = await api.uploadResume(file);
      
      if (result.error) {
        setError(result.error);
      } else {
        setSuccess(true);
        setParsedData(result.parsed_data);
        
        // Update local storage with new skills
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        currentUser.skills = result.parsed_data?.skills || [];
        localStorage.setItem('user', JSON.stringify(currentUser));
        
        // Call success callback after 2 seconds
        setTimeout(() => {
          onSuccess?.(result.parsed_data);
          onClose();
        }, 2000);
      }
    } catch (err) {
      setError('Failed to upload resume. Please try again.');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleSkip = () => {
    // Allow skip but warn user
    if (window.confirm('Without a resume, you won\'t get personalized job matches. Are you sure?')) {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-lg p-8 shadow-2xl">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FileText className="text-blue-600" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Upload Your Resume</h2>
          <p className="text-gray-500 mt-2">
            Upload your resume to get AI-powered job matches based on your skills
          </p>
        </div>

        {!success ? (
          <>
            {/* Upload Area */}
            <div 
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                file 
                  ? 'border-green-400 bg-green-50' 
                  : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              {file ? (
                <div className="flex items-center justify-center gap-3">
                  <Check className="text-green-500" size={24} />
                  <span className="font-medium text-gray-700">{file.name}</span>
                  <button 
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <X size={20} />
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer block">
                  <Upload className="mx-auto text-gray-400 mb-3" size={40} />
                  <p className="text-gray-600 font-medium">Click to upload PDF resume</p>
                  <p className="text-gray-400 text-sm mt-1">Max file size: 5MB</p>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                {error}
              </div>
            )}

            {/* Buttons */}
            <div className="mt-6 flex gap-3">
              <button
                onClick={handleSkip}
                className="flex-1 py-3 px-4 border border-gray-200 rounded-xl text-gray-600 font-medium hover:bg-gray-50 transition"
              >
                Skip for now
              </button>
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Upload size={20} />
                    Upload & Analyze
                  </>
                )}
              </button>
            </div>
          </>
        ) : (
          /* Success State */
          <div className="text-center py-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="text-green-600" size={32} />
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Resume Analyzed!</h3>
            
            {parsedData?.skills?.length > 0 && (
              <div className="mt-4">
                <p className="text-gray-600 mb-3">We found {parsedData.skills.length} skills:</p>
                <div className="flex flex-wrap justify-center gap-2">
                  {parsedData.skills.slice(0, 10).map((skill, i) => (
                    <span 
                      key={i} 
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                  {parsedData.skills.length > 10 && (
                    <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                      +{parsedData.skills.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}
            
            <p className="text-green-600 mt-4 text-sm">Redirecting to dashboard...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUploadModal;
