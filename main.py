# General imports
import math
import random
import os

# Imports for the GUI
from kivy.config import Config
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.modalview import ModalView
from sympy import GoldenRatio
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # Set the config for desktop


# Creating general variables
hex_str = "0123456789ABCDEF"
block_size_var = 2
exclude_chars = list(range(127, 160))


# This function will encrypt a string using the given parameters.
def encrypt(text, n, a, b):
    rs = ""
    add = 0
    text_len = len(text) + 4
    if n > text_len:
        extra_letters = n - text_len
    else:
        extra_letters = (n * math.ceil(text_len / n)) - text_len  # TODO DEVIDE BY 0 ERROR if N is 0
    for i in range(extra_letters):
        text += chr(random.randint(0, ((i * n) % 1114079)))
    # print(extra_letters)
    extra_letters = Functions.dec_to_let(extra_letters, 1)
    while len(extra_letters) < 3:
        extra_letters = chr(0) + extra_letters
    text = extra_letters + text
    i = 0
    while i < len(text):
        utf8 = False
        pair = text[i:n + i]
        pair_value = ((a * Functions.let_to_dec(pair)) + b) % (1114111**n)
        while utf8 is False:
            while Functions.dec_to_let_check(pair_value, n) is False:
                a = (a + 1) % 1114111
                b = (b + 1) % 1114111
                add += 1
                # This means that the higher n is, the longer the script will take to execute
                # TODO Add a note saying that (^) in the GUI
                pair_value = ((a * Functions.let_to_dec(pair)) + b) % (1114111**n)
            rs += Functions.dec_to_let(pair_value, n)
            utf8 = True
        i += n
    # print([ord(l) for l in rs])
    # print([ord(l) for l in text])
    return Functions.dec_to_let(add, 1) + rs
# TODO encrypt_val_2 shows up in 2 places in the encrypted text. FIX!!!


# This function will decrypt a string using the given parameters.
def decrypt(text, n, a, b):
    add = ord(text[0])
    a = (a + add) % 1114111
    b = (b + add) % 1114111
    text = text[1:]
    rs = ""
    i = 0
    while i < len(text):
        utf8 = False
        pair = text[i:n + i]
        print([ord(l) for l in pair])
        pair_value = ((Functions.let_to_dec(pair) - b) * Functions.mod_inverse(a, 1114111**n)) % (1114111**n)
        # while utf8 is False:
        #     while Functions.dec_to_let(pair_value, n) is False:
        #         a = (a + 1) % 1114111
        #         b = (b + 1) % 1114111
        #         add += 1
        #         # This means that the higher n is, the longer the script will take to execute
        #         # TODO Add a note saying that (^) in the GUI
        #         pair_value = ((Functions.let_to_dec(pair) - b) * Functions.mod_inverse(a, 1114111**n)) % (1114111**n)
        #     rs += Functions.dec_to_let(pair_value, n)
        #     utf8 = True
        rs += Functions.dec_to_let(pair_value, n)
        i += n
    extra_letters = (Functions.let_to_dec("".join([l for l in rs[0:3] if ord(l) > 0]))) + 1  # (+ 1) to remove the random hanging null byte...
    return rs[3:len(rs) - extra_letters]


# This is a class for general functions.
class Functions:
    @staticmethod  # This is a static method, meaning that it can be called without an instance of the class.
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

    # This function will convert a hexadecimal value to a base 10 value.
    @staticmethod
    def hex_to_dec(inpt):
        rn = 0
        i = 0
        inpt = inpt[::-1]
        while i < len(inpt):
            val = inpt.upper()[i]
            rn += hex_str.index(val) * (len(hex_str)**i)
            i += 1
        return rn

    # This function will check if a string is part of UTF-8 and not part of the control characters I have excluded.
    @staticmethod
    def unicode_check(num):
        try:
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
    
    @staticmethod
    def dec_to_let_check(num, block_size):
        nm = num
        for i in range(block_size):
            if Functions.unicode_check(nm % 1114111):
                return False
            else:
                return True
        return


# TODO Implement into GUI using a number input field, to allow for more range than a slider.
encrypt_key_1 = "Encryption Key One"
encrypt_key_2 = "Encryption Key Two"
encrypt_val_1 = Functions.let_to_dec(encrypt_key_1) % 1114111
encrypt_val_2 = Functions.let_to_dec(encrypt_key_2) % 1114111
# TODO Fully implement these into the GUI, using (let_to_dec() % 1114111).


# This is the class for the GUI.
class MainUI(TabbedPanel):
    block_size_var = block_size_var
    encrypt_key_1 = encrypt_key_1
    encrypt_key_2 = encrypt_key_2
    output_to_file = True
        
    # Takes the text from the input field and encrypts it.
    def encrypt_text(self):
        with open("out.txt", "w", encoding="utf-8") as f:
            enc = encrypt(self.ids.input.text, block_size_var, encrypt_val_1, encrypt_val_2)
            dec = decrypt(enc, block_size_var, encrypt_val_1, encrypt_val_2)
            if self.ids.input.text == dec:
                f.write(str(self.ids.input.text == dec))
            else:
                f.write(str(self.ids.input.text == dec))
                f.write("\n")
                f.write(str(dec))

    # Takes the text from the input field and decrypts it.
    def decrypt_text(self):
        self.ids.input.text = decrypt(self.ids.input.text, block_size_var, encrypt_val_1, encrypt_val_2)

    # Selects the active file.
    @staticmethod
    def select_file(path, filename):
        global file  # Accessed by encrypt_file() and decrypt_file()
        file = open(os.path.join(path, filename[0]), "r", encoding="utf-8")

    # Encrypts the selected file.
    @staticmethod
    def encrypt_file():
        # file.seek(0)
        global enc
        enc = encrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2)
        if MainUI.output_to_file:
            with open("out.txt", "w", encoding="utf-8") as f:
                f.write(enc)
        else:
            print(enc)
        file.close()

    # Decrypts the selected file.
    @staticmethod
    def decrypt_file():
        # file.seek(0)
        read = file.read()
        dec = decrypt(read, block_size_var, encrypt_val_1, encrypt_val_2)
        if MainUI.output_to_file:
            print(dec)
            with open("out.txt", "w", encoding="utf-8") as f:
                f.write(read)
        else:
            print(dec)
        file.close()

    # This saves the current changes to the settings.
    def save(self):
        # Global vars so that the rest of the program can access the changed settings.
        global block_size_var
        global encrypt_key_1
        global encrypt_key_2
        global encrypt_val_1
        global encrypt_val_2
        # Sets the global vars to the current values in the GUI.
        block_size_var = abs(int(self.ids.block_size.text))  # TODO Don't allow 0.
        encrypt_key_1 = self.ids.encrypt_key_1.text
        encrypt_key_2 = self.ids.encrypt_key_2.text
        encrypt_val_1 = Functions.let_to_dec(encrypt_key_1) % 1114111
        encrypt_val_2 = Functions.let_to_dec(encrypt_key_2) % 1114111
        MainUI.output_to_file = True if self.ids.output_to_file.state == "down" else False
        # TODO Save the settings to a file.
        # TODO Add a modal dialog confirming that the settings have been saved.

    # This discards the current changes to the settings.
    def discard(self):
        self.ids.block_size.text = str(block_size_var)
        self.ids.encrypt_key_1.text = encrypt_key_1
        self.ids.encrypt_key_2.text = encrypt_key_2
        self.ids.output_to_file.state = "down" if MainUI.output_to_file else "normal"


class EncryptionApp(App):
    def build(self):
        return MainUI()


if __name__ == '__main__':
    for i in range(1, 100):
        print(decrypt(encrypt("asd", i, encrypt_val_1, encrypt_val_2), i, encrypt_val_1, encrypt_val_2) == "asd")
    EncryptionApp().run()
    # TODO Add file handling

    # TODO If I get all missing assignments done, try to add a custom file picker,
    #  and even support for encrypting all file types.
