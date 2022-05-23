import math
import random
import sys

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


# utf_gt8 = []
print("Creating dynamic variables...")
# percent = 0
# for num in range(1114111):
#     try:
#         chr(num).encode("utf").decode()
#     except UnicodeEncodeError:
#         utf_gt8.append(chr(num))
#     finally:
#         if '%.2f' % ((num / 1114111) * 100) != percent:
#             percent = '%.2f' % ((num / 1114111) * 100)
#             print(f"\r{percent}% complete", end='', flush=True)
exclude_chars = []
exclude_chars.extend(list(range(32)))
exclude_chars.extend(list(range(127, 161)))
exclude_chars.extend(list(range(8206, 8208)))
print(exclude_chars)
print("Done")
# print(utf_gt8)

def unicode_check(num):
    # Currently, this returns True if it is throwing an error, else returns False. Need to decide how I want it/how I
    # will use it.
    try:
        chr(num).encode("utf").decode()
    except UnicodeEncodeError:
        return True
    if num in exclude_chars:
        return True
    else:
        return False


print(unicode_check(32))


def let_to_dec(inpt):
    rn = 0
    i = 0
    for letter in inpt:
        rn += ord(letter) * (1114111**i)
        i += 1
    return rn


print(let_to_dec(chr(1114111)*3))


def dec_to_let(num, block_size):
    rs = ""
    nm = num
    for i in range(block_size):
        if (nm % 1114111) == 0:
            nm //= 1114111
            continue
        rs += chr(nm % 1114111)
        nm //= 1114111
    return rs


def encrypt(text, n, a, b):
    rs = ""
    if n > len(text):
        extra_letters = n - len(text)
    else:
        extra_letters = (n * math.ceil(len(text) / n)) - len(text)
    for i in range(extra_letters):
        text += chr(random.randint(32, ((i * n) + 32) % 1114111))
    i = 0
    text = ("%03i" % extra_letters) + text
    print(text)
    while i < len(text):
        utf8 = False
        pair = text[i:n + i]
        pair_value = ((a * let_to_dec(pair)) + b) % (1114111**n)
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
        pair_value = ((let_to_dec(pair) - b) * mod_inverse(a, 1114111**n)) % (1114111**n)
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
