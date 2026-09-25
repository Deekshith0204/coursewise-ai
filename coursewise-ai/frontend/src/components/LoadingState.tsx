import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  subtext?: string;
}

export default function LoadingState({
  message = 'Loading content...',
  subtext = 'Please wait a moment.',
}: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl border border-slate-200 shadow-sm text-center">
      <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl mb-4 animate-spin">
        <Loader2 className="w-8 h-8" />
      </div>
      <h3 className="font-semibold text-slate-800 text-base">{message}</h3>
      {subtext && <p className="text-xs text-slate-500 mt-1 max-w-sm">{subtext}</p>}
    </div>
  );
}
