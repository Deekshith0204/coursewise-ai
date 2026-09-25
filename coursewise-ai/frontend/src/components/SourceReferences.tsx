import React from 'react';
import { BookMarked, Quote } from 'lucide-react';
import { SummarySourceItem } from '../types';
import FileTypeBadge from './FileTypeBadge';

interface SourceReferencesProps {
  sources: SummarySourceItem[];
}

export default function SourceReferences({ sources }: SourceReferencesProps) {
  if (!sources || sources.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200 text-slate-500 text-sm">
        Source mapping unavailable.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 p-3.5 bg-blue-50/60 rounded-xl border border-blue-200 text-blue-950 text-xs">
        <BookMarked className="w-4 h-4 text-blue-700 flex-shrink-0" />
        <p>
          Traceable passages extracted directly from the uploaded course materials supporting this summary.
        </p>
      </div>

      <div className="space-y-3">
        {sources.map((src, idx) => {
          const location = src.source_location || (src.page_number ? `Page ${src.page_number}` : 'Reference');
          const hasDocName = Boolean(src.document_name);

          return (
            <div
              key={src.chunk_id || idx}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-slate-300 transition-all text-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2">
                  <FileTypeBadge fileType={src.source_type} size="sm" />
                  <span className="font-bold text-slate-900">
                    {hasDocName ? `${src.document_name} — ` : ''}
                    <span className="text-blue-700 font-semibold">{location}</span>
                  </span>
                </div>

                {src.section_name && src.section_name !== location && (
                  <span className="text-[11px] text-slate-500 font-medium line-clamp-1">
                    {src.section_name}
                  </span>
                )}
              </div>

              <div className="flex items-start gap-2.5 bg-slate-50 p-3 rounded-lg text-slate-700 border border-slate-100 font-mono text-[11px] leading-relaxed">
                <Quote className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
                <p className="italic">{src.snippet}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
