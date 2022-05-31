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

print(hex_to_dec("FB"))