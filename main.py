import math
import random

from kivy.app import App
from kivy.uix.widget import Widget


hex_str = "0123456789ABCDEF"
block_size_var = 1
encrypt_val_1 = 347
encrypt_val_2 = 1721


def mod_inverse_helper(a, b):
    q, r = a//b, a % b
    if r == 1:
        return 1, -1 * q
    u, v = mod_inverse_helper(b, r)
    return v, -1 * q * v + u


def mod_inverse(a, m):
    assert math.gcd(a, m) == 1, "You're trying to invert " + str(a) + " in mod " + str(m) + " and that doesn't work!"
    return mod_inverse_helper(m, a)[1] % m


def hex_to_dec(inpt):
    rn = 0
    i = 0
    inpt = inpt[::-1]
    while i < len(inpt):
        val = inpt.upper()[i]
        rn += hex_str.index(val) * (len(hex_str)**i)
        i += 1
    return rn


unicode_max = hex_to_dec("10FFFD")
utf_gt8 = []
print("Creating dynamic variables...")
for i in range(unicode_max):
    try:
        chr(i).encode("utf").decode()
    except UnicodeEncodeError:
        utf_gt8.append(i)
        print(f"{'%.2f' % ((len(utf_gt8) / 2048) * 100)}% complete")
print("Done")


def unicode_check(num):
    try:
        chr(num).encode("utf").decode()
    except UnicodeEncodeError:
        return True
    if 32 < num > unicode_max:
        return False


def let_to_dec(inpt):
    rn = 0
    i = 0
    for letter in inpt:
        rn += ord(letter) * (unicode_max**i)
        i += 1
    return rn


def dec_to_let(num, block_size):
    rs = ""
    nm = num
    for i in range(block_size):
        if (nm % unicode_max) == 0:
            nm //= unicode_max
            continue
        rs += chr(nm % unicode_max)
        nm //= unicode_max
    return rs


def encrypt(text, n, a, b):
    rs = ""
    if n > len(text):
        extra_letters = n - len(text)
    else:
        extra_letters = (n * math.ceil(len(text) / n)) - len(text)
    for i in range(extra_letters):
        text += chr(random.randint(32, ((i * n) + 32) % unicode_max))
    i = 0
    text = ("%03i" % extra_letters) + text
    print(text)
    while i < len(text):
        utf8 = False
        pair = text[i:n + i]
        pair_value = ((a * let_to_dec(pair)) + b) % (unicode_max**n)
        while utf8 is False:
            try:
                rs += dec_to_let(pair_value, n).encode("utf-8").decode()
                utf8 = True
            except UnicodeEncodeError:
                pair_value += 1
        print(rs)
        i += n
    return rs


def decrypt(text, n, a, b):
    rs = ""
    i = 0
    while i < len(text):
        pair = text[i:n + i]
        pair_value = ((let_to_dec(pair) - b) * mod_inverse(a, unicode_max**n)) % (unicode_max**n)
        rs += dec_to_let(pair_value, n)
        i += n
    return rs  # [0:len(rs) - extra_letters]


class UnicodeEncryption(Widget):
    pass


class EncryptionApp(App):
    def build(self):
        return UnicodeEncryption()

    def encrypt_text(self):
        text = self.root.ids.input.text
        with open("out.txt", "w") as file:
            try:
                file.write(str(let_to_dec(text)))
                file.write("\n")
                file.write(dec_to_let(let_to_dec(text), block_size_var))
                file.write("\n\n\n")
                enc = encrypt(text, block_size_var, encrypt_val_1, encrypt_val_2)
                file.write(enc)
                file.write("\n")
                file.write(decrypt(enc, block_size_var, encrypt_val_1, encrypt_val_2))
            except UnicodeEncodeError:
                pass
        # text = let_to_dec_blocks(text, block_size_var)
        # print(text)


if __name__ == '__main__':
    EncryptionApp().run()
