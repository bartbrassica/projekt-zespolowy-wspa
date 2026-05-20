import { Lock, Zap, Globe } from 'lucide-react';
import type { Feature } from '../types/landing';

export const FEATURES: Feature[] = [
  {
    icon: Lock,
    title: "Military-Grade Encryption",
    desc: "PBKDF2 + AES-128 encryption keeps your data secure",
    color: "from-purple-500 to-purple-600"
  },
  {
    icon: Zap,
    title: "Instant Access",
    desc: "One click to fill passwords anywhere",
    color: "from-blue-500 to-blue-600"
  },
  {
    icon: Globe,
    title: "Cross-Platform Sync",
    desc: "Access your vault from any device",
    color: "from-cyan-500 to-cyan-600"
  }
];

export const HERO_TEXT = "Your Guardian";