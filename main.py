hex_str = "0123456789ABCDEF"
alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


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


def unicode(inpt):
    return chr(hex_to_dec(inpt))


def let_to_dec(inpt):
    rn = 0
    i = 0
    for letter in inpt:
        rn += ord(letter) * (hex_to_dec("10FFFD")**i)
        i += 1
    return rn


def dec_to_let(inpt):
    rs = ""
    nm = inpt
    while (nm / hex_to_dec("10FFFD")) > 0:
        rs += chr(nm % hex_to_dec("10FFFD"))
        nm //= hex_to_dec("10FFFD")
    return rs


def convert_to_text(num, n):
    rs = ""
    nm = num
    for i in range(n):
        rs += alpha[nm % len(alpha)]
        nm //= len(alpha)
    return rs[::-1]


def convert_to_text_uni(num, n):
    rs = ""
    nm = num
    for i in range(n):
        rs += chr(nm % hex_to_dec("10FFFD"))
        nm //= hex_to_dec("10FFFD")
    return rs[::-1]
