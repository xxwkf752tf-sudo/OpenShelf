import os, json, base64
from pathlib import Path

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

SERVICE_NAME = "OpenShelf"
CONFIG_FILENAME = "config.enc"


class SecureStorage:

    def __init__(self, appdata_dir=None):
        if appdata_dir is None:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            appdata_dir = Path(appdata) / "OpenShelf"
        self._data_dir = appdata_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._config_path = self._data_dir / CONFIG_FILENAME
        self._config_cache = {}

    def _derive_key(self, salt=None):
        machine_id = os.environ.get("COMPUTERNAME", "openshelf-default")
        user_name = os.environ.get("USERNAME", "user")
        password = (machine_id + ":" + user_name + ":OpenShelf-v1").encode()
        if salt is None:
            salt = b"OpenShelfSalt\x00\x01"
        kdf = PBKDF2(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        return kdf.derive(password), salt

    def get_credential(self, name):
        if HAS_KEYRING:
            try:
                return keyring.get_password(SERVICE_NAME, name)
            except Exception:
                pass
        config = self._load_config()
        encrypted = config.get(name)
        if encrypted and HAS_CRYPTO:
            try:
                return self._decrypt(encrypted)
            except Exception:
                pass
        return None

    def set_credential(self, name, value):
        if HAS_KEYRING:
            try:
                keyring.set_password(SERVICE_NAME, name, value)
                return
            except Exception:
                pass
        if HAS_CRYPTO:
            config = self._load_config()
            config[name] = self._encrypt(value)
            self._save_config(config)

    def delete_credential(self, name):
        if HAS_KEYRING:
            try:
                keyring.delete_password(SERVICE_NAME, name)
            except Exception:
                pass
        config = self._load_config()
        config.pop(name, None)
        self._save_config(config)

    def get_config(self, key, default=""):
        config = self._load_config()
        return config.get("cfg_" + key, default)

    def set_config(self, key, value):
        config = self._load_config()
        config["cfg_" + key] = value
        self._save_config(config)

    def _load_config(self):
        if self._config_cache:
            return self._config_cache
        if self._config_path.exists():
            try:
                raw = self._config_path.read_bytes()
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                data = {}
        else:
            data = {}
        self._config_cache = data
        return data

    def _save_config(self, config):
        self._config_cache = config
        temp = self._config_path.with_suffix(".tmp")
        temp.write_text(json.dumps(config, indent=2), encoding="utf-8")
        temp.replace(self._config_path)

    def _encrypt(self, plaintext):
        key, salt = self._derive_key()
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(salt + nonce + ct).decode()

    def _decrypt(self, ciphertext_b64):
        raw = base64.b64decode(ciphertext_b64)
        salt, nonce, ct = raw[:16], raw[16:28], raw[28:]
        key, _ = self._derive_key(salt)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ct, None).decode()
