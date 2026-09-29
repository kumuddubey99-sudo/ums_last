import React from 'react';
import { Language } from '../translations';

interface Props {
  isDark: boolean;
  onSelectLanguage: (lang: Language) => void;
}

export const LanguageSelect: React.FC<Props> = ({ isDark, onSelectLanguage }) => {
  const languages: { code: Language; label: string; sub: string }[] = [
    { code: 'English', label: 'English', sub: 'Default' },
    { code: 'Hindi', label: 'हिंदी', sub: 'Hindi' },
    { code: 'Marathi', label: 'मराठी', sub: 'Marathi' },
    { code: 'Malwari', label: 'मारवाड़ी / राजस्थानी', sub: 'Rajasthani' },
  ];

  return (
    <div className={`min-h-screen flex items-center justify-center p-4 ${isDark ? 'bg-[#121212]' : 'bg-[#F5F7FA]'}`}>
      <div className={`w-full max-w-sm rounded-lg border p-8 shadow-sm text-center ${
        isDark ? 'bg-[#1E1E1E] border-[#333333]' : 'bg-white border-[#E0E0E0]'
      }`}>
        <div className="text-xs font-semibold uppercase tracking-wider text-[#1565C0] mb-1">
          Nav Durga Super Market
        </div>
        <h1 className={`text-xl font-bold mb-1 ${isDark ? 'text-white' : 'text-neutral-900'}`}>
          Udhaar Management System
        </h1>
        <p className={`text-sm mb-6 ${isDark ? 'text-neutral-400' : 'text-neutral-600'}`}>
          Select Language / भाषा चुनें
        </p>

        <div className="space-y-3">
          {languages.map((l) => (
            <button
              key={l.code}
              onClick={() => onSelectLanguage(l.code)}
              className="w-full flex items-center justify-between px-4 py-3 rounded text-sm font-semibold bg-[#1565C0] text-white hover:bg-[#0D47A1] transition-colors"
            >
              <span>{l.label}</span>
              <span className="text-xs opacity-80">{l.sub}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
