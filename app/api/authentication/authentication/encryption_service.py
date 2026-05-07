from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import secrets
from typing import Tuple, Optional


class PasswordEncryptionService:
    """
    Service for encrypting and decrypting passwords using Fernet (symmetric encryption)
    with PBKDF2 for key derivation from user's master password.
    """
    
    def __init__(self):
        # Number of iterations for PBKDF2 (100,000 is recommended minimum)
        self.iterations = 200_000
        self.backend = default_backend()
    
    def generate_salt(self) -> bytes:
        """Generate a random salt for key derivation"""
        return secrets.token_bytes(32)
    
    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        """
        Derive an encryption key from the user's master password using PBKDF2
        
        Args:
            master_password: User's master password
            salt: Random salt for this specific password entry
            
        Returns:
            32-byte encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    
    def encrypt_password(self, password: str, master_password: str) -> Tuple[str, bytes]:
        """
        Encrypt a password using the user's master password
        
        Args:
            password: The password to encrypt
            master_password: User's master password for key derivation
            
        Returns:
            Tuple of (encrypted_password, salt)
        """
        # Generate a unique salt for this password
        salt = self.generate_salt()
        
        # Derive encryption key from master password
        key = self.derive_key(master_password, salt)
        
        # Create Fernet instance and encrypt
        f = Fernet(key)
        encrypted = f.encrypt(password.encode())
        
        # Return base64 encoded encrypted password and salt
        return base64.b64encode(encrypted).decode('utf-8'), salt
    
    def decrypt_password(self, encrypted_password: str, master_password: str, salt: bytes) -> Optional[str]:
        """
        Decrypt a password using the user's master password
        
        Args:
            encrypted_password: The encrypted password (base64 encoded)
            master_password: User's master password for key derivation
            salt: The salt used during encryption
            
        Returns:
            Decrypted password or None if decryption fails
        """
        try:
            # Derive the same encryption key
            key = self.derive_key(master_password, salt)
            
            # Create Fernet instance and decrypt
            f = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_password)
            decrypted = f.decrypt(encrypted_bytes)
            
            return decrypted.decode('utf-8')
        except Exception as e:
            # Log the error in production
            print(f"Decryption error: {e}")
            return None
    
    def re_encrypt_password(self, encrypted_password: str, old_master: str, 
                           new_master: str, salt: bytes) -> Optional[Tuple[str, bytes]]:
        """
        Re-encrypt a password when the master password changes
        
        Args:
            encrypted_password: Currently encrypted password
            old_master: Old master password
            new_master: New master password
            salt: Current salt
            
        Returns:
            Tuple of (new_encrypted_password, new_salt) or None if fails
        """
        # First decrypt with old master password
        decrypted = self.decrypt_password(encrypted_password, old_master, salt)
        if not decrypted:
            return None
        
        # Re-encrypt with new master password
        return self.encrypt_password(decrypted, new_master)
    
    def generate_secure_password(self, length: int = 16, 
                                include_symbols: bool = True,
                                include_numbers: bool = True,
                                include_uppercase: bool = True,
                                include_lowercase: bool = True,
                                exclude_ambiguous: bool = True) -> str:
        """
        Generate a cryptographically secure random password
        
        Args:
            length: Password length
            include_symbols: Include special characters
            include_numbers: Include numbers
            include_uppercase: Include uppercase letters
            include_lowercase: Include lowercase letters
            exclude_ambiguous: Exclude ambiguous characters (0, O, l, 1, etc.)
            
        Returns:
            Generated password
        """
        charset = ""
        
        if include_lowercase:
            chars = "abcdefghijkmnopqrstuvwxyz" if exclude_ambiguous else "abcdefghijklmnopqrstuvwxyz"
            charset += chars
        
        if include_uppercase:
            chars = "ABCDEFGHJKLMNPQRSTUVWXYZ" if exclude_ambiguous else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            charset += chars
        
        if include_numbers:
            chars = "23456789" if exclude_ambiguous else "0123456789"
            charset += chars
        
        if include_symbols:
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not charset:
            raise ValueError("At least one character type must be included")
        
        # Generate password using cryptographically secure random
        password = ''.join(secrets.choice(charset) for _ in range(length))
        
        # Ensure at least one character from each requested type
        required_chars = []
        if include_lowercase:
            chars = "abcdefghijkmnopqrstuvwxyz" if exclude_ambiguous else "abcdefghijklmnopqrstuvwxyz"
            required_chars.append(secrets.choice(chars))
        if include_uppercase:
            chars = "ABCDEFGHJKLMNPQRSTUVWXYZ" if exclude_ambiguous else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            required_chars.append(secrets.choice(chars))
        if include_numbers:
            chars = "23456789" if exclude_ambiguous else "0123456789"
            required_chars.append(secrets.choice(chars))
        if include_symbols:
            required_chars.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        # Replace random positions with required characters
        password_list = list(password)
        for i, char in enumerate(required_chars):
            if i < len(password_list):
                pos = secrets.randbelow(len(password_list))
                password_list[pos] = char
        
        return ''.join(password_list)
    
    def check_password_strength(self, password: str) -> dict:
        """
        Check the strength of a password
        
        Args:
            password: Password to check
            
        Returns:
            Dictionary with strength metrics
        """
        strength = {
            'score': 0,
            'length': len(password),
            'has_lowercase': bool(any(c.islower() for c in password)),
            'has_uppercase': bool(any(c.isupper() for c in password)),
            'has_numbers': bool(any(c.isdigit() for c in password)),
            'has_symbols': bool(any(not c.isalnum() for c in password)),
            'is_common': False,  # Would check against common password list
            'strength_label': 'Very Weak'
        }
        
        # Calculate score
        if strength['length'] >= 8:
            strength['score'] += 1
        if strength['length'] >= 12:
            strength['score'] += 1
        if strength['length'] >= 16:
            strength['score'] += 1
        if strength['has_lowercase']:
            strength['score'] += 1
        if strength['has_uppercase']:
            strength['score'] += 1
        if strength['has_numbers']:
            strength['score'] += 1
        if strength['has_symbols']:
            strength['score'] += 1
        
        # Determine strength label
        if strength['score'] <= 2:
            strength['strength_label'] = 'Very Weak'
        elif strength['score'] <= 3:
            strength['strength_label'] = 'Weak'
        elif strength['score'] <= 5:
            strength['strength_label'] = 'Medium'
        elif strength['score'] <= 6:
            strength['strength_label'] = 'Strong'
        else:
            strength['strength_label'] = 'Very Strong'
        
        return strength


# Global instance
encryption_service = PasswordEncryptionService()
