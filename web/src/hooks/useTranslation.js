import { useContext } from 'react';
import { LanguageContext } from '../context/LanguageContext.jsx';

export const useTranslation = () => {
  const { translations } = useContext(LanguageContext);
  return (key) => translations[key] || key;
};
