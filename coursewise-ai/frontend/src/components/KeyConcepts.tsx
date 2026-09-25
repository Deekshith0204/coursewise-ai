import React from 'react';
import { Lightbulb, Bookmark } from 'lucide-react';
import { ConceptItem } from '../types';

interface KeyConceptsProps {
  concepts: ConceptItem[];
}

export default function KeyConcepts({ concepts }: KeyConceptsProps) {
  if (!concepts || concepts.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-slate-500 text-sm">
        No key concepts extracted for this section.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {concepts.map((concept, idx) => (
        <div
          key={concept.id || idx}
          className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition-all flex flex-col justify-between"
        >
          <div>
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600 border border-amber-200">
                  <Lightbulb className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-slate-900 text-sm">
                  {concept.name}
                </h4>
              </div>

              {concept.source_pages && concept.source_pages.length > 0 && (
                <span className="flex-shrink-0 inline-flex items-center gap-1 text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200">
                  <Bookmark className="w-3 h-3" />
                  {concept.source_pages.length === 1
                    ? `Page ${concept.source_pages[0]}`
                    : `Pages ${concept.source_pages.join(', ')}`}
                </span>
              )}
            </div>

            <p className="text-xs text-slate-600 leading-relaxed mt-2">
              {concept.explanation}
            </p>
          </div>

          {concept.importance_score ? (
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
              <span>Importance Weight</span>
              <span className="font-semibold text-slate-600">
                {Math.round(concept.importance_score * 100)}%
              </span>
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
