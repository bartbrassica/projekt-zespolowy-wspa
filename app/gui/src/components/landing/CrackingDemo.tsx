import React from 'react';
import { AlertTriangle, XCircle, Shield, Sparkles, Lock, Key } from 'lucide-react';
import type { CrackingDemoProps } from '../../types/landing';

const CrackingDemo: React.FC<CrackingDemoProps> = ({
  crackedPasswords,
  onCrackPassword,
  onReset
}) => {
  const weakPasswords = ["password123", "qwerty", "123456", "admin", "letmein"];

  return (
    <section className="relative py-12 sm:py-16 md:py-20 lg:py-24 xl:py-32 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24">
      <div className="w-full max-w-[1800px] mx-auto">
        <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-center mb-8 sm:mb-12 md:mb-16 lg:mb-20 xl:mb-24 bg-gradient-to-r from-red-400 to-yellow-400 bg-clip-text text-transparent">
          Watch Passwords Get Cracked in Real-Time
        </h2>

        <div className="grid lg:grid-cols-2 gap-6 sm:gap-8 md:gap-10 lg:gap-12 xl:gap-16 items-start">
          <div className="space-y-3 sm:space-y-4 md:space-y-5 lg:space-y-6">
            <h3 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold text-red-400 flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6 md:mb-8">
              <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 lg:w-10 lg:h-10" />
              Common Passwords
            </h3>
            {weakPasswords.map((pwd, i) => (
              <div
                key={i}
                className={`relative bg-red-950 bg-opacity-50 p-3 sm:p-4 md:p-5 lg:p-6 xl:p-8 rounded-lg border transition-all duration-500 ${
                  crackedPasswords[i] ? 'border-red-500 animate-pulse' : 'border-red-800'
                }`}
                onMouseEnter={() => onCrackPassword(pwd, i)}
              >
                <div className="flex items-center justify-between">
                  <p className="font-mono text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl">{pwd}</p>
                  {crackedPasswords[i] && (
                    <div className="flex items-center gap-2 text-red-400">
                      <XCircle className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 lg:w-7 lg:h-7" />
                      <span className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl">Cracked!</span>
                    </div>
                  )}
                </div>
                {crackedPasswords[i] && (
                  <div className="mt-2 text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-red-400">
                    Time to crack: {i + 1} seconds
                  </div>
                )}
              </div>
            ))}
            <button
              onClick={onReset}
              className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-gray-400 hover:text-white transition-colors"
            >
              Reset Demo
            </button>
          </div>

          <div className="bg-green-950 bg-opacity-50 p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-lg border border-green-800">
            <h3 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold text-green-400 flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6 md:mb-8">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 lg:w-10 lg:h-10" />
              DigitaLockbox Protection
            </h3>
            <div className="space-y-4 sm:space-y-6 md:space-y-8">
              <div className="flex items-center gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 bg-green-900 rounded-full flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 lg:w-8 lg:h-8 xl:w-10 xl:h-10 text-green-400" />
                </div>
                <div>
                  <p className="font-semibold text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl">Auto-Generated Passwords</p>
                  <p className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-gray-400">Unique for every account</p>
                </div>
              </div>
              <div className="flex items-center gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 bg-green-900 rounded-full flex items-center justify-center flex-shrink-0">
                  <Lock className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 lg:w-8 lg:h-8 xl:w-10 xl:h-10 text-green-400" />
                </div>
                <div>
                  <p className="font-semibold text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl">Zero-Knowledge Encryption</p>
                  <p className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-gray-400">Even we can't see your passwords</p>
                </div>
              </div>
              <div className="flex items-center gap-3 sm:gap-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 bg-green-900 rounded-full flex items-center justify-center flex-shrink-0">
                  <Key className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 lg:w-8 lg:h-8 xl:w-10 xl:h-10 text-green-400" />
                </div>
                <div>
                  <p className="font-semibold text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl">One Master Password</p>
                  <p className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-gray-400">The only one you need to remember</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CrackingDemo;