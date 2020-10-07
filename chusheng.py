import ctypes
import itertools
import multiprocessing
import os

from itertools import product
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
#
# Invalid HASH for testing
#   $1$jBjw$l492gWppPZ5ldgkTMr3YC.


def int_to_base_x(characters, num):
    base = len(characters)
    position = []

    while num != 0:
        position = position + [characters[num % base]]
        num = num // base

    if len(position) > 0:
        return position[::-1]
    else:
        return [characters[0]]


def int_to_base_x_by_idx(characters, num):
    # convert an integer to a list containing the integer value of the character it references in
    # the character set.
    base = len(characters)
    position = []

    while num != 0:
        position = position + [
            characters.index(
                characters[num % base]
                )
            ]
        num = num // base

    if len(position) > 0:
        return position[::-1]
    else:
        return [characters[0]]


def build_chunks(characters, maximum):
    cpus = len(os.sched_getaffinity(0))
    chunk_size = len(characters) ** maximum // cpus
    while chunk_size == 0 and cpus > 0:
        print(chunk_size, cpus)
        cpus = cpus - 1
        chunk_size = len(characters) ** maximum // cpus
    chunks = []
    for chunk in range(0, cpus):
        if chunk + 1 < cpus:
            end = (chunk + 1) * chunk_size
        else:
            end = len(characters) ** maximum
        chunks.append((
            chunk * chunk_size,
            end
            ))

    return chunks


def bruteforce_m(characters, salt, target, maximum, sentinel, result, boundaries):
    cartesian = itertools.product(characters, repeat=maximum)
    print(len(characters), salt, target, maximum, sentinel.value, boundaries)

    if boundaries[0] > 0:
        start = int_to_base_x_by_idx(characters, boundaries[0])
        if len(start) < maximum:
            start_tuple = tuple([0] * (maximum - len(start)) + start)
        else:
            start_tuple = tuple(start)
        cartesian.__setstate__(start_tuple)

    for cidx in range(boundaries[0], boundaries[1] - 1):
        if sentinel.value:
            print(f"In a sub-process and noticed that it is set to 1 {os.getpid()}")
            return
            
        guess = next(cartesian)
        h = md5_crypt.using(
            salt=salt,
            salt_size=4
            ).hash(
            "".join(
                guess
                )
            ).strip().split("$")[3]
        
        if h == target:
            print(f"Found a match in {os.getpid()}")
            sentinel.value = True
            result.put("".join(guess))
            #"".join(guess).encode("utf-8")
            return cidx, guess


def bruteforce_o(characters, salt, target, maximum):
    for idx, guess in enumerate(itertools.product(characters, repeat=maximum)):
        h = md5_crypt.using(
            salt = salt,
            salt_size = 4
            ).hash(
            "".join(guess)
            ).strip().split("$")[3]

        if h == target:
            return guess


def wrapper_m(characters, salt, target, maximum):
    sentinel = multiprocessing.Value(ctypes.c_bool, False)
    result = multiprocessing.Queue()
    for m in range(1, maximum + 1):
        chunks = build_chunks(characters, m)
        processes = [
            multiprocessing.Process(
                target=bruteforce_m,
                args=(
                    characters,
                    salt,
                    target,
                    m,
                    sentinel,
                    result,
                    chunk
                    )
                ) for chunk in chunks
            ]
        for process in processes:
            process.start()

        for process in processes:
            if process.is_alive():
                process.join()
    
    if sentinel.value:
        return result.get()


def wrapper_o(characters, salt, target, maximum):
    for m in range(1, maximum + 1):
        answer = bruteforce_o(characters, salt, target, m)
    
    if answer is not None:
        return answer


def crack():
    characters = []
    if chk_numeral_v.get() == 1:
        for c in range(ord('0'),ord('9') + 1):
            characters.append(chr(c))
    if chk_special_v.get() == 1:
        for c in [ '!','@','#','$','%','^','&','*','(',')','-','_','=','+' ]:
            characters.append(c)
    if chk_lower_v.get() == 1:
        for c in range(ord('a'),ord('z') + 1):
            characters.append(chr(c))
    if chk_upper_v.get() == 1:
        for c in range(ord('A'),ord('Z') + 1):
            characters.append(chr(c))
    
    answer = wrapper_m(
        characters,
        ent_hash.get().strip().split("$")[2],
        ent_hash.get().strip().split("$")[3],
        scl_depth_v.get()
        )
    print(answer, type(answer))
    
    if answer is not None:
        ent_answer.insert(0, "".join(answer))
    else:
        ent_answer.insert(0, "Not Found!")


if __name__ == "__main__":
    root = Tk()
    root.title('chusheng')

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

    lbl_depth = Label(root, text = 'Maximum Password Length')
    lbl_depth.grid(row = 2, column = 0, columnspan = 2)

    scl_depth_v = IntVar(value = 12)
    scl_depth = Scale(root, from_ = 1, to = 32,
        length = 256,
        orient = HORIZONTAL,
        showvalue = 1,
        var = scl_depth_v)
    scl_depth.grid(row = 3, column = 0, columnspan = 2)

    lbl_hash = Label(root, text='Enter the hash')
    lbl_hash.grid(row = 4, column = 0, columnspan = 2)

    ent_hash = Entry(root, justify = 'center', width = 36)
    ent_hash.grid(row = 5, column = 0, columnspan = 2)

    ent_hash.delete(0, END)
    ent_hash.insert(0, '$1$jBjw$l492gWppPZ5ldgkTMr3YB.')

    btn_crack = Button(root, text="Crack", command=crack)
    btn_crack.grid(row = 7, column = 0, columnspan = 2, pady = (8,8))

    lbl_status = Label(root, text='')
    lbl_status.grid(row = 9, column = 0, columnspan = 2, pady = (8,8))

    ent_answer = Entry(root, justify = 'center', width = 36)
    ent_answer.grid(row = 10, column = 0, columnspan = 2, pady = (8,8))

    root.mainloop()

