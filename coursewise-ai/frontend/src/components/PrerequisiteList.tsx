import React from 'react';
import { CheckSquare, ArrowRight, HelpCircle } from 'lucide-react';
import { PrerequisiteItem } from '../types';

interface PrerequisiteListProps {
  prerequisites: PrerequisiteItem[];
}

export default function PrerequisiteList({ prerequisites }: PrerequisiteListProps) {
  if (!prerequisites || prerequisites.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-slate-500 text-sm">
        No specific prerequisites flagged for this technical material.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 text-xs">
        <HelpCircle className="w-4 h-4 flex-shrink-0 text-amber-600" />
        <p>
          Mastering these foundational prerequisites before diving into advanced topics significantly boosts comprehension.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {prerequisites.map((prereq, idx) => (
          <div
            key={prereq.id || idx}
            className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-indigo-200 transition-all"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                {prereq.topic}
              </span>

              {prereq.source_pages && prereq.source_pages.length > 0 && (
                <span className="text-[11px] text-slate-400">
                  Ref Page {prereq.source_pages.join(', ')}
                </span>
              )}
            </div>

            <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2 mt-1">
              <CheckSquare className="w-4 h-4 text-indigo-600" />
              {prereq.name}
            </h4>

            <div className="mt-2 text-xs text-slate-600 flex items-start gap-1.5 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
              <span>
                <strong className="text-slate-700 font-semibold">Why it's needed:</strong> {prereq.reason}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
