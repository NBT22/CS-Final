# General imports
import math
import random
import os

# Imports for the GUI
from kivy.config import Config  # For the window size.
from kivy.app import App  # For the application itself.
from kivy.factory import Factory  # For accessing other classes.
from kivy.uix.tabbedpanel import TabbedPanel  # For defining the GUI.
from kivy.uix.modalview import ModalView  # For popups.

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # Set the config for desktop (kivy supports mobile).


# Creating general variables
hex_str = "0123456789ABCDEF"
block_size_var = 5
exclude_chars = list(range(127, 160))
encrypt_file = False
decrypt_file = False
execute_file = False


# This function will encrypt a string using the given parameters.
def encrypt(text, n, a, b):
    rs = ""
    add = 0
    text_len = len(text) + 4  # + 4 because of my variable insertions.
    if n > text_len:  # If the text is too short, add random letters as filler.
        extra_letters = n - text_len
    else:
        extra_letters = (n * math.ceil(text_len / n)) - text_len
    for i in range(extra_letters):
        text += chr(random.randint(0, ((i * n) % 1114079)))
    extra_letters = Functions.dec_to_let(extra_letters, 1)
    while len(extra_letters) < 3:
        extra_letters = chr(0) + extra_letters
    text = extra_letters + text  # Add the encoded value defining how many letters are added to the start of the text.
    i = 0
    while i < len(text):  # Encrypt the text.
        utf8 = False
        pair = text[i:n + i]
        pair_value = ((a * Functions.let_to_dec(pair)) + b) % (1114111**n)
        while utf8 is False:  # Check if the pair is a valid UTF-8 character, and that it is not a control character.
            while Functions.dec_to_let_check(pair_value, n) is False:
                a = (a + 1) % 1114111
                b = (b + 1) % 1114111
                add += 1
                pair_value = ((a * Functions.let_to_dec(pair)) + b) % (1114111**n)  # Recalculate the pair value, if
                # the pair value does not create a valid UTF-8 character.
            rs += Functions.dec_to_let(pair_value, n)  # Add the pair to the encrypted string.
            utf8 = True
        i += n
    return Functions.dec_to_let(add, 1) + rs  # Add the number of times we had to recalculate the pair value to the
    # encrypted string, so it can be decrypted properly.


# This function will decrypt a string using the given parameters.
def decrypt(text, n, a, b):
    add = ord(text[0])
    a = (a + add) % 1114111
    b = (b + add) % 1114111
    text = text[1:]  # Remove the number of times we had to recalculate the pair value from the encrypted string.
    rs = ""
    i = 0
    while i < len(text):  # Decrypt the text.
        pair = text[i:n + i]
        pair_value = ((Functions.let_to_dec(pair) - b) * Functions.mod_inverse(a, 1114111**n)) % (1114111**n)
        rs += Functions.dec_to_let(pair_value, n)
        i += n
    extra_letters = (Functions.let_to_dec("".join([letter for letter in rs[0:3] if ord(letter) > 0]))) + 1
    # + 1 to remove the random hanging null byte that shouldn't exist...
    return rs[3:len(rs) - extra_letters]  # Remove the extra letters from the end, and return the decrypted text.


# This is a class for general functions.
class Functions:
    @staticmethod  # This is a static method, meaning that it does not need a parameter `self`.
    def mod_inverse_helper(a, b):
        q, r = a//b, a % b
        if r == 1:
            return 1, -1 * q
        u, v = Functions.mod_inverse_helper(b, r)
        return v, -1 * q * v + u

    # This function is for the decryption.
    @staticmethod
    def mod_inverse(a, m):
        assert math.gcd(a, m) == 1, f"You're trying to invert {str(a)} in mod {str(m)} and that doesn't work!"
        return Functions.mod_inverse_helper(m, a)[1] % m

    # This function will check if a string is part of UTF-8 and not part of the control characters I have excluded.
    @staticmethod
    def unicode_check(num):
        try:
            if MainUI.utf16:
                chr(num).encode("utf-16LE").decode()
            else:
                chr(num).encode("utf").decode()
        except UnicodeEncodeError:
            return True
        if num in exclude_chars:
            return True
        else:
            return False

    # This function will take a string and convert it to a base 10 value, using each letters' unicode values.
    @staticmethod
    def let_to_dec(inpt):
        rn = 0
        i = 0
        for letter in inpt:
            rn += ord(letter) * (1114111**i)
            i += 1
        return rn

    # This function will take a number and convert it to a string, using each letters' unicode values.
    @staticmethod
    def dec_to_let(num, block_size):
        rs = ""
        nm = num
        for i in range(block_size):
            rs += chr(nm % 1114111)
            nm //= 1114111
        return rs

    # This function will take a number, and check if the corresponding unicode letter is a valid UTF-8 character.
    @staticmethod
    def dec_to_let_check(num, block_size):
        nm = num
        for i in range(block_size):
            if Functions.unicode_check(nm % 1114111):
                return False
            else:
                return True
        return


encrypt_key_1 = "Encryption Key One"
encrypt_key_2 = "Encryption Key Two"
encrypt_val_1 = Functions.let_to_dec(encrypt_key_1) % 1114111  # The first encryption key.
encrypt_val_2 = Functions.let_to_dec(encrypt_key_2) % 1114111  # The second encryption key.


# This is the class for the GUI.
class MainUI(TabbedPanel):
    block_size_var = block_size_var
    encrypt_key_1 = encrypt_key_1
    encrypt_key_2 = encrypt_key_2
    utf16 = False
    output_file_name = "output.txt"  # The default output file name.
    code_execution = False  # This is a boolean that will be used to determine if the decrypted file should be executed.
        
    # Takes the text from the input field and encrypts it.
    def encrypt_text(self):
        try:
            with open(MainUI.output_file_name, "w", encoding="utf") as f:
                f.write(encrypt(self.ids.input.text, block_size_var, encrypt_val_1, encrypt_val_2))
        except UnicodeDecodeError:
            MainUI.utf16 = True
            with open(MainUI.output_file_name, "w", encoding="utf-16LE") as f:
                f.write(encrypt(self.ids.input.text, block_size_var, encrypt_val_1, encrypt_val_2))

    # Selects the active file.
    @staticmethod
    def select_file(path, filename):
        global file  # Accessed by encrypt_file() and decrypt_file()
        file = open(os.path.join(path, filename[0]), "r", encoding="utf-16LE")

    # Encrypts the selected file.
    @staticmethod
    def encrypt_file():
        # try:
        #     with open(MainUI.output_file_name, "w", encoding="utf") as f:  # Output file. This will automatically close.
        #         file.seek(0)
        #         f.write(encrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2))  # Write the encrypted string.
        # except UnicodeDecodeError:
        #     MainUI.utf16 = True
        file.seek(0)
        with open(MainUI.output_file_name, "w", encoding="utf-32") as f:
            while True:
                char = file.read(1)
                if not char:
                    break
                print('{:b}'.format(ord(chr)))
                # f.write(encrypt('{0:08b}'.format(ord(chr)), block_size_var, encrypt_val_1, encrypt_val_2))
                # f.write(encrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2))
        file.close()  # Close the input file.

    # Decrypts the selected file.
    @staticmethod
    def decrypt_file():
        try:
            with open(MainUI.output_file_name, "w", encoding="utf") as f:  # Output file. This will automatically close.
                f.write(decrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2))  # Write the decrypted string.
        except UnicodeDecodeError:
            MainUI.utf16 = True
            with open(MainUI.output_file_name, "w", encoding="utf-16LE") as f:
                f.write(decrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2))
        file.close()  # Close the input file.

    # This function will decrypt the selected file and execute it.
    @staticmethod
    def execute_file():
        exec(decrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2))  # Decrypt the file and execute it.
        file.close()  # Close the input file.

    # Selects the output file, decrypts the selected file, and executes it.
    @staticmethod
    def pick_file_execute():
        global execute_file  # Accessed by FilePicker().
        Factory.FilePicker().open()  # Open the file picker popup.
        execute_file = True  # This will be used to determine if the file should be executed.

    # Selects the output file and encrypts it.
    @staticmethod
    def pick_file_encrypt():
        global encrypt_file  # Accessed by FilePicker().
        Factory.FilePicker().open()  # Open the file picker popup.
        encrypt_file = True  # This will be used to determine that the file should be encrypted immediately.

    # Selects the output file and decrypts it.
    @staticmethod
    def pick_file_decrypt():
        global decrypt_file  # Accessed by FilePicker().
        Factory.FilePicker().open()  # Open the file picker popup.
        decrypt_file = True  # This will be used to determine that the file should be decrypted immediately.

    # This saves the current changes to the settings.
    def save(self):
        # Global vars so that the rest of the program can access the changed settings.
        global block_size_var
        global encrypt_key_1
        global encrypt_key_2
        global encrypt_val_1
        global encrypt_val_2
        value_error = False

        # Sets the global vars to the current values in the GUI.
        try:  # Check if the block size is a valid integer.
            if int(self.ids.block_size.text) > 2:
                block_size_var = int(self.ids.block_size.text)
            else:
                value_error = True  # Error tracking.
                Factory.BlockSizeError().open()  # Open the block size error popup.
        except ValueError:
            value_error = True  # Error tracking.
            self.ids.block_size.text = str(block_size_var)  # Reset the block size to the previous value.
            Factory.BlockSizeError().open()  # Open the block size error popup.
        encrypt_key_1_tmp = self.ids.encrypt_key_1.text
        encrypt_key_2 = self.ids.encrypt_key_2.text
        encrypt_val_1_tmp = Functions.let_to_dec(encrypt_key_1_tmp) % 1114111
        encrypt_val_2 = Functions.let_to_dec(encrypt_key_2) % 1114111
        try:  # Check if the encryption key is valid for the block size in mod_inverse.
            Functions.mod_inverse(encrypt_val_1_tmp, 1114111**block_size_var)
            encrypt_key_1 = encrypt_key_1_tmp
            encrypt_val_1 = encrypt_val_1_tmp
        except AssertionError:
            value_error = True  # Error tracking.
            self.ids.encrypt_key_1.text = encrypt_key_1  # Reset the encryption key to the previous value.
            Factory.KeyError().open()  # Open the key error popup.
        MainUI.output_file_name = self.ids.output_file_name.text
        if self.ids.output_to_file.state == "normal":
            value_error = True  # Error tracking.
            self.ids.output_to_file.state = "down"  # Reset the output to file button down.
            Factory.FileOutputError().open()  # Open the file output error popup.
        if self.ids.code_execution.state == "down":  # If the button is pressed.
            MainUI.code_execution = True  # This will be used to determine if the decrypted file should be executed.
        else:
            MainUI.code_execution = False  # This will be used to determine if the decrypted file should be executed.
        if not value_error:
            Factory.SavedSettings().open()  # If there are no errors, open the saved settings popup.

    # This discards the current changes to the settings.
    def discard(self):  # Discard the changes to the settings.
        self.ids.block_size.text = str(block_size_var)  # Reset the block size to the previous value.
        self.ids.encrypt_key_1.text = encrypt_key_1  # Reset the 1st encryption key to the previous value.
        self.ids.encrypt_key_2.text = encrypt_key_2  # Reset the 2nd encryption key to the previous value.
        self.ids.output_file_name.text = MainUI.output_file_name  # Reset the output file name to the previous value.
        self.ids.output_to_file.state = "down"  # Reset the output to file button to the down state (it should never
        # be in the normal state, because I seemingly can only output to file).
        self.ids.code_execution.state = "down" if MainUI.code_execution else "normal"  # Reset the code execution
        # button to the previous value.
        Factory.DiscardedSettings().open()  # Open the discarded settings popup.


# This is the filepicker popup.
class FilePicker(ModalView):

    # This is the function that is called when the user selects a file.
    def file_select(self, path, filename):
        global encrypt_file
        global decrypt_file
        global execute_file
        try:
            MainUI.select_file(path, filename)  # Select the file.
            if encrypt_file:  # If the file should be encrypted.
                MainUI.encrypt_file()  # Encrypt the file.
                encrypt_file = False  # Reset the encrypt_file variable.
            elif decrypt_file:  # If the file should be decrypted.
                MainUI.decrypt_file()  # Decrypt the file.
                decrypt_file = False  # Reset the decrypt_file variable.
            elif execute_file:  # If the file should be executed.
                MainUI.execute_file()  # Execute the file.
                execute_file = False  # Reset the execute_file variable.
        except IndexError:
            Factory.FileError().open()  # Open the file picking error popup.
        self.dismiss()  # Close the popup.


class EncryptionApp(App):  # This is the app itself.
    def build(self):
        return MainUI()  # Display the GUI.


if __name__ == '__main__':
    EncryptionApp().run()  # Run the app.
