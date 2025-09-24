import enTranslations from './en.json';
import viTranslations from './vi.json';
import jpTranslations from './jp.json';

export const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'vi', label: 'Tiếng Việt' },
  { code: 'jp', label: '日本語' }
];

export const DEFAULT_LANGUAGE = 'en';

export const TRANSLATIONS = {
  en: enTranslations,
  vi: viTranslations,
  jp: jpTranslations,
};
