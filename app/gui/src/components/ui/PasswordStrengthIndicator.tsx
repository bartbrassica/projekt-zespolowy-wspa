import React from 'react';
import type { PasswordStrength } from '../../types/auth';

interface PasswordStrengthIndicatorProps {
  strength: PasswordStrength;
  password: string;
}

const PasswordStrengthIndicator: React.FC<PasswordStrengthIndicatorProps> = ({
  strength,
  password
}) => {
  if (!password) return null;

  const getTextColor = () => {
    if (strength.score < 40) return 'text-red-400';
    if (strength.score < 70) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="mt-2">
      <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${strength.color} transition-all duration-300`}
          style={{ width: `${strength.score}%` }}
        />
      </div>
      <p className={`text-xs mt-1 ${getTextColor()}`}>
        {strength.text} Password
      </p>
    </div>
  );
};

export default PasswordStrengthIndicator;