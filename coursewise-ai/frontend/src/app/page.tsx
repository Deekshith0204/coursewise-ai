'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, BookOpen, Layers, ShieldCheck, Files, Plus } from 'lucide-react';
import UploadBox from '../components/UploadBox';
import FileCollectionList from '../components/FileCollectionList';
import SummaryConfiguration from '../components/SummaryConfiguration';
import ProcessingStatus, { ProcessingStep } from '../components/ProcessingStatus';
import SummaryViewer from '../components/SummaryViewer';
import ErrorMessage from '../components/ErrorMessage';
import {
  DocumentInfo,
  KnowledgeLevel,
  SummaryDepth,
  LearningPreference,
  SummaryResponse,
} from '../types';
import { api } from '../services/api';

export default function DashboardPage() {
  // Document collection state
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [processingMap, setProcessingMap] = useState<Record<string, string>>({});
  const [isUploading, setIsUploading] = useState(false);

  // Configuration state
  const [knowledgeLevel, setKnowledgeLevel] = useState<KnowledgeLevel>('INTERMEDIATE');
  const [summaryDepth, setSummaryDepth] = useState<SummaryDepth>('STANDARD');
  const [learningPreference, setLearningPreference] = useState<LearningPreference>('CONCEPT FOCUSED');

  // Generation & progress state
  const [processingStep, setProcessingStep] = useState<ProcessingStep>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Result state
  const [summaryResult, setSummaryResult] = useState<SummaryResponse | null>(null);

  // Load existing workspace documents on mount
  useEffect(() => {
    const loadExistingDocs = async () => {
      try {
        const docs = await api.listDocuments();
        if (docs && docs.length > 0) {
          setDocuments(docs);
          setSelectedDocIds(docs.map((d) => d.id));
        }
      } catch (err) {
        console.warn('Could not load existing documents:', err);
      }
    };
    loadExistingDocs();
  }, []);

  // Handle successful file uploads
  const handleUploadSuccess = async (
    items: {
      document_id: string;
      filename: string;
      file_type: string;
      page_count: number;
      slide_count: number;
      section_count: number;
      file_size: number;
    }[]
  ) => {
    setErrorMessage(null);
    setSummaryResult(null);

    // Create preliminary document items
    const newDocs: DocumentInfo[] = items.map((item) => ({
      id: item.document_id,
      filename: item.filename,
      original_filename: item.filename,
      file_type: item.file_type as any,
      file_size: item.file_size,
      page_count: item.page_count,
      slide_count: item.slide_count,
      section_count: item.section_count,
      title: item.filename,
      status: 'uploaded',
      created_at: new Date().toISOString(),
    }));

    setDocuments((prev) => {
      const existingIds = new Set(prev.map((d) => d.id));
      const filtered = newDocs.filter((d) => !existingIds.has(d.id));
      return [...filtered, ...prev];
    });

    setSelectedDocIds((prev) => {
      const addedIds = newDocs.map((d) => d.id);
      return Array.from(new Set([...prev, ...addedIds]));
    });

    // Auto-trigger backend document processing pipeline for each file
    for (const item of items) {
      setProcessingMap((prev) => ({
        ...prev,
        [item.document_id]: 'Extracting & Chunking...',
      }));

      try {
        await api.processDocument(item.document_id);
        const refreshed = await api.getDocument(item.document_id);
        setDocuments((prev) =>
          prev.map((d) => (d.id === item.document_id ? refreshed : d))
        );
        setProcessingMap((prev) => ({
          ...prev,
          [item.document_id]: 'Ready',
        }));
      } catch (err: any) {
        setProcessingMap((prev) => ({
          ...prev,
          [item.document_id]: 'Failed',
        }));
        setErrorMessage(
          `Failed to process '${item.filename}': ${err.message || 'Error occurred'}`
        );
      }
    }
  };

  // Toggle selection for a single document
  const handleToggleSelect = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  // Toggle all documents selection
  const handleSelectAll = () => {
    if (selectedDocIds.length === documents.length) {
      setSelectedDocIds([]);
    } else {
      setSelectedDocIds(documents.map((d) => d.id));
    }
  };

  // Remove a document from collection
  const handleRemoveDocument = async (id: string) => {
    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      setSelectedDocIds((prev) => prev.filter((item) => item !== id));
      setProcessingMap((prev) => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to remove document.');
    }
  };

  // Generate Personalized Summary (Single or Multi-Document)
  const handleGenerateSummary = async () => {
    if (selectedDocIds.length === 0) {
      setErrorMessage('Please select at least one document to summarize.');
      return;
    }

    // Check if any selected documents are still processing
    const stillProcessing = selectedDocIds.some((id) => {
      const status = processingMap[id];
      return status && status !== 'Ready' && status !== 'Failed';
    });

    if (stillProcessing) {
      setErrorMessage('Please wait for document indexing to finish before generating the summary.');
      return;
    }

    setErrorMessage(null);
    setIsGenerating(true);
    setProcessingStep('generating');

    const isMulti = selectedDocIds.length > 1;
    setStatusMessage(
      isMulti
        ? `Synthesizing multi-document summary across ${selectedDocIds.length} technical files (${knowledgeLevel.toLowerCase()}, ${summaryDepth.toLowerCase()})...`
        : `Generating personalized ${knowledgeLevel.toLowerCase()} summary (${summaryDepth.toLowerCase()})...`
    );

    try {
      const stepTimer = setTimeout(() => {
        setProcessingStep('preparing');
        setStatusMessage(
          'Synthesizing document-wise breakdowns and verifying source traceability...'
        );
      }, 3500);

      const result = await api.generateSummary(
        selectedDocIds,
        knowledgeLevel,
        summaryDepth,
        learningPreference
      );

      clearTimeout(stepTimer);
      setSummaryResult(result);
      setProcessingStep('idle');
    } catch (err: any) {
      setProcessingStep('idle');
      setErrorMessage(err.message || 'Failed to generate personalized summary.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto space-y-3 pt-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Multi-Format Technical Learning Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          CourseWise <span className="text-blue-600">AI</span>
        </h1>
        <p className="text-base sm:text-lg font-medium text-slate-600">
          AI-Based Personalized Course Content Summarizer
        </p>
        <p className="text-sm text-slate-500 max-w-2xl mx-auto leading-relaxed">
          Upload dense technical course materials in <strong>PDF, Word (DOCX), PowerPoint (PPTX), or Plain Text (TXT)</strong> to generate adaptive, source-traceable summaries tailored to your learning style.
        </p>
      </div>

      {/* Error alert */}
      {errorMessage && (
        <div className="max-w-4xl mx-auto">
          <ErrorMessage
            message={errorMessage}
            onRetry={selectedDocIds.length > 0 ? handleGenerateSummary : undefined}
          />
        </div>
      )}

      {/* Stepped Processing Status Banner */}
      {processingStep !== 'idle' && (
        <div className="max-w-4xl mx-auto">
          <ProcessingStatus
            currentStep={processingStep}
            statusMessage={statusMessage}
          />
        </div>
      )}

      {/* Main Flow: Upload & Collections -> Configuration -> Results */}
      {!summaryResult ? (
        <div className="max-w-4xl mx-auto space-y-6">
          {documents.length === 0 ? (
            /* Empty State: Prominent Multi-File Dropzone */
            <div className="space-y-6">
              <UploadBox
                onUploadSuccess={handleUploadSuccess}
                onError={(msg) => setErrorMessage(msg)}
                isUploading={isUploading}
              />
            </div>
          ) : (
            /* Active Workspace: File Collection + Add More + Configuration */
            <div className="space-y-6">
              <FileCollectionList
                documents={documents}
                selectedDocIds={selectedDocIds}
                onToggleSelect={handleToggleSelect}
                onSelectAll={handleSelectAll}
                onRemove={handleRemoveDocument}
                processingMap={processingMap}
              />

              {/* Compact Add-More Dropzone */}
              <UploadBox
                onUploadSuccess={handleUploadSuccess}
                onError={(msg) => setErrorMessage(msg)}
                isUploading={isUploading}
                compact={true}
              />

              {/* Personalization Options & Generate Action */}
              <SummaryConfiguration
                knowledgeLevel={knowledgeLevel}
                onKnowledgeLevelChange={setKnowledgeLevel}
                summaryDepth={summaryDepth}
                onSummaryDepthChange={setSummaryDepth}
                learningPreference={learningPreference}
                onLearningPreferenceChange={setLearningPreference}
                onGenerate={handleGenerateSummary}
                isGenerating={isGenerating}
                disabled={
                  processingStep !== 'idle' ||
                  selectedDocIds.length === 0 ||
                  selectedDocIds.some(
                    (id) =>
                      processingMap[id] &&
                      processingMap[id] !== 'Ready' &&
                      processingMap[id] !== 'Failed'
                  )
                }
              />
            </div>
          )}

          {/* Academic Features Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-6 border-t border-slate-200/80">
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-blue-50 text-blue-600 mt-0.5">
                <BookOpen className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-xs">Multi-File Processing</h4>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Extracts structured content from PDF, DOCX, PPTX, and TXT files.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600 mt-0.5">
                <Files className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-xs">Cross-Document Synthesis</h4>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Synthesizes overall summaries plus document-wise breakdown cards.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-purple-50 text-purple-600 mt-0.5">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-xs">Adaptive Personalization</h4>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Calibrates terminology for Beginner, Intermediate, and Advanced learners.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600 mt-0.5">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-xs">Source Traceability</h4>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  Precise references to Page X, Slide X, Section X, or Lines X-Y.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Summary Result View */
        <div className="max-w-5xl mx-auto space-y-6">
          <SummaryViewer
            summary={summaryResult}
            onReconfigure={() => setSummaryResult(null)}
          />
        </div>
      )}
    </div>
  );
}
