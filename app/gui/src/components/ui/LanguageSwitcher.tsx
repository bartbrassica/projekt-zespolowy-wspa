import React from 'react';
import { useTranslation } from 'react-i18next';
import { Languages } from 'lucide-react';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const currentLanguage = i18n.language || 'en';

  const toggleLanguage = () => {
    const newLanguage = currentLanguage === 'en' ? 'pl' : 'en';
    i18n.changeLanguage(newLanguage);
  };

  const languageLabel = currentLanguage === 'en' ? 'EN' : 'PL';

  return (
    <button
      onClick={toggleLanguage}
      className="group relative flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-2 bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:border-purple-500 transition-all duration-300 hover:scale-105"
      aria-label="Switch language"
    >
      <Languages className="h-4 w-4 sm:h-5 sm:w-5" />
      <span className="font-semibold">{languageLabel}</span>
      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-cyan-600/10 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    </button>
  );
};

export default LanguageSwitcher;
