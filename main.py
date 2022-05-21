from kivy.app import App
from kivy.uix.widget import Widget


hex_str = "0123456789ABCDEF"


def hex_to_dec(inpt):
    rn = 0
    i = 0
    inpt = inpt[::-1]
    while i < len(inpt):
        val = inpt.upper()[i]
        rn += hex_str.index(val) * (len(hex_str)**i)
        i += 1
    return rn


def dec_to_hex(inpt):
    rs = ""
    inp = inpt
    while inp > 0:
        rs += hex_str[inp % len(hex_str)]
        inp //= len(hex_str)
    return rs[::-1]


def let_to_dec(inpt):
    rn = 0
    i = 0
    for letter in inpt:
        rn += ord(letter) * (hex_to_dec("10FFFD")**i)
        i += 1
    return rn


def dec_to_let(num):
    rs = ""
    nm = num
    while (nm / hex_to_dec("10FFFD")) > 0:
        rs += chr(nm % hex_to_dec("10FFFD"))
        nm //= hex_to_dec("10FFFD")
    return rs


def dec_to_let_blocks(num, n):
    rs = ""
    nm = num
    for i in range(n):
        rs += chr(nm % hex_to_dec("10FFFD"))
        nm //= hex_to_dec("10FFFD")
    return rs[::-1]


class UnicodeEncryption(Widget):
    pass


class EncryptionApp(App):
    def build(self):
        return UnicodeEncryption()


if __name__ == '__main__':
    EncryptionApp().run()
