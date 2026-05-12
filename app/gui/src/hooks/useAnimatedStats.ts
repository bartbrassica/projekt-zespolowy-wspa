import { useState, useEffect } from 'react';
import type { AnimatedStats } from '../types/landing';

export const useAnimatedStats = (isVisible: boolean): AnimatedStats => {
  const [animatedStats, setAnimatedStats] = useState<AnimatedStats>({
    breaches: 0,
    reuse: 0,
    time: 0
  });

  useEffect(() => {
    if (isVisible) {
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

  return animatedStats;
};