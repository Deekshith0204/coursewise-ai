'use client';

import React, { useState } from 'react';
import {
  BookOpen,
  Lightbulb,
  CheckSquare,
  BookMarked,
  BarChart3,
  Copy,
  Check,
  Download,
  RefreshCw,
  Star,
  Layers,
  GraduationCap,
  Target,
  Clock,
  FolderKanban,
} from 'lucide-react';
import { SummaryResponse } from '../types';
import KeyConcepts from './KeyConcepts';
import PrerequisiteList from './PrerequisiteList';
import SourceReferences from './SourceReferences';
import FileTypeBadge from './FileTypeBadge';
import { api } from '../services/api';

interface SummaryViewerProps {
  summary: SummaryResponse;
  onReconfigure: () => void;
}

export default function SummaryViewer({ summary, onReconfigure }: SummaryViewerProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'concepts' | 'prerequisites' | 'sources' | 'evaluation'>('summary');
  const [copied, setCopied] = useState(false);
  const [rating, setRating] = useState<number | null>(summary.evaluation?.user_rating || null);
  const [ratingSaved, setRatingSaved] = useState(false);

  const handleCopy = () => {
    let fullText = `# ${summary.title}\n\n`;
    fullText += `*Knowledge Level: ${summary.knowledge_level} | Depth: ${summary.summary_depth} | Preference: ${summary.learning_preference}*\n\n`;
    fullText += `## Executive Overview\n${summary.overview}\n\n`;

    if (summary.document_wise_summaries && summary.document_wise_summaries.length > 0) {
      fullText += `## Document-Wise Summaries\n`;
      summary.document_wise_summaries.forEach((d, idx) => {
        fullText += `### Document ${idx + 1}: ${d.document_name} (${d.file_type.toUpperCase()})\n${d.summary}\n\n`;
      });
    }
    
    if (summary.key_points && summary.key_points.length > 0) {
      fullText += `## Important Points\n` + summary.key_points.map((p) => `- ${p}`).join('\n') + '\n\n';
    }

    if (summary.sections && summary.sections.length > 0) {
      summary.sections.forEach((sec) => {
        const pages = sec.source_pages?.length ? ` (Ref: ${sec.source_pages.join(', ')})` : '';
        fullText += `### ${sec.heading}${pages}\n${sec.content}\n\n`;
      });
    }

    if (summary.key_concepts && summary.key_concepts.length > 0) {
      fullText += `## Key Concepts\n` + summary.key_concepts.map((c) => `- **${c.name}**: ${c.explanation}`).join('\n') + '\n\n';
    }

    if (summary.prerequisites && summary.prerequisites.length > 0) {
      fullText += `## Prerequisites\n` + summary.prerequisites.map((p) => `- **${p.name}** (${p.topic}): ${p.reason}`).join('\n') + '\n\n';
    }

    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    let md = `# ${summary.title}\n\n`;
    md += `*Document(s): ${summary.document_title}*\n`;
    md += `*Generated: ${new Date(summary.created_at).toLocaleString()}*\n`;
    md += `*Level: ${summary.knowledge_level} | Depth: ${summary.summary_depth} | Preference: ${summary.learning_preference}*\n\n`;
    md += `## Executive Overview\n\n${summary.overview}\n\n`;

    if (summary.document_wise_summaries && summary.document_wise_summaries.length > 0) {
      md += `## Document-Wise Breakdown\n\n`;
      summary.document_wise_summaries.forEach((d, idx) => {
        md += `### ${idx + 1}. ${d.document_name} (${d.file_type.toUpperCase()})\n\n${d.summary}\n\n`;
      });
    }

    if (summary.key_points?.length) {
      md += `## Important Points\n\n` + summary.key_points.map((p) => `* ${p}`).join('\n') + '\n\n';
    }

    if (summary.sections?.length) {
      summary.sections.forEach((s) => {
        md += `### ${s.heading}\n\n${s.content}\n\n`;
      });
    }

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${summary.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_summary.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleRate = async (score: number) => {
    setRating(score);
    try {
      await api.rateSummary(summary.id, score);
      setRatingSaved(true);
      setTimeout(() => setRatingSaved(false), 3000);
    } catch (e) {
      console.error('Failed to save rating:', e);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header bar */}
      <div className="p-6 md:p-8 border-b border-slate-200 bg-slate-50/50">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                <GraduationCap className="w-3 h-3" />
                {summary.knowledge_level}
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800">
                <Layers className="w-3 h-3" />
                {summary.summary_depth}
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                <Target className="w-3 h-3" />
                {summary.learning_preference}
              </span>
              {summary.file_types?.map((ft) => (
                <FileTypeBadge key={ft} fileType={ft} size="sm" />
              ))}
              {summary.response_time_ms ? (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs text-slate-500 font-mono">
                  <Clock className="w-3 h-3" />
                  {(summary.response_time_ms / 1000).toFixed(1)}s
                </span>
              ) : null}
            </div>

            <h2 className="text-xl md:text-2xl font-bold text-slate-900 leading-tight">
              {summary.title}
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Source Collection: <span className="font-semibold text-slate-700">{summary.document_title}</span>
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
              title="Copy formatted summary to clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>

            <button
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
              title="Download as Markdown"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
            </button>

            <button
              onClick={onReconfigure}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-100 transition-colors shadow-sm"
              title="Change configuration or select different files"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reconfigure</span>
            </button>
          </div>
        </div>

        {/* Tab navigation */}
        <div className="flex items-center gap-2 overflow-x-auto mt-6 border-b border-slate-200 pb-px">
          {[
            { id: 'summary', label: 'Summary', icon: BookOpen, count: summary.sections?.length },
            { id: 'concepts', label: 'Key Concepts', icon: Lightbulb, count: summary.key_concepts?.length },
            { id: 'prerequisites', label: 'Prerequisites', icon: CheckSquare, count: summary.prerequisites?.length },
            { id: 'sources', label: 'Source References', icon: BookMarked, count: summary.sources?.length },
            { id: 'evaluation', label: 'Evaluation Metrics', icon: BarChart3 },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2.5 font-semibold text-xs rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
                  isActive
                    ? 'border-blue-600 text-blue-700 bg-white font-bold'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-100/60'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                    isActive ? 'bg-blue-100 text-blue-800' : 'bg-slate-200 text-slate-600'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab content area */}
      <div className="p-6 md:p-8">
        {activeTab === 'summary' && (
          <div className="space-y-8 max-w-4xl">
            {/* Overview Card */}
            <div className="p-6 rounded-2xl bg-blue-50/50 border border-blue-100">
              <h3 className="font-bold text-slate-900 text-base mb-2">Overall Synthesis</h3>
              <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-line">
                {summary.overview}
              </p>
            </div>

            {/* Document-wise Summaries (for multi-file collections) */}
            {summary.document_wise_summaries && summary.document_wise_summaries.length > 0 && (
              <div className="space-y-4 pt-2">
                <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <FolderKanban className="w-4 h-4 text-blue-600" />
                  Document-Wise Summary Breakdown
                </h3>
                <div className="space-y-4">
                  {summary.document_wise_summaries.map((d, idx) => (
                    <div
                      key={idx}
                      className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-all"
                    >
                      <div className="flex items-center gap-2 mb-2.5 pb-2.5 border-b border-slate-100">
                        <span className="font-bold text-[11px] text-slate-400">DOCUMENT {idx + 1}:</span>
                        <FileTypeBadge fileType={d.file_type} size="sm" />
                        <span className="font-bold text-sm text-slate-900">{d.document_name}</span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                        {d.summary}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Important Points */}
            {summary.key_points && summary.key_points.length > 0 && (
              <div>
                <h3 className="font-bold text-slate-900 text-base mb-3 flex items-center gap-2">
                  <CheckSquare className="w-4 h-4 text-emerald-600" />
                  Important Points &amp; Takeaways
                </h3>
                <div className="grid grid-cols-1 gap-2.5">
                  {summary.key_points.map((pt, i) => (
                    <div
                      key={i}
                      className="p-3.5 rounded-xl border border-slate-200 bg-white text-xs text-slate-700 flex items-start gap-2.5 shadow-sm"
                    >
                      <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 font-bold flex items-center justify-center flex-shrink-0 text-[11px]">
                        {i + 1}
                      </span>
                      <span className="leading-relaxed mt-0.5">{pt}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sections */}
            <div className="space-y-6 pt-4 border-t border-slate-100">
              <h3 className="font-bold text-slate-900 text-base">
                Structured Topic Breakdown
              </h3>
              {summary.sections?.map((sec, idx) => (
                <div
                  key={idx}
                  className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:border-slate-300 transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-bold text-slate-900 text-base">
                      {sec.heading}
                    </h4>
                    {sec.source_pages && sec.source_pages.length > 0 && (
                      <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        Refs: {sec.source_pages.join(', ')}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                    {sec.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'concepts' && (
          <KeyConcepts concepts={summary.key_concepts || []} />
        )}

        {activeTab === 'prerequisites' && (
          <PrerequisiteList prerequisites={summary.prerequisites || []} />
        )}

        {activeTab === 'sources' && (
          <SourceReferences sources={summary.sources || []} />
        )}

        {activeTab === 'evaluation' && (
          <div className="space-y-6 max-w-3xl">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Academic Evaluation Metrics</h3>
              <p className="text-xs text-slate-500 mt-1">
                Quantitative metrics computed across the {summary.document_ids?.length || 1} course document(s).
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-5 rounded-xl border border-slate-200 bg-slate-50">
                <span className="text-xs text-slate-500">Compression Ratio</span>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {summary.evaluation?.compression_ratio
                    ? `${(summary.evaluation.compression_ratio * 100).toFixed(1)}%`
                    : 'N/A'}
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Summary / Source word volume
                </span>
              </div>

              <div className="p-5 rounded-xl border border-slate-200 bg-slate-50">
                <span className="text-xs text-slate-500">Source Word Count</span>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {summary.evaluation?.source_word_count?.toLocaleString() || 'N/A'}
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Total words across materials
                </span>
              </div>

              <div className="p-5 rounded-xl border border-slate-200 bg-slate-50">
                <span className="text-xs text-slate-500">Summary Word Count</span>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {summary.evaluation?.summary_word_count?.toLocaleString() || 'N/A'}
                </p>
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Synthesized words produced
                </span>
              </div>
            </div>

            {/* Usefulness Rating */}
            <div className="p-6 rounded-xl border border-slate-200 bg-white">
              <h4 className="font-bold text-slate-900 text-sm mb-1">Rate Educational Usefulness</h4>
              <p className="text-xs text-slate-500 mb-4">
                Did this multi-document summary align with your selected level ({summary.knowledge_level})?
              </p>

              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => handleRate(star)}
                    className="p-1 text-slate-300 hover:text-amber-500 transition-colors"
                  >
                    <Star
                      className={`w-6 h-6 ${
                        rating && rating >= star ? 'text-amber-400 fill-amber-400' : ''
                      }`}
                    />
                  </button>
                ))}
                {ratingSaved && (
                  <span className="text-xs text-emerald-600 font-semibold ml-3">
                    Feedback recorded!
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
