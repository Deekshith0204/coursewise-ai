'use client';

import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, CheckCircle2, AlertCircle, RefreshCw, Key, Server, Cpu, ExternalLink } from 'lucide-react';
import { api } from '../../services/api';
import { HealthResponse, AIConfigInfo } from '../../types';
import ErrorMessage from '../../components/ErrorMessage';
import LoadingState from '../../components/LoadingState';

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [config, setConfig] = useState<AIConfigInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, c] = await Promise.all([api.getHealth(), api.getConfig()]);
      setHealth(h);
      setConfig(c);
    } catch (err: any) {
      setError('Unable to connect to the CourseWise AI backend API. Please ensure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const h = await api.getHealth();
      setHealth(h);
      if (h.ai_configured) {
        setTestResult('Success: Backend is healthy and AI provider is properly configured!');
      } else {
        setTestResult('Notice: Backend is healthy, but AI_API_KEY is not yet set in backend/.env.');
      }
    } catch (err: any) {
      setTestResult(`Error: Could not reach backend: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return <LoadingState message="Checking system & AI configuration..." />;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-blue-50 text-blue-700">
            <SettingsIcon className="w-5 h-5" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">System &amp; AI Configuration</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Inspect connection status, LLM integration settings, and environment configuration.
        </p>
      </div>

      {error && <ErrorMessage message={error} onRetry={loadSettings} />}

      {/* Backend & AI Connection Status Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Backend &amp; AI Integration Status</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Live telemetry reported from FastAPI backend server
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleTestConnection}
              disabled={testing}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${testing ? 'animate-spin' : ''}`} />
              <span>Test Connection</span>
            </button>
          </div>
        </div>

        {testResult && (
          <div className={`p-3.5 rounded-xl border text-xs font-medium ${
            testResult.startsWith('Success')
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : testResult.startsWith('Notice')
              ? 'bg-amber-50 text-amber-800 border-amber-200'
              : 'bg-red-50 text-red-800 border-red-200'
          }`}>
            {testResult}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-start gap-3">
            <div className="p-2 rounded-lg bg-blue-100 text-blue-700 mt-0.5">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-slate-500">FastAPI Backend Status</span>
              <p className="font-bold text-slate-900 text-sm mt-0.5 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                Online &amp; Healthy (v{health?.version || '1.0.0'})
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">
                Database: SQLite (data/coursewise.db)
              </span>
            </div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-start gap-3">
            <div className={`p-2 rounded-lg mt-0.5 ${
              config?.configured ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
            }`}>
              <Key className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-slate-500">AI Provider Key</span>
              <p className={`font-bold text-sm mt-0.5 flex items-center gap-1.5 ${
                config?.configured ? 'text-emerald-700' : 'text-amber-700'
              }`}>
                {config?.configured ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Configured ({config.masked_key})
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-amber-600" />
                    Not Configured
                  </>
                )}
              </p>
              <span className="text-[11px] text-slate-400 mt-1 block">
                Model: {config?.model || 'gemini-1.5-flash'}
              </span>
            </div>
          </div>
        </div>

        {/* Configuration details table */}
        <div className="rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-100 text-slate-600 font-semibold border-b border-slate-200">
              <tr>
                <th className="p-3">Setting</th>
                <th className="p-3">Current Active Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr>
                <td className="p-3 font-semibold text-slate-700">AI Provider</td>
                <td className="p-3 font-mono text-slate-600">{config?.provider || 'openai'}</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-700">Target Model</td>
                <td className="p-3 font-mono text-slate-600">{config?.model || 'gemini-1.5-flash'}</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-700">Base URL</td>
                <td className="p-3 font-mono text-slate-600">{config?.base_url || 'https://generativelanguage.googleapis.com/v1beta/openai'}</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-slate-700">Vector Index</td>
                <td className="p-3 text-slate-600">Local Dense Vectorizer (Hashing + Cosine Similarity)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Guide on setting .env */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-900 text-base">How to Configure AI Providers</h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Create or edit the <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono text-blue-700 font-semibold">backend/.env</code> file in your project.
          CourseWise AI uses standard OpenAI-compatible endpoints, which work directly with Google Gemini, OpenAI, Groq, Ollama, and OpenRouter!
        </p>

        <div className="space-y-4 pt-2">
          {/* Option 1: Google Gemini */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
            <span className="font-bold text-slate-900 text-xs flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-600 inline-block" />
              Option 1: Google Gemini (Recommended)
            </span>
            <pre className="p-3 rounded-lg bg-slate-900 text-slate-100 text-xs font-mono overflow-x-auto">
{`AI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-1.5-flash
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
AI_PROVIDER=openai`}
            </pre>
          </div>

          {/* Option 2: OpenAI */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
            <span className="font-bold text-slate-900 text-xs flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-600 inline-block" />
              Option 2: OpenAI
            </span>
            <pre className="p-3 rounded-lg bg-slate-900 text-slate-100 text-xs font-mono overflow-x-auto">
{`AI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-4o-mini
AI_BASE_URL=https://api.openai.com/v1
AI_PROVIDER=openai`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
