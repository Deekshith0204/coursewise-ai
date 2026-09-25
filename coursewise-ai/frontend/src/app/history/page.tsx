'use client';

import React, { useEffect, useState } from 'react';
import { History as HistoryIcon, ArrowLeft, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import Link from 'next/link';
import HistoryCard from '../../components/HistoryCard';
import SummaryViewer from '../../components/SummaryViewer';
import LoadingState from '../../components/LoadingState';
import ErrorMessage from '../../components/ErrorMessage';
import { SummaryHistoryItem, SummaryResponse } from '../../types';
import { api } from '../../services/api';

export default function HistoryPage() {
  const [historyList, setHistoryList] = useState<SummaryHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected summary detail view
  const [selectedSummary, setSelectedSummary] = useState<SummaryResponse | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHistory();
      setHistoryList(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load summary history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleView = async (summaryId: string) => {
    setLoadingDetail(true);
    setError(null);
    try {
      const data = await api.getSummary(summaryId);
      setSelectedSummary(data);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      setError(err.message || 'Failed to load summary details.');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleDelete = async (summaryId: string) => {
    if (!confirm('Are you sure you want to delete this summary from your history?')) {
      return;
    }

    setDeletingId(summaryId);
    try {
      await api.deleteSummary(summaryId);
      setHistoryList((prev) => prev.filter((item) => item.id !== summaryId));
      if (selectedSummary?.id === summaryId) {
        setSelectedSummary(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete summary.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-blue-50 text-blue-700">
              <HistoryIcon className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Summary History</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Access, review, and export all previously generated course material summaries.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {selectedSummary ? (
            <button
              onClick={() => setSelectedSummary(null)}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to History List</span>
            </button>
          ) : (
            <button
              onClick={fetchHistory}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          )}

          <Link
            href="/"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Summary</span>
          </Link>
        </div>
      </div>

      {/* Error alert */}
      {error && <ErrorMessage message={error} onRetry={fetchHistory} />}

      {/* Detail View */}
      {selectedSummary && !loadingDetail ? (
        <div className="space-y-4 animate-fade-in">
          <SummaryViewer
            summary={selectedSummary}
            onReconfigure={() => setSelectedSummary(null)}
          />
        </div>
      ) : loadingDetail ? (
        <LoadingState message="Loading summary details..." subtext="Retrieving saved sections and source citations." />
      ) : loading ? (
        <LoadingState message="Loading summary history..." subtext="Accessing your database records." />
      ) : historyList.length === 0 ? (
        /* Empty State */
        <div className="text-center py-16 px-4 bg-white rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
            <HistoryIcon className="w-8 h-8" />
          </div>
          <div>
            <h3 className="font-bold text-slate-800 text-lg">No summaries yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              Upload a technical PDF document to generate your first personalized learning summary.
            </p>
          </div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-xs bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-sm"
          >
            <Sparkles className="w-4 h-4" />
            <span>Go to Summarizer</span>
          </Link>
        </div>
      ) : (
        /* History Items List */
        <div className="space-y-3">
          {historyList.map((item) => (
            <HistoryCard
              key={item.id}
              item={item}
              onView={handleView}
              onDelete={handleDelete}
              isDeleting={deletingId === item.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
