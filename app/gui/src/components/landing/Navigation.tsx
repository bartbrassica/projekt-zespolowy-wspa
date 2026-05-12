import React from 'react';
import type { NavigationProps } from '../../types/landing';

const Navigation: React.FC<NavigationProps> = ({ onLogin }) => {
  return (
    <nav className="relative z-50 w-full">
      <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24 py-4 md:py-6 lg:py-8">
        <div className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
          DigitaLockbox
        </div>

        <button
          onClick={onLogin}
          className="group relative px-4 py-2 sm:px-6 sm:py-3 md:px-8 md:py-4 lg:px-10 lg:py-5 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50"
        >
          <span className="relative z-10">Login</span>
          <div className="absolute inset-0 bg-gradient-to-r from-purple-700 to-cyan-700 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </button>
      </div>
    </nav>
  );
};

export default Navigation;