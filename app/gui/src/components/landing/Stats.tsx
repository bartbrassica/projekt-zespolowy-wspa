import React from 'react';
import type { StatsProps } from '../../types/landing';

const Stats: React.FC<StatsProps> = ({ animatedStats }) => {
  return (
    <section id="stats-section" data-animate className="relative py-12 sm:py-16 md:py-20 lg:py-24 xl:py-32 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24 bg-gradient-to-b from-transparent via-purple-900/20 to-transparent">
      <div className="w-full max-w-[1800px] mx-auto">
        <div className="grid sm:grid-cols-3 gap-4 sm:gap-6 md:gap-8 lg:gap-10 xl:gap-12">
          <div className="text-center p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-2xl bg-gradient-to-br from-purple-900/30 to-cyan-900/30 backdrop-blur-sm border border-purple-700/50 hover:border-purple-500 transition-all duration-500 hover:scale-105">
            <p className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl 2xl:text-8xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent mb-2 sm:mb-3 md:mb-4">
              {animatedStats.breaches}%
            </p>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl text-gray-400">of breaches involve weak passwords</p>
          </div>
          <div className="text-center p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-2xl bg-gradient-to-br from-purple-900/30 to-cyan-900/30 backdrop-blur-sm border border-purple-700/50 hover:border-purple-500 transition-all duration-500 hover:scale-105">
            <p className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl 2xl:text-8xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent mb-2 sm:mb-3 md:mb-4">
              {animatedStats.reuse}%
            </p>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl text-gray-400">of people reuse passwords</p>
          </div>
          <div className="text-center p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-2xl bg-gradient-to-br from-purple-900/30 to-cyan-900/30 backdrop-blur-sm border border-purple-700/50 hover:border-purple-500 transition-all duration-500 hover:scale-105">
            <p className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl 2xl:text-8xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent mb-2 sm:mb-3 md:mb-4">
              {animatedStats.time}s
            </p>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl text-gray-400">to crack a 6-character password</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Stats;