import math
import random
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.modalview import ModalView


hex_str = "0123456789ABCDEF"
block_size_var = 2
encrypt_val_1 = 347
encrypt_val_2 = 1721

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
    # text += chr(0) * extra_letters
    # print(extra_letters)
    extra_letters = functions.dec_to_let(extra_letters, 1)
    while len(extra_letters) < 3:
        extra_letters = chr(0) + extra_letters
    # print([ord(l) for l in extra_letters if ord(l) > 0])
    # print(let_to_dec("\u0000\u0000\u0001"))
    text = extra_letters + text
    # print([ord(l) for l in text])
    i = 0
    while i < len(text):
        utf8 = False
        pair = text[i:n + i]
        pair_value = ((a * functions.let_to_dec(pair)) + b) % (1114111**n)
        while utf8 is False:
            # try:
            #     rs += dec_to_let(pair_value, n).encode("utf-8").decode()
            #     utf8 = True
            # except UnicodeEncodeError:
            #     pair_value += 1
            while functions.dec_to_let(pair_value, n) is False:
                a = (a + 1) % 1114111
                b = (b + 1) % 1114111
                add += 1
                # This means that the higher n is, the longer the script will take to execute
                # TODO Add a note saying that (^) in the GUI
                pair_value = ((a * functions.let_to_dec(pair)) + b) % (1114111**n)
            # print(add, a, b)
            rs += functions.dec_to_let(pair_value, n)
            utf8 = True
        # print([[ord(l) for l in s] for s in [extra_letters, text, rs]])
        # print(rs)
        i += n
    # print([[ord(l) for l in rs], [ord(l) for l in rs[:1] + dec_to_let(add, 1) + rs[1:]]])
    return rs[:1] + functions.dec_to_let(add, 1) + rs[1:]


def decrypt(text, n, a, b):
    # print([ord(l) for l in text])
    # print([dec_to_let(l, 1) for l in [ord(l) for l in text]])
    # print(a, b)
    # add = ((let_to_dec(text[1]) - b) * mod_inverse(a, 1114111)) % 1114111
    add = ord(text[1])
    a = (a + add) % 1114111
    b = (b + add) % 1114111
    text = text[:1] + text[2:]
    # print(add, a, b)
    rs = ""
    i = 0
    nl = []
    while i < len(text):
        pair = text[i:n + i]
        # print([ord(letter) for letter in pair])
        # print(let_to_dec(pair), let_to_dec(pair[0]))
        pair_value = ((functions.let_to_dec(pair) - b) * functions.mod_inverse(a, 1114111**n)) % (1114111**n)
        rs += functions.dec_to_let(pair_value, n)
        # print([ord(letter) for letter in dec_to_let(pair_value, n)])
        i += n
    extra_letters = functions.let_to_dec("".join([l for l in rs[0:3] if ord(l) > 0]))
    print([ord(l) for l in rs])
    # print(extra_letters)
    # print(rs)
    # print([ord(l) for l in rs])
    return rs[3:len(rs) - extra_letters]


class functions():
    def mod_inverse_helper(a, b):
        q, r = a//b, a % b
        if r == 1:
            return 1, -1 * q
        u, v = functions.mod_inverse_helper(b, r)
        return v, -1 * q * v + u


    def mod_inverse(a, m):
        assert math.gcd(a, m) == 1, "You're trying to invert " + str(a) + " in mod " + str(m) + " and that doesn't work!"
        return functions.mod_inverse_helper(m, a)[1] % m


    def hex_to_dec(inpt):
        rn = 0
        i = 0
        inpt = inpt[::-1]
        while i < len(inpt):
            val = inpt.upper()[i]
            rn += hex_str.index(val) * (len(hex_str)**i)
            i += 1
        return rn


    def unicode_check(num):
        try:
            chr(num).encode("utf").decode()
        except UnicodeEncodeError:
            return True
        if num in exclude_chars:
            return True
        else:
            return False


    def let_to_dec(inpt):
        rn = 0
        i = 0
        for letter in inpt:
            rn += ord(letter) * (1114111**i)
            i += 1
        return rn


    def dec_to_let(num, block_size):
        rs = ""
        nm = num
        # block_size += 1
        for i in range(block_size):
            # if (nm % 1114111) == 0:
            #     nm //= 1114111
            #     continue
            if functions.unicode_check(nm % 1114111):
                return False
            else:
                rs += chr(nm % 1114111)
                nm //= 1114111
        return rs


class ScreenManager(ScreenManager):
    pass


class TextEncryption(Screen):
    def encrypt_text(self):
        global file
        text = self.ids.input.text
        with open("out.txt", "w", encoding="utf-8") as file:
        # file = open("out.txt", "w", encoding="utf-8")
            # for i in range(2):
            #     for j in range(1114111**i):
                    # try:
                        # text = dec_to_let(j, i)
                        # file.write(text)
                        # file.write("\n")
            enc = encrypt(text, block_size_var, encrypt_val_1, encrypt_val_2)
            file.write(enc)
            file.write("\n")
            file.write(str([ord(l) for l in enc]))
            # file.write("\n")
            dec = decrypt(enc, block_size_var, encrypt_val_1, encrypt_val_2)
            # file.write(dec)
            file.write("\n")
            file.write(dec)
            # file.write("\n")
            # file.write(str([ord(l) for l in dec]))
            file.write("\n")
            file.write(str(text == dec))
                        # if text == dec:
                        #     continue
                        # else:
                        #     file.write(f"{str(text == dec)}, {j}")
                        # file.write("\n\n")
                    # except:
                    #     print("NOOOOOOOOOOOOOOOOOOOOOOOO")
        print("done")
        # text = let_to_dec_blocks(text, block_size_var)
        # print(text)

    def decrypt_text(self):
        return self


class FilePicker(ModalView):
    def select_file(self, path, filename):
        file = open(os.path.join(path, filename[0]), "r", encoding="utf-8")
        print(file.readlines())



class EncryptionApp(App):
    def build(self):
        return ScreenManager()


if __name__ == '__main__':
    EncryptionApp().run()
    # TODO Add file handling, and a UI
    # TODO Add a GUI file picker

    # TODO If I get all missing assignments done, try to add a custom file picker,
    #  and even support for encrypting all file types.
