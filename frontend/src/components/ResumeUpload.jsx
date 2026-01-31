import React, { useState, useCallback } from 'react';
import { Upload, File, X, Check, AlertCircle } from 'lucide-react';
import { resumeAPI } from '../services/api';

const ResumeUpload = ({ onUploadSuccess, onUploadError, className = '' }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success' | 'error' | null
  const [errorMessage, setErrorMessage] = useState('');

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (file) => {
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setErrorMessage('Please upload a PDF or Word document');
      setUploadStatus('error');
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      setErrorMessage('File size should be less than 5MB');
      setUploadStatus('error');
      return;
    }

    setFile(file);
    setErrorMessage('');
    setUploadStatus(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await resumeAPI.upload(formData);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');
      
      onUploadSuccess?.(response.data);
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(error.response?.data?.message || 'Upload failed. Please try again.');
      onUploadError?.(error);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setUploadStatus(null);
    setErrorMessage('');
    setUploadProgress(0);
  };

  return (
    <div className={`${className}`}>
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
          isDragging
            ? 'border-blue-500 bg-blue-500/10'
            : uploadStatus === 'success'
              ? 'border-green-500 bg-green-500/10'
              : uploadStatus === 'error'
                ? 'border-red-500 bg-red-500/10'
                : 'border-white/20 hover:border-white/40 bg-white/5'
        }`}
      >
        {!file ? (
          <>
            <Upload className={`mx-auto mb-4 ${isDragging ? 'text-blue-400' : 'text-gray-400'}`} size={48} />
            <p className="text-white font-medium mb-2">
              Drag and drop your resume here
            </p>
            <p className="text-gray-400 text-sm mb-4">
              or click to browse (PDF, DOC, DOCX - Max 5MB)
            </p>
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${
                uploadStatus === 'success' ? 'bg-green-500/20' :
                uploadStatus === 'error' ? 'bg-red-500/20' : 'bg-blue-500/20'
              }`}>
                {uploadStatus === 'success' ? (
                  <Check className="text-green-400" size={24} />
                ) : uploadStatus === 'error' ? (
                  <AlertCircle className="text-red-400" size={24} />
                ) : (
                  <File className="text-blue-400" size={24} />
                )}
              </div>
              <div className="text-left">
                <p className="text-white font-medium">{file.name}</p>
                <p className="text-gray-400 text-sm">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-2 hover:bg-white/10 rounded-lg transition"
            >
              <X className="text-gray-400 hover:text-white" size={20} />
            </button>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {uploading && (
        <div className="mt-4">
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-gray-400 text-sm mt-2">Uploading... {uploadProgress}%</p>
        </div>
      )}

      {/* Error Message */}
      {errorMessage && (
        <p className="mt-4 text-red-400 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          {errorMessage}
        </p>
      )}

      {/* Upload Button */}
      {file && !uploading && uploadStatus !== 'success' && (
        <button
          onClick={handleUpload}
          className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition"
        >
          Upload Resume
        </button>
      )}

      {/* Success Message */}
      {uploadStatus === 'success' && (
        <p className="mt-4 text-green-400 text-sm flex items-center gap-2">
          <Check size={16} />
          Resume uploaded successfully!
        </p>
      )}
    </div>
  );
};

export default ResumeUpload;
