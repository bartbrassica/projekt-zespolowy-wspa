import { useState, useEffect } from 'react';

export const useTypingAnimation = (text: string, speed: number = 100): string => {
  const [typedText, setTypedText] = useState('');

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= text.length) {
        setTypedText(text.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return typedText;
};