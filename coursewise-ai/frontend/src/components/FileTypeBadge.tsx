import React from 'react';
import { FileText, Presentation, FileCode, AlignLeft } from 'lucide-react';

interface FileTypeBadgeProps {
  fileType: string;
  size?: 'sm' | 'md';
}

export default function FileTypeBadge({ fileType, size = 'sm' }: FileTypeBadgeProps) {
  const t = (fileType || '').toLowerCase();

  if (t === 'pdf') {
    return (
      <span className={`inline-flex items-center gap-1 font-bold rounded uppercase tracking-wider ${
        size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
      } bg-red-50 text-red-700 border border-red-200`}>
        <FileText className={size === 'sm' ? 'w-3 h-3 text-red-600' : 'w-3.5 h-3.5 text-red-600'} />
        PDF
      </span>
    );
  }

  if (t === 'docx' || t === 'doc' || t === 'word') {
    return (
      <span className={`inline-flex items-center gap-1 font-bold rounded uppercase tracking-wider ${
        size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
      } bg-blue-50 text-blue-700 border border-blue-200`}>
        <FileText className={size === 'sm' ? 'w-3 h-3 text-blue-600' : 'w-3.5 h-3.5 text-blue-600'} />
        WORD
      </span>
    );
  }

  if (t === 'pptx' || t === 'ppt' || t === 'powerpoint') {
    return (
      <span className={`inline-flex items-center gap-1 font-bold rounded uppercase tracking-wider ${
        size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
      } bg-amber-50 text-amber-800 border border-amber-300`}>
        <Presentation className={size === 'sm' ? 'w-3 h-3 text-amber-600' : 'w-3.5 h-3.5 text-amber-600'} />
        PPTX
      </span>
    );
  }

  if (t === 'txt' || t === 'text') {
    return (
      <span className={`inline-flex items-center gap-1 font-bold rounded uppercase tracking-wider ${
        size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
      } bg-slate-100 text-slate-700 border border-slate-300`}>
        <AlignLeft className={size === 'sm' ? 'w-3 h-3 text-slate-500' : 'w-3.5 h-3.5 text-slate-500'} />
        TXT
      </span>
    );
  }

  if (t === 'md' || t === 'markdown') {
    return (
      <span className={`inline-flex items-center gap-1 font-bold rounded uppercase tracking-wider ${
        size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
      } bg-purple-50 text-purple-700 border border-purple-200`}>
        <FileCode className={size === 'sm' ? 'w-3 h-3 text-purple-600' : 'w-3.5 h-3.5 text-purple-600'} />
        MD
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1 font-bold rounded uppercase tracking-wider ${
      size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-1 text-xs'
    } bg-slate-100 text-slate-600 border border-slate-200`}>
      <FileText className="w-3 h-3" />
      {fileType.toUpperCase()}
    </span>
  );
}
