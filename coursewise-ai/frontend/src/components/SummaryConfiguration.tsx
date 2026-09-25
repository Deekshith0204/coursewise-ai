import React from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import { KnowledgeLevel, SummaryDepth, LearningPreference } from '../types';
import KnowledgeLevelSelector from './KnowledgeLevelSelector';
import SummaryDepthSelector from './SummaryDepthSelector';
import LearningPreferenceSelector from './LearningPreferenceSelector';

interface SummaryConfigurationProps {
  knowledgeLevel: KnowledgeLevel;
  onKnowledgeLevelChange: (level: KnowledgeLevel) => void;
  summaryDepth: SummaryDepth;
  onSummaryDepthChange: (depth: SummaryDepth) => void;
  learningPreference: LearningPreference;
  onLearningPreferenceChange: (pref: LearningPreference) => void;
  onGenerate: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}

export default function SummaryConfiguration({
  knowledgeLevel,
  onKnowledgeLevelChange,
  summaryDepth,
  onSummaryDepthChange,
  learningPreference,
  onLearningPreferenceChange,
  onGenerate,
  isGenerating,
  disabled,
}: SummaryConfigurationProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-8">
      <div>
        <h3 className="text-lg font-bold text-slate-900">Personalization Configuration</h3>
        <p className="text-xs text-slate-500 mt-1">
          Customize how the AI synthesizes and explains the dense technical material for your current study needs.
        </p>
      </div>

      <div className="space-y-6">
        <KnowledgeLevelSelector
          value={knowledgeLevel}
          onChange={onKnowledgeLevelChange}
          disabled={disabled || isGenerating}
        />

        <SummaryDepthSelector
          value={summaryDepth}
          onChange={onSummaryDepthChange}
          disabled={disabled || isGenerating}
        />

        <LearningPreferenceSelector
          value={learningPreference}
          onChange={onLearningPreferenceChange}
          disabled={disabled || isGenerating}
        />
      </div>

      <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-slate-400">
          Source page traceability &amp; hallucination controls are enforced across all levels.
        </p>

        <button
          onClick={onGenerate}
          disabled={disabled || isGenerating}
          className={`w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl font-semibold text-sm text-white shadow-md transition-all ${
            disabled || isGenerating
              ? 'bg-slate-400 cursor-not-allowed shadow-none'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg hover:scale-[1.01]'
          }`}
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Generating Personalized Summary...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate Personalized Summary</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
