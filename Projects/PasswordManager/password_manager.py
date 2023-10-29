# ===== Load libraries
import argparse
import os
import json
import bson
import getpass
import secrets
import string
from pprint import pprint

# ======  Load crypography 
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import bcrypt

# =========== Functions ===================
# Function to check if a user exists
def user_exists(username):
    """
    Check if a user profile (JSON file) exists.
    Args:
        username (str): Username of the user.
    Returns:
        bool: True if the user profile exists, False otherwise.
    """

    # Folder path where to store user data
    folder_path = f'users'
    # Check if the folder exists and create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

    # Define the file path for the user data
    file_path = f'{folder_path}/{username}.json'

    return os.path.exists(file_path)

# ===== Function to generate a secure random password with customizable options
def generate_password(length=12, use_digits=True, use_special_chars=True):
    """
    Generate a secure random password with customizable options.
    Args:
        length (int): Length of the password (default is 16).
        use_digits (bool): Include digits in the password (default is True).
        use_special_chars (bool): Include special characters in the password (default is True).

    Returns:
        str: A strong, randomly generated password.
    """
    alphabet = string.ascii_letters
    if use_digits:
        alphabet += string.digits
    if use_special_chars:
        alphabet += string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

# ===== Generate prompt for the generate_password function that allows the user to choose from three options.
def prompt_for_password_option():
    """
    Prompt the user to choose a password generation option and generate a password accordingly.
    This function presents the user with three password generation options, each tailored for different security levels and requirements:
    1. Simple 8-character password: This option generates an 8-character password containing only letters (both uppercase and lowercase), providing basic security without digits or special characters.
    2. 12-character password: This option generates a 12-character password, including letters and digits, suitable for general use and moderate security.
    3. Very secure 16-character password: This option creates a highly secure 16-character password with a mix of letters (uppercase and lowercase), digits, and special characters, ideal for high-security scenarios.
    The user is prompted to select an option by entering 1, 2, or 3. After making a choice, the corresponding password is generated and returned as a string.
    Returns:
        str: The generated password based on the user's chosen option.
    """
    while True:
        print("Choose a password option:")
        print("1. Simple 8-character password (no digits, no special characters)")
        print("2. 12-character password (letters and digits only)")
        print("3. Very secure 16-character password (all allowed characters)")
        choice = input("Enter the option (1/2/3): ")

        if choice == '1':
            return generate_password(length=8, use_digits=False, use_special_chars=False)
        elif choice == '2':
            return generate_password(length=12, use_digits=True, use_special_chars=False)
        elif choice == '3':
            return generate_password(length=16, use_digits=True, use_special_chars=True)
        
        else:
            print("Invalid option. Please choose 1, 2, or 3.")

# ===== Function to hash a password
def hash_password(password, salt=None):
    """
    Hash a password using bcrypt, alghoritm designed for purpose-built password hashing.
    Args:
        password (str): Password to be hashed.
        salt (bytes, optional): Salt used for hashing (default is None).
    Returns:
        bytes: Hashed password.
        bytes: Salt used for hashing.
    """
    if salt is None:
        salt = bcrypt.gensalt()     # Returns <class 'bytes'> object
    hashed_password = bcrypt.hashpw(password.encode(), salt)    # Return <class 'bytes'> object

    return hashed_password.decode("utf-8"), salt.decode("utf-8")

# ===== Function to create a new user profile
def create_user(username, master_password):
    """
    Create a new user profile and store it in a JSON file.
    Set the desired file permissions. Be default 0o600 is used here as an example, which means read and write permissions for the owner only.
    Args:
        username (str): Username of the user.
        master_password (str): Master password of the user.
    Returns:
        None
    """
    salt = bcrypt.gensalt()             # return <class 'bytes'> object
    hashed_password, salt = hash_password(master_password, salt)
    user_data = {
        'username': username,
        'master_password': hashed_password,
        'salt': salt,
        'passwords': {}
    }

    # Folder path where to store user data
    folder_path = f'users'
    # Check if the folder exists and create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

    # Define the file path for the user data
    file_path = f'{folder_path}/{username}.json'
            
    # Save user profile, with file permisions.
    with open(file_path, 'w') as file:
        json.dump(user_data, file)
        # Define the desired file permissions (e.g., 0o600 for read-write permissions for the owner)
        permissions = 0o600
        os.chmod(file_path, permissions)
    
# ===== Function to load user profile
def load_user(username, master_password):
    """
    Load an existing user profile from a JSON file and verify the master password.
    Args:
        username (str): Username of the user.
        master_password (str): Master password to be verified.
    Returns:
        dict: User data if master password is correct, None if not.
    """
    with open(f'users/{username}.json', 'r') as file:
        user_data = json.load(file)
    
    # Encode the hashed password to  <class 'bytes'> object
    hashed_password = user_data['master_password'].encode()  
    if bcrypt.checkpw(master_password.encode(), hashed_password):
        return user_data
    else:
        print("Incorrect master password.")
        return None
    
# ===== Function to create Ferney key from master password.
def generate_fernet_key_from_master_password(master_password, salt):
    """
    Generate a Fernet key from a master password using PBKDF2HMAC.
    Fernet symmetric encryption algorithm, Fernet/secret key used to both encrypt and decrypt data
    Args:
        master_password (str): The master password.
        salt (bytes): A unique salt for key derivation.

    Returns:
        bytes: Fernet key derived from the master password.
    """
    password = master_password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        iterations=10000,  # You can adjust the number of iterations for stronger or weaker key derivation
        salt=salt.encode(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

    # Generate a random Fernet key
    fernet_key = Fernet.generate_key()


# ===== Function to encrypt a password
def encrypt_password(user_data, password):
    """
    Encrypt a password using a cryptographic key.
    Args:
        password (str): Password to be encrypted.
        encryption_key (bytes): Cryptographic key used for encryption.
    Returns:
        bytes: Encrypted password.
    """
    # Get master_password (hash) to derive encryption key
    master_hashed_password = user_data['master_password']
    salt = user_data['salt']
    # Fernet Key is generated from hashed master key.
    encryption_key = generate_fernet_key_from_master_password(master_hashed_password, salt)

    if encryption_key is None:
        print("Password cannot be encrypted because the Fernet key is missing.")
        return

    cipher = Fernet(encryption_key)
    encrypted_password = cipher.encrypt(password.encode())
    print(type(encrypted_password))
    return encrypted_password.decode("utf-8")

# ===== Function to decrypt an encrypted password
def decrypt_password(user_data, encrypted_password):
    """
    Decrypt an encrypted password using a cryptographic key.

    Args:
        encrypted_password (bytes): Encrypted password.
        encryption_key (bytes): Cryptographic key used for decryption.

    Returns:
        str: Decrypted password.
    """
    # Get master_password (hash) to derive encryption key
    master_hashed_password = user_data['master_password']
    salt = user_data['salt']
    # Fernet Key is generated from hashed master key.
    encryption_key = generate_fernet_key_from_master_password(master_hashed_password, salt)

    if encryption_key is None:
        print("Password cannot be encrypted because the Fernet key is missing.")
        return

    cipher = Fernet(encryption_key)
    decrypted_password = cipher.decrypt(encrypted_password).decode()
    return decrypted_password

# ===== Function to add a password
def insert_password(user_data, website, username, password, encrypt=False):
    """
    Add a new password entry to the user's profile.
    Args:
        user_data (dict): User's data loaded from the JSON file.
        website (str): Website or service name.
        username (str): Username for the website.
        password (str): Password for the website.
        encrypt (bool): Flag to indicate whether password encrypted.
    Returns:
        None
    """
    
    # If encrypt password requested.
    if encrypt:
        master_hashed_password = user_data['master_password']
        salt = user_data['salt']
        # Fernet Key is generated from hashed master key.
        fernet_key = generate_fernet_key_from_master_password(master_hashed_password, salt)

        if fernet_key is None:
            print("Password cannot be encrypted because the Fernet key is missing.")
            return
        cipher = Fernet(fernet_key)
        encrypted_password = cipher.encrypt(password.encode())
        password = encrypted_password.decode("utf-8")
        encrypted = True

    else:
        encrypted = False   

    # Add new password to user profile.     
    user_data['passwords'][website] = {
        'username': username,
        'password': password,
        'encrypt': encrypted
        }
    with open(f'{user_data["username"]}.json', 'w') as file:
        json.dump(user_data, file)

# ===== Function to display passwords
def display_passwords(user_data):
    """
    Display saved passwords from the user's profile.
    Args:
        user_data (dict): User's data loaded from the JSON file.
    Returns:
        None
    """
    if user_data['passwords']:
        for website, data in user_data['passwords'].items():
            print(f"Website: {website}")
            print(f"Username: {data['username']}")
            print(f"Password: {data['password']}")
            print(f"Encrypted: {data['encrypt']}")
            print()
    else:
        print("No passwords stored")

# Function to update a password
def update_password(user_data, website, new_password, encrypt=False):
    """
    Update an existing password in the user's profile.
    Args:
        user_data (dict): User's data loaded from the JSON file.
        website (str): Website or service name.
        new_password (str): New password for the website.
    Returns:
        None
    """

    if website in user_data['passwords']:
        # encrypt password if requested
        if encrypt:
            master_hashed_password = user_data['master_password']
            salt = user_data['salt']
            # Fernet Key is generated from hashed master key.
            fernet_key = generate_fernet_key_from_master_password(master_hashed_password, salt)

            if fernet_key is None:
                print("Password cannot be encrypted because the Fernet key is missing.")
                return
            
            cipher = Fernet(fernet_key)
            encrypted_password = cipher.encrypt(new_password.encode())
            new_password = encrypted_password.decode("utf-8")

        user_data['passwords'][website]['password'] = new_password
        user_data['passwords'][website]['encrypt'] = encrypt

        # update profile
        with open(f'{user_data["username"]}.json', 'w') as file:
            json.dump(user_data, file)
        print("Password updated successfully.")
    else:
        print(f"Website '{website}' not found in your passwords.")

# Function to delete a password
def delete_password(user_data, website):
    """
    Delete an existing password from the user's profile.
    Args:
        user_data (dict): User's data loaded from the JSON file.
        website (str): Website or service name to be deleted.
    Returns:
        None
    """
    if website in user_data['passwords']:
        del user_data['passwords'][website]
        with open(f'{user_data["username"]}.json', 'w') as file:
            json.dump(user_data, file)
        print("Password deleted successfully.")
    else:
        print(f"Website '{website}' not found in your passwords.")

 # ===== Function to export password data to a file
def export_passwords(user_data, filename, websites, include_usernames):
    """
    Export the user's password data to a file in a custom format.
    Args:
        user_data (dict): User's data containing passwords.
        filename (str): Name of the file to export data to.
        websites (list): List of websites to export passwords for.
        include_usernames (str): 'y' to include usernames, 'n' to exclude.

    Returns:
        None
    """
    exported_data = []
    for website in websites:
        password_data = user_data['passwords'].get(website, None)
        if password_data:
            website = website
            username = password_data.get('username', '') if include_usernames == 'y' else ''
            password = password_data.get('password', '')
            encrypted = password_data.get('encrypt', '')

            data_string = f"{website}:{username}:{password}:{encrypted}"
            exported_data.append(data_string)

    # Save to txt file
    with open(filename, 'w') as file:
        file.write('\n'.join(exported_data))
    print(f"Password data exported to '{filename}'.")

    # save to Json fil
    # with open(filename, 'w') as file:
    #     json.dump(user_data['passwords'], file)
    # print(f"Password data exported to '{filename}'.")

# ===== Function to import password data from a file
def import_passwords(user_data, filename):
    """
    Import password data from a file and update the user's profile.
    Args:
        user_data (dict): User's data containing passwords.
        filename (str): Name of the file to import data from.
    Returns:
        None
    """
    try:
        with open(filename, 'r') as file:
            imported_data = file.read().splitlines()

        # Define counter
        counter = 0
        for data_string in imported_data:
            website, username, password, encrypted = data_string.split(':')

            if website not in user_data['passwords']:
                user_data['passwords'][website] = {
                    'username': username,
                    'password': password,
                    'encrypt': encrypted
                }
                counter += 1
                
        with open(f'users/{user_data["username"]}.json', 'w') as user_file:
            json.dump(user_data, user_file)

        print(f"Done. {counter} password(s) data imported from '{filename}' and updated in your user file.")


    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred during the import: {e}")

# ===== Function to save user data to a BSON file
def save_userdata_to_bson(user_data, filename):
    """
    Save user data to a BSON (binary json) file.
    Args:
        user_data (dict): User data to be saved.
        filename (str): Name of the BSON file to save data to.
    Returns:
        None
    """

    with open(filename, 'wb') as file:
        bson_data = bson.BSON.encode(user_data)
        file.write(bson_data)
    print(f"User data saved to '{filename}' in BSON format.")

# ===== Function to read user data from a BSON file
def read_userdata_from_bson(filename):
    """
    Read user data from a BSON (binary json) file.
    Args:
        filename (str): Name of the BSON file to read data from.
    Returns:
        dict: User data read from the file.
    """
    try:
        with open(filename, 'rb') as file:
            bson_data = file.read()
            user_data = bson.BSON(bson_data).decode()
        return user_data
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None


# ===== Define main function
def main():
    # Parse input arguments
    parser = argparse.ArgumentParser(description="Password Manager")
    parser.add_argument("--user", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Master Password")
    args = parser.parse_args()

    username = args.user
    master_password = args.password
    # If user profile exists, check if master pasword is correct.
    if user_exists(username):    
        user_data = load_user(username, master_password)
        master_password = user_data['master_password']
        print(f"Welcome back to Password Manager")
        print(f"Your username: {user_data['username']}")
        print(f"You have { len(user_data['passwords']) } password(s) stored.")

        # If user passwords data exists then ask for options.
        if user_data:
            while True:
                print("\nPassword Manager Menu:")
                print("0. Generate new password")
                print("1. Add new password")
                print("2. Display saved passwords")
                print("3. Update password")
                print("4. Delete password")
                print("5. Encrypt password")
                print("6. Decrypt password")
                print("7. Export password")
                print("8. Import password")
                print("9. Save/Read profile to/from BSON file ")

                print("-1. Exit")
                choice = input("\nEnter your choice: ")

                # Generate a new password
                if choice == '0':
                    generated_password = prompt_for_password_option()
                    print("Generated Password:", generated_password)
                
                # Add a new password
                elif choice == '1':
                    website = input("Enter the website: ")
                    username = input("Enter the username: ")
                    password = input("Enter the password: ")
                    encrypt = input("Encrypt the password? (0/1): ")
                    encrypt = encrypt == '1'  # This line converts the user's input to a Boolean value
                    insert_password(user_data, website, username, password, encrypt)
                    print("Password added successfully.")

                # Display saved passwords
                elif choice == '2':
                    display_passwords(user_data)

                # Update Password  
                elif choice == '3':                   
                    website = input("Enter the website to update: ")
                    # check of website password exists
                    existing_password = user_data['passwords'].get(website, {}).get('password', None)
    
                    if existing_password is not None:
                        print(f"Existing Password: {existing_password}")                        
                        new_password = getpass.getpass("Enter the new password: ")
                        confirm_password = getpass.getpass("Confirm the new password: ")

                        if new_password == confirm_password:
                            
                            encrypt = input("Encrypt the password? (0/1): ")
                            encrypt = encrypt == '1'  # This line converts the user's input to a Boolean value
                            #insert_password(user_data, website, username, password, encrypt)
                            update_password(user_data, website, new_password, encrypt)                    
                            #print("Password updated successfully.")
                        
                        else:
                            print("Passwords do not match. Password update canceled.")
                    else:
                        print(f"Website '{website}' not found in your passwords.")

                # Delete Password ( and username for website )
                elif choice == '4':
                    website = input("Enter the website to delete: ")
                    delete_password(user_data, website)


                # Encrypt Password using Master Key
                elif choice == '5':
                    website = input("Enter the website to encrypt the password: ")
                    if website in user_data['passwords']:
                        if user_data['passwords'][website]['encrypt'] == "True":
                            print(f"Password already Encrypted")
                        else:
                            password = user_data['passwords'][website]['password']
                            #encrypted_password = encrypt_password(user_data, password)                        
                            update_password(user_data, website, password, True)   
                            #print(f"Encrypted Password: {encrypted_password}")
                    else:
                        print(f"Website '{website}' not found in your passwords.")

                # Decrypt Password using Master Key
                elif choice == '6':
                    website = input("Enter the website to decrypt the password: ")
                    if website in user_data['passwords']:
                        # Check if password is not decrypted
                        if user_data['passwords'][website]['encrypt'] == "False":
                            print(f"Password is already Decrypted")
                        else:
                            encrypted_password = user_data['passwords'][website]['password']
                            decrypted_password = decrypt_password(user_data, encrypted_password)
                            #print(f"Decrypted Password: {decrypted_password}")
                            update_password(user_data, website, decrypted_password, False)

                    else:
                        print(f"Website '{website}' not found in your passwords.")

                # Export Password to txt file
                elif choice == '7':
                    export_filename = input("Enter the filename.txt to export password data: ")           
                    websites = input("Enter the websites (comma-separated) for which you want to export passwords: ").strip().split(',')
                    include_usernames = input("Include usernames in the export? (y/n): ").strip().lower()
                    export_passwords(user_data, export_filename, websites, include_usernames)

                # Import Password
                elif choice == '8':
                    import_filename = input("Enter the filename to import password data: ")
                    import_passwords(user_data, import_filename)

                # Save/Read to/from BSON Password
                elif choice == '9':
                    save_or_read = input("Save (s) or Read (r) user-data from BSON file? ").strip().lower()
                    if save_or_read == 's':
                        save_userdata_to_bson(user_data, f"users/{user_data['username']}.bson")
                    elif save_or_read == 'r':
                        loaded_user_data = read_userdata_from_bson(f"users/{user_data['username']}.bson")
                    
                        if loaded_user_data:
                            print("Loaded User Data:")
                            #print(loaded_user_data)
                            pprint(loaded_user_data)
                    else:
                        print("Invalid choice. Please enter 's' to save or 'r' to read from BSON file.")
                
                # Exit 
                elif choice == '-1':
                    print("Exiting Password Manager.")
                    break

                else:
                    print("Invalid choice. Please select a valid option.")

    # If new user, then create new password config file.
    else:
        create_user(username, master_password)
        print(f"New User: {username} profile created. You can now log in.")

# run main function
if __name__ == "__main__":
    main()
