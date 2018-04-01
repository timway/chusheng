from passlib.hash import md5_crypt
from tkinter import *

#### Source Material
# Cisco 1841 with IOS15
#   Username of test
#   Password of a1b2
# username test secret 5 $1$jBjw$l492gWppPZ5ldgkTMr3YB.
#
# Linux with OpenSSL Method
#   [user@wk1 chusheng]$ openssl passwd -1 -salt 'jBjw' -1 'a1b2'
#   $1$jBjw$l492gWppPZ5ldgkTMr3YB.

def byfire(salt, target, guess):
    a = md5_crypt.using( salt = salt, salt_size = 4).hash(''.join(guess))
    if target == a.strip().split('$')[3]:
        return True
    else:
        return False

def actually(characters, salt, target, s, i, p):
    if len(s) < i:
        s.append(characters[0])
        actually(characters, salt, target, s, i, p)
    elif len(s) == i and not byfire(salt, target, s):
        for z in reversed(range(p,len(s))):
            if s[z] != characters[len(characters) - 1]:
                s[z] = characters[characters.index(s[z]) + 1]
                actually(characters, salt, target, s, i, z)
            else:
                s[z] = characters[0]
    else:
        lbl_answer.configure(text = ''.join(s))
        lbl_answer.update()
        return True

    return False

def bruteforce(salt,target):
    '''
    
    '''
    
    characters = []
    for c in range(ord('0'),ord('9') + 1):
        characters.append(chr(c))
    for c in range(ord('A'),ord('Z') + 1):
        characters.append(chr(c))
    for c in range(ord('a'),ord('z') + 1):
        characters.append(chr(c))

    characters = list(['a','1','b','2'])

    lbl_answer['text'] = ''
    upper = 4
    print('the label cget is %s fdsa' % lbl_answer.cget("text"))
    for x in range(0,upper + 1):
        lbl_status['text'] = 'Processing length of %s' % x
        if lbl_answer.cget("text") != '':
            print('test string 1')
        print('the label cget is %s fdsa' % lbl_answer.cget("text"))
        print(lbl_answer['text'])
        actually(characters, salt, target, list(), x, 0)
    
def dictionary():
    '''
    '''

def crack():
    print(ent_hash.get().strip().split("$"))
    a = ent_hash.get().strip().split("$")
    
    if len(a) == 4:
        salt = a[2]
        target = a[3]
        bruteforce(salt,target)
    else:
        print('Incorrectly inputted hash.')

root = Tk()
root.title('chusheng')

hash = ''

chk_lower_v = IntVar(value = 1)
chk_lower = Checkbutton(root,
    text="Lowercase, [a .. b]",
    var = chk_lower_v)
chk_lower.grid(row = 0, column = 0)

chk_upper_v = IntVar(value = 1)
chk_upper = Checkbutton(root,
    text="Uppercase, [A .. B]",
    var = chk_upper_v)
chk_upper.grid(row = 0, column = 1)

chk_numeral_v = IntVar(value = 1)
chk_numeral = Checkbutton(root,
    text="Numerals, [0 .. 9]",
    var = chk_numeral_v)
chk_numeral.grid(row = 1, column = 0)

chk_special_v = IntVar(value = 0)
chk_special = Checkbutton(root,
    text="Specials",
    var = chk_special_v)
chk_special.grid(row = 1, column = 1)

lbl_status = Label(root, text='')
lbl_status.grid(row = 2, column = 0, columnspan = 2)

lbl_answer = Label(root, text='')
lbl_answer.grid(row = 3, column = 0, columnspan = 2)

lbl_hash = Label(root, text='Enter the hash')
lbl_hash.grid(row = 3, column = 0, columnspan = 2)

ent_hash = Entry(root, justify = 'center', width = 36)
ent_hash.grid(row = 5, column = 0, columnspan = 2)

btn_crack = Button(root, text="Crack", command=crack)
btn_crack.grid(row = 6, column = 0, columnspan = 2)

root.mainloop()
