import React from 'react';
import { Eye, EyeOff } from 'lucide-react';
import type { InputFieldProps } from '../../types/auth';

const InputField: React.FC<InputFieldProps> = ({
  id,
  name,
  type,
  placeholder,
  value,
  onChange,
  required = false,
  autoComplete,
  icon,
  showToggle = false,
  showPassword = false,
  onTogglePassword,
  className
}) => {
  return (
    <div>
      <label htmlFor={id} className="sr-only">
        {placeholder}
      </label>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          {icon}
        </div>
        <input
          id={id}
          name={name}
          type={showToggle ? (showPassword ? 'text' : 'password') : type}
          autoComplete={autoComplete}
          required={required}
          value={value}
          onChange={onChange}
          className={className || "appearance-none relative block w-full px-10 py-3 bg-black bg-opacity-50 border border-gray-700 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"}
          placeholder={placeholder}
        />
        {showToggle && onTogglePassword && (
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
            onClick={onTogglePassword}
          >
            {showPassword ? (
              <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-300" />
            ) : (
              <Eye className="h-5 w-5 text-gray-400 hover:text-gray-300" />
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default InputField;