# TODO encrypt_val_2 shows up in 2 places in the encrypted text. FIX!!!
import math
import random
import os

from kivy.config import Config
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.modalview import ModalView
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


hex_str = "0123456789ABCDEF"
block_size_var = 2
# TODO Implement into GUI using a number input field, to allow for more range than a slider.
encrypt_val_1 = ord("ś")  # 347
# Functions.let_to_dec("ś")
encrypt_val_2 = ord("ь")  # 1100
# TODO encrypt_val_2 shows up in 2 places in the encrypted text. FIX!!!
# Functions.let_to_dec("ь")
# TODO Fully implement these into the GUI, using (let_to_dec() % 1114111)


exclude_chars = []
exclude_chars.extend(list(range(127, 160)))
exclude_chars.extend(list(range(8206, 8208)))


def encrypt(text, n, a, b):
    rs = ""
    add = 0
    text_len = len(text) + 4
    if n > text_len:
        extra_letters = n - text_len
    else:
        extra_letters = (n * math.ceil(text_len / n)) - text_len
    for i in range(extra_letters):
        text += chr(random.randint(0, ((i * n) % 1114079)))
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
            while Functions.dec_to_let(pair_value, n) is False:
                a = (a + 1) % 1114111
                b = (b + 1) % 1114111
                add += 1
                # This means that the higher n is, the longer the script will take to execute
                # TODO Add a note saying that (^) in the GUI
                pair_value = ((a * Functions.let_to_dec(pair)) + b) % (1114111**n)
            rs += Functions.dec_to_let(pair_value, n)
            utf8 = True
        i += n
    return Functions.dec_to_let(add, 1) + rs
# TODO encrypt_val_2 shows up in 2 places in the encrypted text. FIX!!!


def decrypt(text, n, a, b):
    add = ord(text[0])
    a = (a + add) % 1114111
    b = (b + add) % 1114111
    text = text[1:]
    rs = ""
    i = 0
    nl = []
    while i < len(text):
        pair = text[i:n + i]
        pair_value = ((Functions.let_to_dec(pair) - b) * Functions.mod_inverse(a, 1114111**n)) % (1114111**n)
        rs += Functions.dec_to_let(pair_value, n)
        i += n
    extra_letters = (Functions.let_to_dec("".join([l for l in rs[0:3] if ord(l) > 0]))) + 1  # (+ 1) to remove the random hanging null byte...
    return rs[3:len(rs) - extra_letters]


class Functions:
    @staticmethod
    def mod_inverse_helper(a, b):
        q, r = a//b, a % b
        if r == 1:
            return 1, -1 * q
        u, v = Functions.mod_inverse_helper(b, r)
        return v, -1 * q * v + u

    @staticmethod
    def mod_inverse(a, m):
        assert math.gcd(a, m) == 1, "You're trying to invert " + str(a) + " in mod " + str(m) + " and that doesn't work!"
        return Functions.mod_inverse_helper(m, a)[1] % m

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

    @staticmethod
    def let_to_dec(inpt):
        rn = 0
        i = 0
        for letter in inpt:
            rn += ord(letter) * (1114111**i)
            i += 1
        return rn

    @staticmethod
    def dec_to_let(num, block_size):
        rs = ""
        nm = num
        for i in range(block_size):
            if Functions.unicode_check(nm % 1114111):
                return False
            else:
                rs += chr(nm % 1114111)
                nm //= 1114111
        return rs


print(Functions.dec_to_let(347, 1), Functions.dec_to_let(1100, 1))


class MainUI(TabbedPanel):
    def encrypt_text(self):
        with open("out.txt", "w", encoding="utf-8") as file:
            file.write(encrypt(self.ids.input.text, block_size_var, encrypt_val_1, encrypt_val_2))

    def decrypt_text(self):
        self.ids.input.text = decrypt(self.ids.input.text, block_size_var, encrypt_val_1, encrypt_val_2)

    @staticmethod
    def select_file(path, filename):
        global file  # Accessed by encrypt_file() and decrypt_file()
        file = open(os.path.join(path, filename[0]), "r", encoding="utf-8")

    @staticmethod
    def encrypt_file():
        # file.seek(0)
        enc = encrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2)
        file.close()

    @staticmethod
    def decrypt_file():
        # file.seek(0)
        dec = decrypt(file.read(), block_size_var, encrypt_val_1, encrypt_val_2)
        file.close()


class MainSettings(ModalView):
    def save(self):
        global block_size_var
        block_size_var = self.ids.block_size.text
        print(block_size_var)
        self.dismiss()


class EncryptionApp(App):
    def build(self):
        return MainUI()


# TODO encrypt_val_2 shows up in 2 places in the encrypted text. FIX!!!
if __name__ == '__main__':
    EncryptionApp().run()
    # TODO Add file handling

    # TODO If I get all missing assignments done, try to add a custom file picker,
    #  and even support for encrypting all file types.
