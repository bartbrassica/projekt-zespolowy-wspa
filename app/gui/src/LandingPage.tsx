import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useMouseTracking,
  useTypingAnimation,
  useIntersectionObserver,
  useAnimatedStats,
  usePasswordStrengthDemo,
  usePasswordGenerator
} from './hooks';
import {
  Navigation,
  HeroSection,
  PasswordGenerator,
  CrackingDemo,
  Stats,
  Features
} from './components/landing';
import { createCrackPasswordHandler, resetCrackedPasswords } from './utils/landingUtils';
import { FEATURES, HERO_TEXT } from './constants/landingData';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);
  const [crackedPasswords, setCrackedPasswords] = useState<Record<number, boolean>>({});

  // Custom hooks
  const mousePosition = useMouseTracking();
  const typedText = useTypingAnimation(HERO_TEXT, 100);
  const { isVisible } = useIntersectionObserver();
  const animatedStats = useAnimatedStats(isVisible['stats-section'] || false);
  const { passwordInput, passwordStrength, handlePasswordChange } = usePasswordStrengthDemo();
  const { generatedPassword, copied, generatePassword, copyPassword } = usePasswordGenerator();

  // Event handlers
  const handleLogin = () => navigate('/login');
  const handleGetStarted = () => navigate('/login');
  const handleCrackPassword = createCrackPasswordHandler(setCrackedPasswords);
  const handleResetDemo = () => resetCrackedPasswords(setCrackedPasswords);
  const handleFeatureHover = (index: number | null) => setHoveredFeature(index);

  return (
    <div className="min-h-screen bg-black text-white relative">
      {/* Animated Background with Mouse Tracking */}
      <div className="fixed inset-0 opacity-30 overflow-hidden pointer-events-none">
        <div
          className="absolute inset-[-20%] bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-600 animate-pulse transition-transform duration-200 ease-out"
          style={{
            transform: `translate(${mousePosition.x * 50}px, ${mousePosition.y * 50}px)`
          }}
        ></div>
        <div className="absolute inset-0 bg-black bg-opacity-50"></div>
      </div>

      {/* Navigation */}
      <Navigation onLogin={handleLogin} />

      {/* Hero Section */}
      <HeroSection
        mousePosition={mousePosition}
        typedText={typedText}
        passwordInput={passwordInput}
        passwordStrength={passwordStrength}
        onPasswordChange={handlePasswordChange}
        onGetStarted={handleGetStarted}
      />

      {/* Password Generator */}
      <PasswordGenerator
        generatedPassword={generatedPassword}
        copied={copied}
        onGenerate={generatePassword}
        onCopy={copyPassword}
      />

      {/* Password Cracking Demo */}
      <CrackingDemo
        crackedPasswords={crackedPasswords}
        onCrackPassword={handleCrackPassword}
        onReset={handleResetDemo}
      />

      {/* Statistics */}
      <Stats animatedStats={animatedStats} />

      {/* Features */}
      <Features
        features={FEATURES}
        hoveredFeature={hoveredFeature}
        onFeatureHover={handleFeatureHover}
      />

      {/* Footer */}
      <footer className="relative py-6 sm:py-8 md:py-10 lg:py-12 xl:py-16 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24 border-t border-gray-800">
        <div className="w-full max-w-[1800px] mx-auto text-center text-gray-400">
          <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl">&copy; 2025 DigitaLockbox. Your security is our priority.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;