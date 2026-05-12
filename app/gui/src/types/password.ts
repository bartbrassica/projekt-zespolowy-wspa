export interface PasswordEntry {
  id: string;
  name: string;
  site: string;
  username: string;
  notes: string;
  is_favorite: boolean;
  folder: string | null;
  tags: string[];
  expires_at: string | null;
  created_at: string;
  updated_at: string;
  last_accessed: string | null;
}

export interface PasswordFormData {
  name: string;
  site: string;
  username: string;
  password: string;
  notes: string;
  is_favorite: boolean;
  folder_id?: string;
  tag_ids?: string[];
  expires_at?: string;
  master_password: string;
}

export interface PasswordGeneratorSettings {
  length: number;
  include_symbols: boolean;
  include_numbers: boolean;
  include_uppercase: boolean;
  include_lowercase: boolean;
  exclude_ambiguous: boolean;
}

export interface PasswordStrengthInfo {
  strength: string;
  color: string;
}

export interface PendingAction {
  type: 'submit' | 'decrypt' | 'delete' | 'favorite';
  data?: string | PasswordEntry | PasswordFormData;
}

export interface AlertProps {
  type: 'error' | 'success';
  message: string;
  onClose: () => void;
}

export interface PasswordCardProps {
  entry: PasswordEntry;
  showPassword: boolean;
  decryptedPassword?: string;
  onToggleFavorite: (entry: PasswordEntry) => void;
  onCopyPassword: (entryId: string) => void;
  onToggleVisibility: (entryId: string) => void;
  onEdit: (entry: PasswordEntry) => void;
  onDelete: (entryId: string) => void;
}

export interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onAddPassword: () => void;
}

export interface PasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  editingEntry?: PasswordEntry | null;
  onSubmit: (formData: PasswordFormData) => void;
  onGeneratePassword: () => void;
  formData: PasswordFormData;
  onFormDataChange: (data: Partial<PasswordFormData>) => void;
  showPassword: boolean;
  onTogglePasswordVisibility: () => void;
  passwordStrength: PasswordStrengthInfo;
}

export interface MasterPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (password: string) => void;
  masterPassword: string;
  onMasterPasswordChange: (password: string) => void;
}