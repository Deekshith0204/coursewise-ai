import React from 'react';
import { Target, FileCheck, Wrench } from 'lucide-react';
import { LearningPreference } from '../types';

interface LearningPreferenceSelectorProps {
  value: LearningPreference;
  onChange: (pref: LearningPreference) => void;
  disabled?: boolean;
}

export default function LearningPreferenceSelector({
  value,
  onChange,
  disabled,
}: LearningPreferenceSelectorProps) {
  const preferences: { id: LearningPreference; title: string; desc: string; icon: any }[] = [
    {
      id: 'CONCEPT FOCUSED',
      title: 'Concept Focused',
      desc: 'Emphasize architectural intuition, theoretical models, and fundamental principles.',
      icon: Target,
    },
    {
      id: 'EXAM FOCUSED',
      title: 'Exam Focused',
      desc: 'Emphasize high-yield definitions, comparisons, key formulas, and distinctions.',
      icon: FileCheck,
    },
    {
      id: 'PRACTICAL FOCUSED',
      title: 'Practical Focused',
      desc: 'Emphasize concrete workflows, real-world examples, and applied implementations.',
      icon: Wrench,
    },
  ];

  return (
    <div>
      <label className="block text-sm font-bold text-slate-800 mb-2">
        Learning Preference
      </label>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {preferences.map((pref) => {
          const Icon = pref.icon;
          const isSelected = value === pref.id;
          return (
            <button
              key={pref.id}
              type="button"
              disabled={disabled}
              onClick={() => onChange(pref.id)}
              className={`p-4 rounded-xl text-left border transition-all ${
                isSelected
                  ? 'border-purple-600 bg-purple-50/70 shadow-sm ring-1 ring-purple-600'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
              } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-purple-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className={`font-semibold text-sm ${isSelected ? 'text-purple-900' : 'text-slate-800'}`}>
                  {pref.title}
                </span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                {pref.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
