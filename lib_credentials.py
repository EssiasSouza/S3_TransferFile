from cryptography.fernet import Fernet
import json
import os
import threading

def starting_credencials(timeout_to_add_bucket):
    class TimeoutExpired(Exception):
        pass

    global credential_list
    credential_list = []

    def generate_key():
        key = Fernet.generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)

    def load_key():
        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
        if len(key) != 44:
            raise ValueError("Fernet key must be 32 url-safe base64-encoded bytes.")
        return key

    def encrypt_value(value, key):
        fernet = Fernet(key)
        return fernet.encrypt(value.encode())

    def decrypt_value(encrypted_value, key):
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_value).decode()

    def save_credentials(BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY):
        key = load_key()
        encrypted_BUCKET_NAME = encrypt_value(BUCKET_NAME, key)
        encrypted_AWS_ACCESS_KEY = encrypt_value(AWS_ACCESS_KEY, key)
        encrypted_AWS_SECRET_KEY = encrypt_value(AWS_SECRET_KEY, key)
        new_data = {
            'BUCKET_NAME': encrypted_BUCKET_NAME.decode(),  # Convert bytes to string for JSON serialization
            'AWS_ACCESS_KEY': encrypted_AWS_ACCESS_KEY.decode(),  # Convert bytes to string for JSON serialization
            'AWS_SECRET_KEY': encrypted_AWS_SECRET_KEY.decode()   # Convert bytes to string for JSON serialization
        }

        if os.path.exists('credentials.json'):
            with open('credentials.json', 'r') as json_file:
                data = json.load(json_file)
            data.append(new_data)
        else:
            data = [new_data]
        
        with open('credentials.json', 'w') as json_file:
            json.dump(data, json_file)

    def get_bucket_info():
        if not os.path.exists('credentials.json'):
            return []

        with open('credentials.json', 'r') as json_file:
            data = json.load(json_file)

        key = load_key()
        decrypted_data = []
        for entry in data:
            encrypted_BUCKET_NAME = entry.get('BUCKET_NAME')
            encrypted_AWS_ACCESS_KEY = entry.get('AWS_ACCESS_KEY')
            encrypted_AWS_SECRET_KEY = entry.get('AWS_SECRET_KEY')
            BUCKET_NAME = decrypt_value(encrypted_BUCKET_NAME.encode(), key) if encrypted_BUCKET_NAME else None
            AWS_ACCESS_KEY = decrypt_value(encrypted_AWS_ACCESS_KEY.encode(), key) if encrypted_AWS_ACCESS_KEY else None
            AWS_SECRET_KEY = decrypt_value(encrypted_AWS_SECRET_KEY.encode(), key) if encrypted_AWS_SECRET_KEY else None
            decrypted_data.append((BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY))
            credential_list.append(( BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY))

        return decrypted_data

    def add_new_credentials_group():
        
        BUCKET_NAME = input('Bucket name: ')
        AWS_ACCESS_KEY = input('AWS_ACCESS_KEY: ')
        AWS_SECRET_KEY = input('AWS_SECRET_KEY: ')
        save_credentials(BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY)
        print(f'-- New AWS Bucket "{BUCKET_NAME}" credentials was saved successfully.\n')

    def timed_input(prompt, timeout=int(timeout_to_add_bucket)):
        
        def input_with_timeout():
            nonlocal user_input
            user_input = input(prompt)

        user_input = None
        thread = threading.Thread(target=input_with_timeout)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            print("\nInput timed out. Assuming 'no' for setup other bucket.\n")
            raise TimeoutExpired("Timeout expired")
        return user_input.strip().lower()

    if not os.path.exists('secret.key'):
        generate_key()

    stored_credentials_groups = get_bucket_info()

    if not stored_credentials_groups:
        add_new_credentials_group()
    else:
        for i, (bucket, access_k, secret_k) in enumerate(stored_credentials_groups, start=1):
            print(f'-- Executing process to bucket: {bucket}')

    while True:
        try:
            add_more = timed_input('Do you want to add another group of credentials? (yes/no): ')
            add_more = add_more.upper()
            if add_more == 'YES' or add_more == 'Y':
                add_new_credentials_group()
            else:
                break
        except TimeoutExpired:
            break
    return credential_list