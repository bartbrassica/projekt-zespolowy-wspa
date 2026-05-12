import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import type { BrandLogoProps } from '../../types/layout';

const BrandLogo: React.FC<BrandLogoProps> = ({ className = '' }) => {
  return (
    <div className={`flex-shrink-0 flex items-center ${className}`}>
      <Link to="/passwords" className="flex items-center">
        <Shield className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
        <span className="ml-2 text-xl font-semibold text-gray-900 dark:text-white">
          Digital Lockbox
        </span>
      </Link>
    </div>
  );
};

export default BrandLogo;