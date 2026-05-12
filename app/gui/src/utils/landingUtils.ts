export const calculatePasswordStrength = (password: string): number => {
  let strength = 0;
  if (password.length >= 8) strength += 20;
  if (password.length >= 12) strength += 20;
  if (/[a-z]/.test(password)) strength += 15;
  if (/[A-Z]/.test(password)) strength += 15;
  if (/[0-9]/.test(password)) strength += 15;
  if (/[^A-Za-z0-9]/.test(password)) strength += 15;
  return strength;
};

export const getPasswordStrengthColor = (strength: number): string => {
  if (strength < 40) return 'from-red-500 to-red-600';
  if (strength < 70) return 'from-yellow-500 to-yellow-600';
  return 'from-green-500 to-green-600';
};

export const getPasswordStrengthText = (strength: number): string => {
  if (strength < 40) return 'Weak';
  if (strength < 70) return 'Medium';
  return 'Strong';
};

export const generateSecurePassword = (): string => {
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
  return password.split('').sort(() => Math.random() - 0.5).join('');
};

export const copyToClipboard = async (text: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
  }
};

export const createCrackPasswordHandler = (
  setCrackedPasswords: React.Dispatch<React.SetStateAction<Record<number, boolean>>>
) => {
  return (_password: string, index: number) => {
    setTimeout(() => {
      setCrackedPasswords((prev: Record<number, boolean>) => ({ ...prev, [index]: true }));
    }, 500 + index * 200);
  };
};

export const resetCrackedPasswords = (
  setCrackedPasswords: React.Dispatch<React.SetStateAction<Record<number, boolean>>>
) => {
  setCrackedPasswords({});
};