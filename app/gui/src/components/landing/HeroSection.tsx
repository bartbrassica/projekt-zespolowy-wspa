import React from 'react';
import { Shield } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { HeroSectionProps } from '../../types/landing';
import { getPasswordStrengthColor } from '../../utils/landingUtils';

const HeroSection: React.FC<HeroSectionProps> = ({
  mousePosition,
  typedText,
  passwordInput,
  passwordStrength,
  onPasswordChange,
  onGetStarted
}) => {
  const { t } = useTranslation();

  const getPasswordStrengthText = (strength: number): string => {
    if (strength < 40) return t('landing.weakPassword');
    if (strength < 70) return t('landing.mediumPassword');
    return t('landing.strongPassword');
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24">
      <div className="w-full max-w-[1800px] mx-auto text-center pt-16 sm:pt-20 md:pt-24 lg:pt-28">
        <div className="mb-6 sm:mb-8 md:mb-10 lg:mb-12 xl:mb-16 inline-flex items-center justify-center" style={{ perspective: '1000px' }}>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full blur-2xl opacity-50 animate-pulse"></div>
            <Shield
              className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 lg:w-32 lg:h-32 xl:w-40 xl:h-40 2xl:w-48 2xl:h-48 text-white relative z-10 transition-transform duration-200 ease-out"
              style={{
                transform: `translate(${mousePosition.x * 30}px, ${mousePosition.y * 30}px) rotateY(${mousePosition.x * 15}deg) rotateX(${-mousePosition.y * 15}deg)`
              }}
            />
          </div>
        </div>

        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl 2xl:text-8xl font-bold mb-4 sm:mb-6 md:mb-8 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
          {t('common.brandName')}
        </h1>

        <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl 2xl:text-5xl mb-4 sm:mb-6 md:mb-8 text-gray-300 h-8 sm:h-10 md:h-12 lg:h-14">
          {typedText}
          <span className="animate-pulse">|</span>
        </p>

        <p className="text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl 2xl:text-4xl mb-6 sm:mb-8 md:mb-10 lg:mb-12 text-gray-400 max-w-4xl mx-auto">
          {t('landing.heroSubtitle')}
        </p>

        {/* Interactive Password Strength Demo */}
        <div className="max-w-lg md:max-w-xl lg:max-w-2xl xl:max-w-3xl mx-auto mb-6 sm:mb-8 md:mb-10 lg:mb-12">
          <div className="relative">
            <input
              type="password"
              value={passwordInput}
              onChange={(e) => onPasswordChange(e.target.value)}
              placeholder={t('landing.passwordPlaceholder')}
              className="w-full px-4 py-3 sm:px-6 sm:py-4 md:px-8 md:py-5 lg:px-10 lg:py-6 xl:px-12 xl:py-7 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl bg-gray-900 bg-opacity-50 border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-all duration-300"
            />
            <div className="absolute left-0 right-0 -bottom-2 h-1 bg-gray-800 rounded-full overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${getPasswordStrengthColor(passwordStrength)} transition-all duration-300`}
                style={{ width: `${passwordStrength}%` }}
              />
            </div>
            {passwordInput && (
              <div className="absolute -bottom-8 sm:-bottom-10 md:-bottom-12 left-1/2 transform -translate-x-1/2 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl">
                <span className={`text-${passwordStrength < 40 ? 'red' : passwordStrength < 70 ? 'yellow' : 'green'}-400`}>
                  {getPasswordStrengthText(passwordStrength)} Password
                </span>
              </div>
            )}
          </div>
        </div>

        <button
          onClick={onGetStarted}
          className="group relative px-6 py-3 sm:px-8 sm:py-4 md:px-10 md:py-5 lg:px-12 lg:py-6 xl:px-14 xl:py-7 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50 mt-8 sm:mt-10 md:mt-12 lg:mt-16"
        >
          <span className="relative z-10">{t('landing.getStarted')}</span>
          <div className="absolute inset-0 bg-gradient-to-r from-purple-700 to-cyan-700 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </button>
      </div>
    </section>
  );
};

export default HeroSection;