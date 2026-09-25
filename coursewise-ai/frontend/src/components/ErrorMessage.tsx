import React from 'react';
import { AlertCircle, Key, RefreshCw } from 'lucide-react';
import Link from 'next/link';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  title?: string;
}

export default function ErrorMessage({ message, onRetry, title = 'An error occurred' }: ErrorMessageProps) {
  const isAiConfigError = message.toLowerCase().includes('ai provider not configured') || message.toLowerCase().includes('ai_api_key');

  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-900 shadow-sm animate-fade-in">
      <div className="flex items-start gap-3.5">
        <div className="p-2 rounded-lg bg-red-100 text-red-600 mt-0.5">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-red-950 text-base">{title}</h3>
          <p className="mt-1 text-sm text-red-800 leading-relaxed">{message}</p>

          {isAiConfigError && (
            <div className="mt-4 p-3.5 rounded-lg bg-white border border-red-200 text-slate-800 text-xs">
              <div className="flex items-center gap-2 font-semibold text-slate-900 mb-1">
                <Key className="w-4 h-4 text-amber-600" />
                How to configure your AI provider:
              </div>
              <p className="text-slate-600 mb-2">
                Open <code className="bg-slate-100 px-1.5 py-0.5 rounded text-blue-700 font-mono">backend/.env</code> and set your <code className="bg-slate-100 px-1.5 py-0.5 rounded text-blue-700 font-mono">AI_API_KEY</code>.
              </p>
              <Link
                href="/settings"
                className="inline-flex items-center gap-1.5 text-blue-700 font-medium hover:underline text-xs"
              >
                Go to Settings Page →
              </Link>
            </div>
          )}

          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3.5 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-red-300 text-red-800 hover:bg-red-100 transition-colors shadow-sm"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
