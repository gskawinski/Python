Password Manager Project

This Python-based Password Manager is a command-line tool designed to help users securely store, manage, and manipulate their passwords. It provides a range of features, including password generation, encryption, decryption, updating, and exporting.

Users can log in with their master passwords and manage their passwords. 

Menu Options:
0. Generate new password
1. Add new password
2. Display saved passwords
3. Update Password
4. Delete Password
5. Encrypt Password
6. Decrypt Password
7. Export Password
8. Import Password
9. Save/Read to/from BSON Password

Usage:
- Choose options by entering the corresponding number.
- To generate secure passwords, use option 0.
- To add, update, and manage passwords, select options 1-6.
- Export and import password data using options 7 and 8.
- Option 9 allows you to save or read user data in BSON format.

Note:
- All user data can be securely encrypted, where encryption key is based on the user master password.
- You can specify whether to encrypt passwords on addition or update.
- User data is saved in JSON format by default, but you can switch to BSON with option 9.

Please take a look at a screenshoot photo of the operation.

Feel free to customize and expand this password manager to suit your needs. Always ensure the security of your master password and user data.

Author: [Greg Skawinski]
Date: [12-11-2021]

How to run it?

If a user doesn't exist, a new profile is created, storing the master password as a hash with a unique salt.

- Creating a New User Profile
Create a new user profile by specifying a username and a master password. The script will then create a user JSON file for this new user.
The profile file is written with the file permision:  0o600 for read-write permissions for the owner

python password_manager.py --user 'username' --password 'master_password'
example: python password_manager.py --user john --password mysecretmasterpassword

- Logging In as an existing user

python password_manager.py --user 'username' --password 'master_password'
example: python password_manager.py --user gregory --password mysecretmasterpassword

Some terminology explained.

- Encryption: Password managers use encryption to securely store your passwords. When you save a password in a password manager, it's encrypted using a cryptographic key. To access your stored passwords, you need to provide a master password or key that is used to decrypt the stored passwords. This allows you to retrieve your original passwords in a usable form when needed. Encryption is a two-way process, meaning you can both encrypt and decrypt the data.

- Hashing is a one-way process. Passwords are hashed before being stored, and the hash cannot be reversed to retrieve the original password. When you log in to a system, your entered password is hashed and compared to the stored hash. If they match, you're granted access. However, you can't retrieve the original password from the hash, making it unsuitable for a password manager where you need to retrieve stored passwords.

- Salt is a random value that is added to data before it is hashed or encrypted. It's like adding a pinch of salt to your food to enhance its flavor.

In the context of security and cryptography, a salt is used to make it more difficult for attackers to guess or crack passwords. When a salt is added to a password before hashing it, even if two people have the same password, their hashed values will be different because of the unique salt. This adds an extra layer of security, making it harder for attackers to use precomputed tables (rainbow tables) to reverse the hashed values and discover the original passwords. In summary, a salt is a random value added to data for security purposes, specifically to protect sensitive information like passwords. It ensures that even when two pieces of data are the same, their hashed or encrypted forms are different due to the unique salt, making it more challenging for attackers to break the security measures.

