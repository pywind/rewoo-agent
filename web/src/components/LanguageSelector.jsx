import React, { useContext, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { LanguageContext } from '../context/LanguageContext.jsx';
import { SUPPORTED_LANGUAGES } from '../locales';

const LanguageSelector = () => {
  const { language, setLanguage } = useContext(LanguageContext);
  const [isOpen, setIsOpen] = useState(false);

  const currentLanguage = SUPPORTED_LANGUAGES.find(lang => lang.code === language);

  const handleSelect = (langCode) => {
    setLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
      >
        <span className="text-sm font-medium text-gray-700">
          {currentLanguage?.label || 'English'}
        </span>
        <ChevronDown 
          size={16} 
          className={`text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          {SUPPORTED_LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleSelect(lang.code)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-blue-50 transition-colors first:rounded-t-lg last:rounded-b-lg
                ${language === lang.code ? 'bg-blue-100 text-blue-900 font-medium' : 'text-gray-700'}`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      )}

      {/* Backdrop to close dropdown */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default LanguageSelector;
