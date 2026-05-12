import type { LucideIcon } from 'lucide-react';

export interface MousePosition {
  x: number;
  y: number;
}

export interface AnimatedStats {
  breaches: number;
  reuse: number;
  time: number;
}

export interface Feature {
  icon: LucideIcon;
  title: string;
  desc: string;
  color: string;
}

export interface PasswordGeneratorState {
  generatedPassword: string;
  copied: boolean;
}

export interface PasswordStrengthState {
  passwordInput: string;
  passwordStrength: number;
}

export interface CrackingDemoState {
  crackedPasswords: Record<number, boolean>;
}

export interface VisibilityState {
  isVisible: Record<string, boolean>;
}

export interface HeroSectionProps {
  mousePosition: MousePosition;
  typedText: string;
  passwordInput: string;
  passwordStrength: number;
  onPasswordChange: (password: string) => void;
  onGetStarted: () => void;
}

export interface PasswordGeneratorProps {
  generatedPassword: string;
  copied: boolean;
  onGenerate: () => void;
  onCopy: () => void;
}

export interface CrackingDemoProps {
  crackedPasswords: Record<number, boolean>;
  onCrackPassword: (password: string, index: number) => void;
  onReset: () => void;
}

export interface StatsProps {
  animatedStats: AnimatedStats;
}

export interface FeaturesProps {
  features: Feature[];
  hoveredFeature: number | null;
  onFeatureHover: (index: number | null) => void;
}

export interface NavigationProps {
  onLogin: () => void;
}