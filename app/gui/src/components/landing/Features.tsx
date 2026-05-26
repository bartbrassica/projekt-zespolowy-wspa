import React from 'react';
import { useTranslation } from 'react-i18next';
import type { FeaturesProps } from '../../types/landing';

const Features: React.FC<FeaturesProps> = ({ features, hoveredFeature, onFeatureHover }) => {
  const { t } = useTranslation();

  return (
    <section className="relative py-12 sm:py-16 md:py-20 lg:py-24 xl:py-32 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24">
      <div className="w-full max-w-[1800px] mx-auto">
        <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-center mb-8 sm:mb-12 md:mb-16 lg:mb-20 xl:mb-24">
          {t('landing.securitySimplifiedTitle')} <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">{t('landing.securitySimplifiedHighlight')}</span>
        </h2>

        <div className="grid lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8 lg:gap-10 xl:gap-12">
          {features.map((feature: any, i: number) => (
            <div
              key={i}
              onMouseEnter={() => onFeatureHover(i)}
              onMouseLeave={() => onFeatureHover(null)}
              className="group relative p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-2xl bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 hover:border-purple-500 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20 cursor-pointer"
            >
              <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-300`}></div>
              <div className="relative z-10">
                <div className={`mb-4 sm:mb-6 md:mb-8 inline-flex p-2 sm:p-3 md:p-4 lg:p-5 bg-gradient-to-br ${feature.color} rounded-xl transition-all duration-300 ${hoveredFeature === i ? 'scale-110 rotate-12' : ''}`}>
                  <feature.icon className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 lg:w-10 lg:h-10 xl:w-12 xl:h-12" />
                </div>
                <h3 className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-2 sm:mb-3 md:mb-4">{t(feature.titleKey)}</h3>
                <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl text-gray-400">{t(feature.descKey)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;