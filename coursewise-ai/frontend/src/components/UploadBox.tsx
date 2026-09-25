'use client';

import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Loader2, Plus } from 'lucide-react';
import { api } from '../services/api';

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.txt', '.md'];

interface UploadBoxProps {
  onUploadSuccess: (
    items: {
      document_id: string;
      filename: string;
      file_type: string;
      page_count: number;
      slide_count: number;
      section_count: number;
      file_size: number;
    }[]
  ) => void;
  onError: (errorMessage: string) => void;
  isUploading: boolean;
  compact?: boolean;
}

export default function UploadBox({ onUploadSuccess, onError, isUploading, compact = false }: UploadBoxProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFiles(Array.from(e.target.files));
    }
  };

  const validateAndProcessFiles = async (files: File[]) => {
    const validFiles: File[] = [];

    for (const file of files) {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        onError(`Unsupported file type '${ext}'. Please upload PDF, DOCX, PPTX, or TXT.`);
        return;
      }

      if (file.size === 0) {
        onError(`'${file.name}' is empty (0 bytes).`);
        return;
      }

      if (file.size > 50 * 1024 * 1024) {
        onError(`'${file.name}' exceeds the 50MB maximum limit.`);
        return;
      }

      validFiles.push(file);
    }

    if (validFiles.length === 0) return;

    try {
      const results = await api.uploadDocuments(validFiles);
      onUploadSuccess(results);
    } catch (err: any) {
      onError(err.message || 'Failed to upload course materials.');
    }
  };

  if (compact) {
    return (
      <div
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className="flex items-center justify-center gap-2 p-3.5 border-2 border-dashed border-slate-300 hover:border-blue-400 bg-slate-50 hover:bg-blue-50/50 rounded-xl cursor-pointer transition-colors text-xs font-semibold text-slate-700"
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.pptx,.txt,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation,text/plain"
          className="hidden"
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <Plus className="w-4 h-4 text-blue-600" />
        <span>Add More Course Materials (PDF, DOCX, PPTX, TXT)</span>
      </div>
    );
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-10 text-center transition-all duration-200 ${
        isDragOver
          ? 'border-blue-500 bg-blue-50/70 scale-[1.01]'
          : 'border-slate-300 hover:border-blue-400 bg-slate-50/60 hover:bg-slate-50'
      } ${isUploading ? 'opacity-70 pointer-events-none' : ''}`}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.pptx,.txt,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation,text/plain"
        className="hidden"
        onChange={handleFileChange}
        disabled={isUploading}
      />

      <div className="flex flex-col items-center justify-center">
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-colors ${
          isDragOver ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'
        }`}>
          {isUploading ? (
            <Loader2 className="w-8 h-8 animate-spin" />
          ) : (
            <UploadCloud className="w-8 h-8" />
          )}
        </div>

        <h3 className="text-xl font-bold text-slate-900 mb-1">
          {isUploading ? 'Uploading & Validating Materials...' : 'Upload Course Material'}
        </h3>
        
        <p className="text-sm text-slate-600 mb-3">
          Upload PDF, Word, PowerPoint, or text files
        </p>

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="mb-4 px-6 py-2.5 rounded-xl font-semibold text-xs bg-white border border-slate-300 hover:border-blue-500 hover:bg-blue-50/50 text-slate-800 shadow-sm transition-all"
        >
          Choose Files
        </button>

        <p className="text-xs text-slate-400 mb-4">
          Drag and drop files here (select single or multiple files)
        </p>

        {/* Supported Format Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 text-xs font-semibold">
          <span className="px-2.5 py-1 rounded-md bg-red-50 text-red-700 border border-red-200">
            PDF
          </span>
          <span className="text-slate-300">•</span>
          <span className="px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
            DOCX
          </span>
          <span className="text-slate-300">•</span>
          <span className="px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-300">
            PPTX
          </span>
          <span className="text-slate-300">•</span>
          <span className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 border border-slate-300">
            TXT
          </span>
        </div>
      </div>
    </div>
  );
}
