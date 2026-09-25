import React from 'react';
import { GraduationCap, Award, Compass } from 'lucide-react';
import { KnowledgeLevel } from '../types';

interface KnowledgeLevelSelectorProps {
  value: KnowledgeLevel;
  onChange: (level: KnowledgeLevel) => void;
  disabled?: boolean;
}

export default function KnowledgeLevelSelector({ value, onChange, disabled }: KnowledgeLevelSelectorProps) {
  const levels: { id: KnowledgeLevel; title: string; desc: string; icon: any }[] = [
    {
      id: 'BEGINNER',
      title: 'Beginner',
      desc: 'Simple analogies, demystified jargon, foundational concepts explained.',
      icon: Compass,
    },
    {
      id: 'INTERMEDIATE',
      title: 'Intermediate',
      desc: 'Balanced technical vocabulary, structural links & system mechanisms.',
      icon: GraduationCap,
    },
    {
      id: 'ADVANCED',
      title: 'Advanced',
      desc: 'Rigorous technical depth, mathematical & algorithmic nuances.',
      icon: Award,
    },
  ];

  return (
    <div>
      <label className="block text-sm font-bold text-slate-800 mb-2">
        Knowledge Level
      </label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {levels.map((lvl) => {
          const Icon = lvl.icon;
          const isSelected = value === lvl.id;
          return (
            <button
              key={lvl.id}
              type="button"
              disabled={disabled}
              onClick={() => onChange(lvl.id)}
              className={`p-4 rounded-xl text-left border transition-all ${
                isSelected
                  ? 'border-blue-600 bg-blue-50/70 shadow-sm ring-1 ring-blue-600'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
              } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className={`font-semibold text-sm ${isSelected ? 'text-blue-900' : 'text-slate-800'}`}>
                  {lvl.title}
                </span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                {lvl.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
