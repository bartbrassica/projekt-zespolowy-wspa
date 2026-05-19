/**
 * Client-side decryption utility for shared passwords
 * Mirrors the Python encryption_service.decrypt_password() function
 *
 * This implementation uses Web Crypto API (built into browsers)
 */

const PBKDF2_ITERATIONS = 200_000;
const KEY_LENGTH = 32;

/**
 * Convert base64 string to Uint8Array
 */
function base64ToBytes(base64: string): Uint8Array {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

/**
 * Convert base64url string to Uint8Array
 */
function base64urlToBytes(base64url: string): Uint8Array {
  // Convert base64url to standard base64
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  // Add padding if needed
  const padded = base64 + '==='.slice(0, (4 - base64.length % 4) % 4);
  return base64ToBytes(padded);
}

/**
 * Derive encryption key using PBKDF2 (matches Python implementation)
 *
 * Python does: base64.urlsafe_b64encode(kdf.derive(...))
 * Then Fernet decodes it back. We skip the encode/decode and use raw bytes.
 */
async function deriveKey(password: string, salt: Uint8Array): Promise<Uint8Array> {
  const encoder = new TextEncoder();
  const passwordBuffer = encoder.encode(password);

  // Import password as key material
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    'PBKDF2',
    false,
    ['deriveBits']
  );

  // Derive key using PBKDF2 (same as Python's kdf.derive())
  const derivedBits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: PBKDF2_ITERATIONS,
      hash: 'SHA-256',
    },
    keyMaterial,
    KEY_LENGTH * 8 // bits
  );

  return new Uint8Array(derivedBits);
}

/**
 * Decrypt Fernet token (matches Python Fernet.decrypt())
 *
 * Fernet token format:
 * Version (1 byte) || Timestamp (8 bytes) || IV (16 bytes) || Ciphertext || HMAC (32 bytes)
 */
async function decryptFernet(token: Uint8Array, key: ArrayBuffer): Promise<string> {
  // Fernet key split: Signing-key (first 16 bytes) || Encryption-key (last 16 bytes)
  const signingKey = new Uint8Array(key).slice(0, 16);
  const encryptionKey = new Uint8Array(key).slice(16, 32);

  // Verify token structure
  if (token.length < 57) { // minimum: 1 + 8 + 16 + 0 + 32
    throw new Error('Invalid Fernet token: too short');
  }

  // Extract components
  const version = token[0];
  if (version !== 0x80) {
    throw new Error('Invalid Fernet version');
  }

  // Extract HMAC (last 32 bytes) and payload
  const payload = token.slice(0, -32);
  const hmac = token.slice(-32);

  // Verify HMAC
  const signingKeyObj = await crypto.subtle.importKey(
    'raw',
    signingKey,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['verify']
  );

  const isValid = await crypto.subtle.verify(
    'HMAC',
    signingKeyObj,
    hmac,
    payload
  );

  if (!isValid) {
    throw new Error('Invalid HMAC signature');
  }

  // Extract IV and ciphertext
  const iv = payload.slice(9, 25); // bytes 9-24 (16 bytes)
  const ciphertext = payload.slice(25); // everything after IV

  // Decrypt using AES-128-CBC
  const aesKey = await crypto.subtle.importKey(
    'raw',
    encryptionKey,
    { name: 'AES-CBC' },
    false,
    ['decrypt']
  );

  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-CBC', iv: iv },
    aesKey,
    ciphertext
  );

  // Web Crypto API automatically removes PKCS7 padding!
  const decryptedArray = new Uint8Array(decrypted);

  // Convert to string (no manual padding removal needed)
  const decoder = new TextDecoder();
  return decoder.decode(decryptedArray);
}

/**
 * Decrypt password using the same algorithm as Python encryption_service
 *
 * @param encryptedPassword - Base64 encoded encrypted password (double encoded!)
 * @param encryptionKey - The random key used for encryption
 * @param saltBase64 - Base64 encoded salt
 * @returns Decrypted password or null if decryption fails
 */
export async function decryptPassword(
  encryptedPassword: string,
  encryptionKey: string,
  saltBase64: string
): Promise<string | null> {
  try {
    // Decode salt from base64
    const salt = base64ToBytes(saltBase64);

    // Derive key from encryption key and salt
    const derivedKey = await deriveKey(encryptionKey, salt);

    // Python does: base64.b64encode(f.encrypt())
    // f.encrypt() returns base64url-encoded Fernet token (as bytes)
    // base64.b64encode() wraps those bytes in standard base64

    // Step 1: Decode outer standard base64 layer
    const base64urlFernetBytes = base64ToBytes(encryptedPassword);

    // Step 2: Convert bytes to string (the base64url Fernet token)
    const base64urlFernetString = new TextDecoder('ascii').decode(base64urlFernetBytes);

    // Step 3: Decode base64url to get raw Fernet bytes (starting with 0x80)
    const fernetTokenBytes = base64urlToBytes(base64urlFernetString);

    // Decrypt using Fernet
    const decrypted = await decryptFernet(fernetTokenBytes, derivedKey);

    return decrypted;
  } catch (error) {
    console.error('Decryption error:', error);
    return null;
  }
}
