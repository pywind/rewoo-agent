import React, { createContext, useState, useEffect } from 'react';
import { DEFAULT_LANGUAGE, TRANSLATIONS } from '../locales';

export const LanguageContext = createContext({
  language: DEFAULT_LANGUAGE,
  setLanguage: () => {},
  translations: {},
});

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(DEFAULT_LANGUAGE);
  const [translations, setTranslations] = useState(TRANSLATIONS[DEFAULT_LANGUAGE] || {});

  useEffect(() => {
    setTranslations(TRANSLATIONS[language] || {});
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, translations }}>
      {children}
    </LanguageContext.Provider>
  );
};
