from cryptography.fernet import Fernet

# Загрузка ключа шифрования из файла
with open('secret.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

def encrypt_data(data):
    return cipher_suite.encrypt(data)

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data)
# .decode()