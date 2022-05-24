import math
import random
import sys

from kivy.app import App
from kivy.uix.widget import Widget


hex_str = "0123456789ABCDEF"
block_size_var = 10
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


exclude_chars = []
# exclude_chars.extend(list(range(32)))
exclude_chars.extend(list(range(127, 160)))
exclude_chars.extend(list(range(8206, 8208)))
for n in exclude_chars:
    print(chr(n), n)
# print(utf_gt8)


def unicode_check(num):
    try:
        chr(num).encode("utf").decode()
    except UnicodeEncodeError:
        return True
    if num in exclude_chars:
        return True
    else:
        return False


# print(unicode_check(32))


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
        if unicode_check(nm % 1114111):
            return False
        else:
            rs += chr(nm % 1114111)
            nm //= 1114111
    return rs


def encrypt(text, n, a, b):
    global add
    rs = ""
    add = 0
    text_len = len(text) + 4
    if n > text_len:
        extra_letters = n - text_len
    else:
        extra_letters = (n * math.ceil(text_len / n)) - text_len
    for i in range(extra_letters):
        text += chr(random.randint(32, ((i * n) + 32) % 1114111))
    extra_letters = dec_to_let(extra_letters, 1)
    while len(extra_letters) < 3:
        extra_letters = chr(0) + extra_letters
    text = chr(8237) + extra_letters + text
    i = 0
    while i < len(text):
        utf8 = False
        pair = text[i:n + i]
        pair_value = ((a * let_to_dec(pair)) + b) % (1114111**n)
        while utf8 is False:
            # try:
            #     rs += dec_to_let(pair_value, n).encode("utf-8").decode()
            #     utf8 = True
            # except UnicodeEncodeError:
            #     pair_value += 1
            while dec_to_let(pair_value, n) is False:
                a = (a + 1) % 1114111
                b = (b + 1) % 1114111
                add += 1
                pair_value = ((a * let_to_dec(pair)) + b) % (1114111**n)
            # print(add)
            rs += dec_to_let(pair_value, n)
            utf8 = True
        # print(rs)
        i += n
    return rs


def decrypt(text, n, a, b):
    global add
    a = (a + add) % 1114111
    b = (b + add) % 1114111
    rs = ""
    i = 0
    while i < len(text):
        pair = text[i:n + i]
        # print([ord(letter) for letter in pair])
        # print(let_to_dec(pair), let_to_dec(pair[0]))
        pair_value = ((let_to_dec(pair) - b) * mod_inverse(a, 1114111**n)) % (1114111**n)
        rs += dec_to_let(pair_value, n)
        # print([ord(letter) for letter in dec_to_let(pair_value, n)])
        i += n
    extra_letters = let_to_dec("".join([l for l in rs[1:4] if ord(l) > 0]))
    # print(extra_letters)
    # print(rs)
    # print([ord(l) for l in rs])
    return rs[4:len(rs) - extra_letters]


class UnicodeEncryption(Widget):
    pass


class EncryptionApp(App):
    def build(self):
        return UnicodeEncryption()

    def encrypt_text(self):
        # text = self.root.ids.input.text
        with open("out.txt", "w", encoding="utf-32") as file:
            for i in range(2):
                for j in range(1114111**i):
                    try:
                        text = dec_to_let(j, i)
                        # file.write(text)
                        # file.write("\n")
                        enc = encrypt(text, block_size_var, encrypt_val_1, encrypt_val_2)
                        # file.write(enc)
                        # file.write("\n")
                        dec = decrypt(enc, block_size_var, encrypt_val_1, encrypt_val_2)
                        # file.write(dec)
                        # file.write("\n")
                        if text == dec:
                            continue
                        else:
                            file.write(f"{str(text == dec)}, {j}")
                        # file.write("\n\n")
                    except:
                        continue
        print("done")
        # text = let_to_dec_blocks(text, block_size_var)
        # print(text)


if __name__ == '__main__':
    EncryptionApp().run()
