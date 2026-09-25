import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

export type ProcessingStep =
  | 'idle'
  | 'uploading'
  | 'extracting'
  | 'cleaning'
  | 'chunking'
  | 'analyzing'
  | 'prerequisites'
  | 'generating'
  | 'preparing'
  | 'completed'
  | 'error';

interface ProcessingStatusProps {
  currentStep: ProcessingStep;
  statusMessage?: string;
}

const STEPS = [
  { id: 'uploading', label: 'Uploading document...' },
  { id: 'extracting', label: 'Extracting text & preserving pages...' },
  { id: 'cleaning', label: 'Cleaning headers & formatting structure...' },
  { id: 'chunking', label: 'Creating semantic chunks & embeddings...' },
  { id: 'analyzing', label: 'Analyzing technical concepts...' },
  { id: 'prerequisites', label: 'Detecting prerequisites...' },
  { id: 'generating', label: 'Generating personalized summary...' },
  { id: 'preparing', label: 'Preparing results...' },
];

export default function ProcessingStatus({ currentStep, statusMessage }: ProcessingStatusProps) {
  if (currentStep === 'idle' || currentStep === 'completed') {
    return null;
  }

  const currentStepIndex = STEPS.findIndex((s) => s.id === currentStep);
  const progressPercent = Math.min(
    100,
    Math.max(10, Math.round(((currentStepIndex + 1) / STEPS.length) * 100))
  );

  return (
    <div className="bg-white rounded-2xl border border-blue-100 p-6 md:p-8 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-base font-bold text-slate-900">
            Processing Document
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            {statusMessage || (currentStepIndex >= 0 ? STEPS[currentStepIndex].label : 'Processing...')}
          </p>
        </div>
        <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
          {progressPercent}% Complete
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mb-6">
        <div
          className="bg-gradient-to-r from-blue-600 to-indigo-600 h-full rounded-full transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Steps List */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {STEPS.map((step, idx) => {
          const isDone = currentStepIndex > idx;
          const isCurrent = currentStepIndex === idx;

          return (
            <div
              key={step.id}
              className={`p-3 rounded-xl border text-xs flex items-center gap-2.5 transition-colors ${
                isDone
                  ? 'border-emerald-200 bg-emerald-50/50 text-emerald-800'
                  : isCurrent
                  ? 'border-blue-400 bg-blue-50/80 text-blue-900 font-semibold ring-1 ring-blue-300'
                  : 'border-slate-100 bg-slate-50/60 text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-blue-600 animate-spin flex-shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-slate-300 flex-shrink-0" />
              )}
              <span className="line-clamp-1">{step.label.replace('...', '')}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
