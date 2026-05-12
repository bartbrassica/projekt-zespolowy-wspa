import React from 'react';
import type { CheckboxProps } from '../../types/auth';

const Checkbox: React.FC<CheckboxProps> = ({
  id,
  name,
  checked,
  onChange,
  label,
  className = ''
}) => {
  const defaultClassName = "h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-800";

  return (
    <div className="flex items-center">
      <input
        id={id}
        name={name}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className={className || defaultClassName}
      />
      <label htmlFor={id} className="ml-2 block text-sm text-gray-300">
        {label}
      </label>
    </div>
  );
};

export default Checkbox;