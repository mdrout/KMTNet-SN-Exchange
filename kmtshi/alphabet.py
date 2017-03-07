'''This will take a number and output the alphabet code for it
i.e 1= A, 2=B, 27 =aa, 28 = ab etc.'''

from string import ascii_letters

def num2alpha(num):
    lower = ascii_letters[0:26]
    upper = ascii_letters[26:]
    if num <= 26:
        letters = upper[num-1]
    else:
        base1 = int(num/26)
        base2 = num % 26
        if base2 == 0:
            letters = lower[base1-2]+lower[base2-1]
        else:
            letters = lower[base1-1]+lower[base2-1]
    return letters
