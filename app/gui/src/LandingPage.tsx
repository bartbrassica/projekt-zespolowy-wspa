import { useState, useEffect } from 'react';
import { Shield, Lock, Key, AlertTriangle, Zap, Globe, RefreshCw, Copy, CheckCircle, XCircle, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [copied, setCopied] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);
  const [crackedPasswords, setCrackedPasswords] = useState<Record<number, boolean>>({});
  const [animatedStats, setAnimatedStats] = useState({ breaches: 0, reuse: 0, time: 0 });
  const [typedText, setTypedText] = useState('');
  const [isVisible, setIsVisible] = useState<Record<string, boolean>>({});
  
  const fullText = "Your Guardian";

  // Mouse tracking for parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      setMousePosition({ x, y });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Typing animation
  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setTypedText(fullText.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, 100);
    return () => clearInterval(timer);
  }, []);

  // Intersection observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          setIsVisible((prev: Record<string, boolean>) => ({
            ...prev,
            [entry.target.id]: entry.isIntersecting
          }));
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[data-animate]').forEach(el => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  // Animated statistics counter
  useEffect(() => {
    if (isVisible['stats-section']) {
      const duration = 2000;
      const steps = 60;
      const interval = duration / steps;
      let step = 0;

      const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        setAnimatedStats({
          breaches: Math.floor(80 * progress),
          reuse: Math.floor(51 * progress),
          time: Math.floor(13 * progress)
        });
        if (step >= steps) clearInterval(timer);
      }, interval);

      return () => clearInterval(timer);
    }
  }, [isVisible]);

  // Password strength calculation
  const calculatePasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength += 20;
    if (password.length >= 12) strength += 20;
    if (/[a-z]/.test(password)) strength += 15;
    if (/[A-Z]/.test(password)) strength += 15;
    if (/[0-9]/.test(password)) strength += 15;
    if (/[^A-Za-z0-9]/.test(password)) strength += 15;
    return strength;
  };

  useEffect(() => {
    setPasswordStrength(calculatePasswordStrength(passwordInput));
  }, [passwordInput]);

  // Password generator
  const generatePassword = () => {
    const chars = {
      lower: 'abcdefghijklmnopqrstuvwxyz',
      upper: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
      numbers: '0123456789',
      symbols: '!@#$%^&*()_+-=[]{}|;:,.<>?'
    };
    
    let password = '';
    const allChars = chars.lower + chars.upper + chars.numbers + chars.symbols;
    
    // Ensure at least one of each type
    password += chars.lower[Math.floor(Math.random() * chars.lower.length)];
    password += chars.upper[Math.floor(Math.random() * chars.upper.length)];
    password += chars.numbers[Math.floor(Math.random() * chars.numbers.length)];
    password += chars.symbols[Math.floor(Math.random() * chars.symbols.length)];
    
    // Fill the rest
    for (let i = 4; i < 16; i++) {
      password += allChars[Math.floor(Math.random() * allChars.length)];
    }
    
    // Shuffle
    password = password.split('').sort(() => Math.random() - 0.5).join('');
    setGeneratedPassword(password);
  };

  // Copy to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedPassword);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simulate password cracking
  const crackPassword = (_password: string, index: number) => {
    setTimeout(() => {
      setCrackedPasswords((prev: Record<number, boolean>) => ({ ...prev, [index]: true }));
    }, 500 + index * 200);
  };

  const weakPasswords = ["password123", "qwerty", "123456", "admin", "letmein"];
  
  const getStrengthColor = () => {
    if (passwordStrength < 40) return 'from-red-500 to-red-600';
    if (passwordStrength < 70) return 'from-yellow-500 to-yellow-600';
    return 'from-green-500 to-green-600';
  };

  const getStrengthText = () => {
    if (passwordStrength < 40) return 'Weak';
    if (passwordStrength < 70) return 'Medium';
    return 'Strong';
  };

  const features = [
    { icon: Lock, title: "Military-Grade Encryption", desc: "AES-256 encryption keeps your data secure", color: "from-purple-500 to-purple-600" },
    { icon: Zap, title: "Instant Access", desc: "One click to fill passwords anywhere", color: "from-blue-500 to-blue-600" },
    { icon: Globe, title: "Cross-Platform Sync", desc: "Access your vault from any device", color: "from-cyan-500 to-cyan-600" }
  ];

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
      <nav className="relative z-50 w-full">
        <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24 py-4 md:py-6 lg:py-8">
          <div className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            DigitaLockbox
          </div>
          
          <button 
            onClick={() => navigate('/login')}
            className="group relative px-4 py-2 sm:px-6 sm:py-3 md:px-8 md:py-4 lg:px-10 lg:py-5 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50"
          >
            <span className="relative z-10">Login</span>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-700 to-cyan-700 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </button>
        </div>
      </nav>

      {/* Hero Section with Parallax */}
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
            DigitaLockbox
          </h1>
          
          <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl 2xl:text-5xl mb-4 sm:mb-6 md:mb-8 text-gray-300 h-8 sm:h-10 md:h-12 lg:h-14">
            {typedText}
            <span className="animate-pulse">|</span>
          </p>
          
          <p className="text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl 2xl:text-4xl mb-6 sm:mb-8 md:mb-10 lg:mb-12 text-gray-400 max-w-4xl mx-auto">
            Stop using sticky notes. Start using the password manager that puts your security first.
          </p>
          
          {/* Interactive Password Strength Demo */}
          <div className="max-w-lg md:max-w-xl lg:max-w-2xl xl:max-w-3xl mx-auto mb-6 sm:mb-8 md:mb-10 lg:mb-12">
            <div className="relative">
              <input
                type="password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="Try typing a password..."
                className="w-full px-4 py-3 sm:px-6 sm:py-4 md:px-8 md:py-5 lg:px-10 lg:py-6 xl:px-12 xl:py-7 text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl bg-gray-900 bg-opacity-50 border border-gray-700 rounded-full text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-all duration-300"
              />
              <div className="absolute left-0 right-0 -bottom-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${getStrengthColor()} transition-all duration-300`}
                  style={{ width: `${passwordStrength}%` }}
                />
              </div>
              {passwordInput && (
                <div className="absolute -bottom-8 sm:-bottom-10 md:-bottom-12 left-1/2 transform -translate-x-1/2 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl">
                  <span className={`text-${passwordStrength < 40 ? 'red' : passwordStrength < 70 ? 'yellow' : 'green'}-400`}>
                    {getStrengthText()} Password
                  </span>
                </div>
              )}
            </div>
          </div>
          
          <button 
            onClick={() => navigate('/login')}
            className="group relative px-6 py-3 sm:px-8 sm:py-4 md:px-10 md:py-5 lg:px-12 lg:py-6 xl:px-14 xl:py-7 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-full text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl font-semibold transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50 mt-8 sm:mt-10 md:mt-12 lg:mt-16"
          >
            <span className="relative z-10">Get Started Free</span>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-700 to-cyan-700 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </button>
        </div>
      </section>

      {/* Interactive Password Generator */}
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
                  onClick={generatePassword}
                  className="px-4 py-2 sm:px-6 sm:py-3 md:px-8 md:py-4 lg:px-10 lg:py-5 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-xl font-semibold hover:scale-105 transition-all duration-300 flex items-center gap-2 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl"
                >
                  <RefreshCw className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 lg:w-7 lg:h-7" />
                  Generate
                </button>
                
                {generatedPassword && (
                  <button
                    onClick={copyToClipboard}
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

      {/* Interactive Password Cracking Demo */}
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
                  onMouseEnter={() => crackPassword(pwd, i)}
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
                onClick={() => setCrackedPasswords({})}
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

      {/* Animated Statistics */}
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

      {/* Interactive Features */}
      <section className="relative py-12 sm:py-16 md:py-20 lg:py-24 xl:py-32 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 2xl:px-24">
        <div className="w-full max-w-[1800px] mx-auto">
          <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-center mb-8 sm:mb-12 md:mb-16 lg:mb-20 xl:mb-24">
            Your Security, <span className="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">Simplified</span>
          </h2>
          
          <div className="grid lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8 lg:gap-10 xl:gap-12">
            {features.map((feature, i) => (
              <div 
                key={i}
                onMouseEnter={() => setHoveredFeature(i)}
                onMouseLeave={() => setHoveredFeature(null)}
                className="group relative p-4 sm:p-6 md:p-8 lg:p-10 xl:p-12 rounded-2xl bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 hover:border-purple-500 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20 cursor-pointer"
              >
                <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-300`}></div>
                <div className="relative z-10">
                  <div className={`mb-4 sm:mb-6 md:mb-8 inline-flex p-2 sm:p-3 md:p-4 lg:p-5 bg-gradient-to-br ${feature.color} rounded-xl transition-all duration-300 ${hoveredFeature === i ? 'scale-110 rotate-12' : ''}`}>
                    <feature.icon className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 lg:w-10 lg:h-10 xl:w-12 xl:h-12" />
                  </div>
                  <h3 className="text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-2 sm:mb-3 md:mb-4">{feature.title}</h3>
                  <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl text-gray-400">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

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