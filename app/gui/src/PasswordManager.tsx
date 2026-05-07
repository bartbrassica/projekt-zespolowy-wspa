import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Eye, 
  EyeOff, 
  Edit, 
  Trash2, 
  Copy, 
  ExternalLink,
  Star,
  StarOff,
  Key,
  RefreshCw,
  Shield,
  Clock,
  AlertCircle
} from 'lucide-react';
import { authenticatedFetch } from './store/auth';

interface PasswordEntry {
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

interface PasswordFormData {
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

const PasswordManager: React.FC = () => {
  const [passwords, setPasswords] = useState<PasswordEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState<{ [key: string]: boolean }>({});
  const [decryptedPasswords, setDecryptedPasswords] = useState<{ [key: string]: string }>({});
  const [masterPassword, setMasterPassword] = useState('');
  const [showMasterPasswordModal, setShowMasterPasswordModal] = useState(false);
  const [pendingAction, setPendingAction] = useState<{ type: string; data?: any } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<PasswordFormData>({
    name: '',
    site: '',
    username: '',
    password: '',
    notes: '',
    is_favorite: false,
    master_password: ''
  });

  const [generatorSettings] = useState({
    length: 16,
    include_symbols: true,
    include_numbers: true,
    include_uppercase: true,
    include_lowercase: true,
    exclude_ambiguous: true
  });

  // Fetch passwords on component mount
  useEffect(() => {
    fetchPasswords();
  }, []);

  const fetchPasswords = async () => {
    try {
      setLoading(true);
      const response = await authenticatedFetch('/api/passwords/entries');
      if (response.ok) {
        const data = await response.json();
        setPasswords(data);
      } else {
        setError('Failed to fetch passwords');
      }
    } catch (err) {
      setError('Error fetching passwords');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generatePassword = async () => {
    try {
      const response = await fetch('/api/passwords/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatorSettings)
      });
      
      if (response.ok) {
        const data = await response.json();
        setFormData({ ...formData, password: data.password });
        setSuccess(`Generated ${data.strength} password`);
      }
    } catch (err) {
      setError('Failed to generate password' + err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.master_password) {
      setShowMasterPasswordModal(true);
      setPendingAction({ type: 'submit', data: formData });
      return;
    }

    try {
      const url = editingId 
        ? `/api/passwords/entries/${editingId}`
        : '/api/passwords/entries';
      
      const method = editingId ? 'PUT' : 'POST';

      const payload: any = {
        name: formData.name,
        site: formData.site,
        username: formData.username,
        notes: formData.notes,
        is_favorite: formData.is_favorite,
        master_password: formData.master_password,
        expires_at: formData.expires_at
          ? new Date(formData.expires_at).toISOString()
          : null
      };
  
      if (formData.password || !editingId) {
        payload.password = formData.password;
      }
  
      if (formData.folder_id) {
        payload.folder_id = formData.folder_id;
      }
      if (formData.tag_ids) {
        payload.tag_ids = formData.tag_ids;
      }
      
      const response = await authenticatedFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
  
      if (response.ok) {
        setSuccess(editingId ? 'Password updated successfully' : 'Password created successfully');
        setShowModal(false);
        resetForm();
        fetchPasswords();
      } else {
        const errorData = await response.json();
        // Handle different error formats
        const errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : (errorData.detail?.[0]?.msg || 'Operation failed');
        setError(errorMessage);
      }
    } catch (err) {
      setError('An error occurred');
      console.error(err);
    }
  };

  const handleDecrypt = async (entryId: string) => {
    if (!masterPassword) {
      setShowMasterPasswordModal(true);
      setPendingAction({ type: 'decrypt', data: entryId });
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/passwords/entries/${entryId}/decrypt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ master_password: masterPassword })
      });

      if (response.ok) {
        const data = await response.json();
        setDecryptedPasswords({ ...decryptedPasswords, [entryId]: data.password });
        setShowPassword({ ...showPassword, [entryId]: true });
      } else {
        setError('Failed to decrypt password. Check your master password.');
      }
    } catch (err) {
      setError('Decryption error ' + err);
    }
  };

  const handleCopyPassword = async (entryId: string) => {
    if (!decryptedPasswords[entryId]) {
      await handleDecrypt(entryId);
    }
    
    if (decryptedPasswords[entryId]) {
      navigator.clipboard.writeText(decryptedPasswords[entryId]);
      setSuccess('Password copied to clipboard');
      
      // Auto-clear clipboard after 30 seconds
      setTimeout(() => {
        navigator.clipboard.writeText('');
      }, 30000);
    }
  };

  const handleDelete = async (entryId: string) => {
    if (!confirm('Are you sure you want to delete this password?')) return;
    
    if (!masterPassword) {
      setShowMasterPasswordModal(true);
      setPendingAction({ type: 'delete', data: entryId });
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/passwords/entries/${entryId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ master_password: masterPassword })
      });

      if (response.ok) {
        setSuccess('Password deleted successfully');
        fetchPasswords();
      } else {
        setError('Failed to delete password');
      }
    } catch (err) {
      setError('Delete operation failed ' + err);
    }
  };

  const handleToggleFavorite = async (entry: PasswordEntry) => {
    if (!masterPassword) {
      setShowMasterPasswordModal(true);
      setPendingAction({ type: 'favorite', data: entry });
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/passwords/entries/${entry.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_favorite: !entry.is_favorite,
          master_password: masterPassword
        })
      });

      if (response.ok) {
        fetchPasswords();
      }
    } catch (err) {
      console.error('Failed to toggle favorite', err);
    }
  };

  const handleMasterPasswordSubmit = () => {
    setFormData({ ...formData, master_password: masterPassword });
    setShowMasterPasswordModal(false);
    
    if (pendingAction) {
      switch (pendingAction.type) {
        case 'submit':
          handleSubmit(new Event('submit') as any);
          break;
        case 'decrypt':
          handleDecrypt(pendingAction.data);
          break;
        case 'delete':
          handleDelete(pendingAction.data);
          break;
        case 'favorite':
          handleToggleFavorite(pendingAction.data);
          break;
      }
      setPendingAction(null);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      site: '',
      username: '',
      password: '',
      notes: '',
      expires_at: undefined,
      is_favorite: false,
      master_password: masterPassword
    });
    setEditingId(null);
  };

  const openEditModal = (entry: PasswordEntry) => {
    setEditingId(entry.id);
    setFormData({
      name: entry.name,
      site: entry.site,
      username: entry.username,
      password: '',
      notes: entry.notes,
      is_favorite: entry.is_favorite,
      expires_at: entry.expires_at ? new Date(entry.expires_at).toISOString().slice(0, 10) : undefined,
      master_password: masterPassword
    });
    setShowModal(true);
  };

  const filteredPasswords = passwords
  .filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.site.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.username.toLowerCase().includes(searchQuery.toLowerCase())
  )
  .sort((a, b) => {
    // Sort favorites first
    if (a.is_favorite && !b.is_favorite) return -1;
    if (!a.is_favorite && b.is_favorite) return 1;
    return 0;
  });

  const getPasswordStrength = (password: string): { strength: string; color: string } => {
    if (!password) return { strength: 'None', color: 'text-gray-400' };
    if (password.length < 8) return { strength: 'Weak', color: 'text-red-500' };
    if (password.length < 12) return { strength: 'Medium', color: 'text-yellow-500' };
    return { strength: 'Strong', color: 'text-green-500' };
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Shield className="h-8 w-8 text-indigo-600" />
            Password Manager
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Securely manage all your passwords in one place
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-red-700 dark:text-red-400">{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500 flex items-center gap-3">
            <Shield className="h-5 w-5 text-green-500" />
            <span className="text-green-700 dark:text-green-400">{success}</span>
            <button 
              onClick={() => setSuccess(null)}
              className="ml-auto text-green-500 hover:text-green-700"
            >
              ×
            </button>
          </div>
        )}

        {/* Search and Actions Bar */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search passwords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
          >
            <Plus className="h-5 w-5" />
            Add Password
          </button>
        </div>

        {/* Password Cards Grid */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin" />
          </div>
        ) : filteredPasswords.length === 0 ? (
          <div className="text-center py-12">
            <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No passwords found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {searchQuery ? 'Try a different search term' : 'Get started by adding your first password'}
            </p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredPasswords.map((entry) => (
              <div
                key={entry.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {entry.name}
                    </h3>
                    {entry.is_favorite && (
                      <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    )}
                  </div>
                  <button
                    onClick={() => handleToggleFavorite(entry)}
                    className="text-gray-400 hover:text-yellow-500 transition-colors"
                  >
                    {entry.is_favorite ? (
                      <StarOff className="h-5 w-5" />
                    ) : (
                      <Star className="h-5 w-5" />
                    )}
                  </button>
                </div>

                <div className="space-y-2 mb-4">
                  {entry.site && (
                    <div className="flex items-center gap-2 text-sm">
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                      <a 
                        href={entry.site} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-indigo-600 hover:text-indigo-700 truncate"
                      >
                        {new URL(entry.site).hostname}
                      </a>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Username:</span>
                    <span className="truncate">{entry.username || 'N/A'}</span>
                  </div>

                  {entry.expires_at && (
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-yellow-500" />
                      <span className="text-yellow-600 dark:text-yellow-400">
                        Expires: {new Date(entry.expires_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleCopyPassword(entry.id)}
                    className="flex-1 px-3 py-1.5 text-sm bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded hover:bg-indigo-100 dark:hover:bg-indigo-900/30 transition-colors flex items-center justify-center gap-1"
                  >
                    <Copy className="h-4 w-4" />
                    Copy
                  </button>
                  <button
                    onClick={() => {
                      if (showPassword[entry.id]) {
                        setShowPassword({ ...showPassword, [entry.id]: false });
                      } else {
                        handleDecrypt(entry.id);
                      }
                    }}
                    className="px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    {showPassword[entry.id] ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                  <button
                    onClick={() => openEditModal(entry)}
                    className="px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="px-3 py-1.5 text-sm bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                {showPassword[entry.id] && decryptedPasswords[entry.id] && (
                  <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Password:</p>
                    <code className="text-sm font-mono text-gray-900 dark:text-white">
                      {decryptedPasswords[entry.id]}
                    </code>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Add/Edit Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {editingId ? 'Edit Password' : 'Add New Password'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Website URL
                    </label>
                    <input
                      type="url"
                      value={formData.site}
                      onChange={(e) => setFormData({ ...formData, site: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Username/Email
                    </label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Password *
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword['form'] ? 'text' : 'password'}
                        required={!editingId}
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="w-full px-3 py-2 pr-20 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder={editingId ? 'Leave blank to keep current' : ''}
                      />
                      <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex gap-1">
                        <button
                          type="button"
                          onClick={() => setShowPassword({ ...showPassword, form: !showPassword['form'] })}
                          className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        >
                          {showPassword['form'] ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          type="button"
                          onClick={generatePassword}
                          className="p-1 text-indigo-600 hover:text-indigo-700"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    {formData.password && (
                      <p className={`text-xs mt-1 ${getPasswordStrength(formData.password).color}`}>
                        Strength: {getPasswordStrength(formData.password).strength}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Notes
                    </label>
                    <textarea
                      value={formData.notes}
                      onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Expiration Date
                    </label>
                    <input
                        type="date"
                        value={formData.expires_at || ''}
                        onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="favorite"
                      checked={formData.is_favorite}
                      onChange={(e) => setFormData({ ...formData, is_favorite: e.target.checked })}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="favorite" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      Mark as favorite
                    </label>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowModal(false);
                        resetForm();
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      {editingId ? 'Update' : 'Create'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Master Password Modal */}
        {showMasterPasswordModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
              <div className="flex items-center gap-3 mb-4">
                <Key className="h-6 w-6 text-indigo-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Enter Master Password
                </h2>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Your master password is required to encrypt and decrypt passwords.
              </p>

              <input
                type="password"
                value={masterPassword}
                onChange={(e) => setMasterPassword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && masterPassword) {
                    handleMasterPasswordSubmit();
                  }
                }}
                placeholder="Enter your master password"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4"
                autoFocus
              />

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowMasterPasswordModal(false);
                    setPendingAction(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleMasterPasswordSubmit}
                  disabled={!masterPassword}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PasswordManager;
