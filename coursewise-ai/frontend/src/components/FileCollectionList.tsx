import React from 'react';
import { Trash2, CheckCircle2, RefreshCw, AlertCircle, Layers, FileText } from 'lucide-react';
import { DocumentInfo } from '../types';
import FileTypeBadge from './FileTypeBadge';

interface FileCollectionListProps {
  documents: DocumentInfo[];
  selectedDocIds: string[];
  onToggleSelect: (id: string) => void;
  onSelectAll: () => void;
  onRemove: (id: string) => void;
  processingMap: Record<string, string>; // docId -> status string e.g. "Extracting...", "Embedding...", "Ready"
}

export default function FileCollectionList({
  documents,
  selectedDocIds,
  onToggleSelect,
  onSelectAll,
  onRemove,
  processingMap,
}: FileCollectionListProps) {
  if (documents.length === 0) return null;

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getUnitDetail = (doc: DocumentInfo) => {
    const t = (doc.file_type || '').toLowerCase();
    if (t === 'pptx' || t === 'ppt') {
      return `${doc.slide_count || doc.page_count || 1} slides`;
    }
    if (t === 'docx' || t === 'doc') {
      return `${doc.section_count || doc.page_count || 1} sections`;
    }
    if (t === 'txt' || t === 'text' || t === 'md') {
      return `${doc.section_count || 1} line blocks`;
    }
    return `${doc.page_count || 1} pages`;
  };

  const getStatusBadge = (doc: DocumentInfo) => {
    const currentStatus = processingMap[doc.id] || (doc.status === 'processed' ? 'Ready' : doc.status);

    if (currentStatus === 'Ready' || doc.status === 'processed') {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          Ready
        </span>
      );
    }

    if (doc.status === 'error' || currentStatus === 'Failed') {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
          <AlertCircle className="w-3 h-3 text-red-600" />
          Failed
        </span>
      );
    }

    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200 animate-pulse">
        <RefreshCw className="w-3 h-3 animate-spin" />
        {currentStatus}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-base">
            MY COURSE MATERIAL ({documents.length})
          </h3>
          <p className="text-xs text-slate-500">
            Select files to summarize individually or combine into a multi-document synthesis.
          </p>
        </div>

        <button
          onClick={onSelectAll}
          className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
        >
          {selectedDocIds.length === documents.length ? 'Deselect All' : 'Select All'}
        </button>
      </div>

      <div className="divide-y divide-slate-100">
        {documents.map((doc) => {
          const isSelected = selectedDocIds.includes(doc.id);

          return (
            <div
              key={doc.id}
              className={`py-3.5 px-3 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors ${
                isSelected ? 'bg-blue-50/40' : 'hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggleSelect(doc.id)}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer"
                />

                <div>
                  <div className="flex items-center gap-2">
                    <FileTypeBadge fileType={doc.file_type} size="sm" />
                    <span className="font-bold text-slate-800 text-sm line-clamp-1">
                      {doc.original_filename}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-[11px] text-slate-500 mt-1">
                    <span>{formatSize(doc.file_size)}</span>
                    <span>•</span>
                    <span>{getUnitDetail(doc)}</span>
                    {doc.chunks_count ? (
                      <>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Layers className="w-3 h-3 text-slate-400" />
                          {doc.chunks_count} chunks
                        </span>
                      </>
                    ) : null}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 self-end sm:self-center">
                {getStatusBadge(doc)}

                <button
                  type="button"
                  onClick={() => onRemove(doc.id)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                  title="Remove from collection"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
