import { Lock, Zap, Globe } from 'lucide-react';
import type { Feature } from '../types/landing';

// Features structure without text (text will come from translations)
export const getFeaturesStructure = (): Feature[] => [
  {
    icon: Lock,
    titleKey: "landing.militaryGradeEncryption",
    descKey: "landing.militaryGradeEncryptionDesc",
    color: "from-purple-500 to-purple-600"
  },
  {
    icon: Zap,
    titleKey: "landing.instantAccess",
    descKey: "landing.instantAccessDesc",
    color: "from-blue-500 to-blue-600"
  },
  {
    icon: Globe,
    titleKey: "landing.crossPlatformSync",
    descKey: "landing.crossPlatformSyncDesc",
    color: "from-cyan-500 to-cyan-600"
  }
];