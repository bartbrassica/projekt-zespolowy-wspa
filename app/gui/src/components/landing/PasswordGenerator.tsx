import React from 'react';
import { RefreshCw, Copy, CheckCircle } from 'lucide-react';
import type { PasswordGeneratorProps } from '../../types/landing';

const PasswordGenerator: React.FC<PasswordGeneratorProps> = ({
  generatedPassword,
  copied,
  onGenerate,
  onCopy
}) => {
  return (
    <section className="relative py-12 sm:py-16 md:py-20 lg:py-24 xl:py-32 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24">
      <div className="w-full max-w-[1600px] mx-auto">
        <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-center mb-6 sm:mb-8 md:mb-12 lg:mb-16 xl:mb-20">
          Generate Your First <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">Secure Password</span>
        </h2>

        <div className="bg-gray-900 bg-opacity-50 p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-2xl border border-gray-700 backdrop-blur-sm">
          <div className="flex flex-col lg:flex-row gap-4 sm:gap-6 md:gap-8 items-center">
            <div className="flex-1 w-full bg-black bg-opacity-50 p-3 sm:p-4 md:p-5 lg:p-6 xl:p-8 rounded-xl border border-gray-700">
              <p className="font-mono text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl text-center break-all">
                {generatedPassword || 'Click generate to create a password'}
              </p>
            </div>

            <div className="flex gap-2 sm:gap-3 md:gap-4">
              <button
                onClick={onGenerate}
                className="px-4 py-2 sm:px-6 sm:py-3 md:px-8 md:py-4 lg:px-10 lg:py-5 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-xl font-semibold hover:scale-105 transition-all duration-300 flex items-center gap-2 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl"
              >
                <RefreshCw className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 lg:w-7 lg:h-7" />
                Generate
              </button>

              {generatedPassword && (
                <button
                  onClick={onCopy}
                  className="px-4 py-2 sm:px-6 sm:py-3 md:px-8 md:py-4 lg:px-10 lg:py-5 bg-gray-800 rounded-xl font-semibold hover:bg-gray-700 transition-all duration-300 flex items-center gap-2 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl"
                >
                  {copied ? (
                    <>
                      <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 lg:w-7 lg:h-7 text-green-400" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 lg:w-7 lg:h-7" />
                      Copy
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PasswordGenerator;