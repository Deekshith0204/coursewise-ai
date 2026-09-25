import React from 'react';
import { FileText, Calendar, Trash2, ArrowUpRight, GraduationCap, Layers, Target, Files } from 'lucide-react';
import { SummaryHistoryItem } from '../types';
import FileTypeBadge from './FileTypeBadge';

interface HistoryCardProps {
  item: SummaryHistoryItem;
  onView: (id: string) => void;
  onDelete: (id: string) => void;
  isDeleting?: boolean;
}

export default function HistoryCard({ item, onView, onDelete, isDeleting }: HistoryCardProps) {
  const formattedDate = new Date(item.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 hover:shadow-md transition-all">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-2 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {item.is_multi_document ? (
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
                  <Files className="w-3 h-3" />
                  Multi-Doc ({item.file_types?.length || 'Multiple'})
                </span>
                {item.file_types?.map((ft) => (
                  <FileTypeBadge key={ft} fileType={ft} size="sm" />
                ))}
              </div>
            ) : (
              <FileTypeBadge fileType={item.file_type || 'pdf'} size="sm" />
            )}
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
              <GraduationCap className="w-3 h-3" />
              {item.knowledge_level}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-200">
              <Layers className="w-3 h-3" />
              {item.summary_depth}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-full border border-purple-200">
              <Target className="w-3 h-3" />
              {item.learning_preference}
            </span>
          </div>

          <h3 className="font-bold text-slate-900 text-base leading-snug">
            {item.title}
          </h3>

          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1 font-medium text-slate-700">
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              {item.document_name}
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              {formattedDate}
            </span>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 self-end sm:self-center">
          <button
            onClick={() => onView(item.id)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors border border-blue-200"
          >
            <span>View</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => onDelete(item.id)}
            disabled={isDeleting}
            className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 border border-slate-200 hover:border-red-200 transition-colors"
            title="Delete summary"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
