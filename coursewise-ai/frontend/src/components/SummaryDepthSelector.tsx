import React from 'react';
import { Zap, BookOpen, Layers } from 'lucide-react';
import { SummaryDepth } from '../types';

interface SummaryDepthSelectorProps {
  value: SummaryDepth;
  onChange: (depth: SummaryDepth) => void;
  disabled?: boolean;
}

export default function SummaryDepthSelector({ value, onChange, disabled }: SummaryDepthSelectorProps) {
  const depths: { id: SummaryDepth; title: string; desc: string; icon: any }[] = [
    {
      id: 'QUICK',
      title: 'Quick',
      desc: 'Concise executive summary, primary takeaways, and high-level ideas.',
      icon: Zap,
    },
    {
      id: 'STANDARD',
      title: 'Standard',
      desc: 'Section-wise explanation, core concepts, relationships & prerequisites.',
      icon: BookOpen,
    },
    {
      id: 'DETAILED',
      title: 'Detailed',
      desc: 'In-depth section breakdown, definitions, examples & exhaustive references.',
      icon: Layers,
    },
  ];

  return (
    <div>
      <label className="block text-sm font-bold text-slate-800 mb-2">
        Summary Depth
      </label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {depths.map((d) => {
          const Icon = d.icon;
          const isSelected = value === d.id;
          return (
            <button
              key={d.id}
              type="button"
              disabled={disabled}
              onClick={() => onChange(d.id)}
              className={`p-4 rounded-xl text-left border transition-all ${
                isSelected
                  ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-1 ring-indigo-600'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
              } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className={`font-semibold text-sm ${isSelected ? 'text-indigo-900' : 'text-slate-800'}`}>
                  {d.title}
                </span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                {d.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
