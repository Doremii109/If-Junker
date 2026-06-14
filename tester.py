# link to the file: https://t.me/PaketPKSoftware
# link to the file: https://t.me/PaketPKSoftware
# link to the file: https://t.me/PaketPKSoftware
# link to the file: https://t.me/PaketPKSoftware

import ast

a = "asd"


class ObfuscatorError(RuntimeError): ...


try:
    raise ObfuscatorError("asd")
except ObfuscatorError as e:
    if e.args != ("asd",):
        print("ObfuscatorError raise error")
    else:
        print("raise test passed")


def nigger(d: str):
    global a
    a = a + d


def loader():
    global asd
    asd = "asd32"


class Pidr:
    nigger("3")
    xxx = 123


def closu():
    loader()
    g = "a"

    def pidr(d: str):
        nonlocal g
        g = g + d
        match d:
            case "sd":
                g += str(3)

    nigger("2")
    pidr("sd")
    pidr("2")
    if not (a == g == asd):
        print("nonlocal/global + const error")
    else:
        print("nonlocal/global + const test passed!")


def cefefe():
    a = 0
    for asd in range(100):
        if asd % 2 == 0:
            continue
        elif (asd + 1) % 16 == 0:
            break

        a += asd
    if a != 49:
        print("break/continue error")
    else:
        print("break/continue passed")

    a1 = 0
    for asd in range(100):
        try:
            if asd % 2 == 0:
                try:
                    continue
                except:
                    pass
            elif (asd + 1) % 16 == 0:
                try:
                    break
                except BaseException:
                    pass
        except:
            pass
        a1 += asd
    if a1 != 49:
        print("break/continue (try except) error")
    else:
        print("break/continue (try except) passed")


def kwtest():

    def a_cell(id):
        return [id]

    c_a = a_cell(id="asd")
    c_n = ast.Name(id="asd")
    if c_a[0] != c_n.id:
        print("kw args test 1 error!")
    else:
        print("kw args test 1 passed!")

    # ращница в том что id - имя из builtin, а arg нет

    def b_cell(arg):
        return [arg]

    c_a = b_cell(arg="asd")
    c_n = ast.arg(arg="asd")
    if c_a[0] != c_n.arg:
        print("kw args test 2 error!")
    else:
        print("kw args test 2 passed!")


def attrer():
    class Attrst:
        arg = "123"
        other = 123
        value = "asd"

        def nig(sel_f):
            return "as" + sel_f.forv()

        def forv(s_elf):
            return "sa"

        @staticmethod
        def X():
            return "sa" + Attrst().nig()

    def giga(x):
        return x.value

    if giga(ast.Constant("asd")) == giga(Attrst):
        print("attr test 1 passed!")
    else:
        print("attr test 1 error!")

    if Pidr.xxx == 123 == Attrst.other:
        print("attr test 2 passed!")
    else:
        print("attr test 2 error!")

    if Attrst.X() == "saassa":
        print("attr test 3 passed!")
    else:
        print("attr test 3 error!")


def sideff():
    from types import SimpleNamespace

    cnt = 0

    def flag(x):
        nonlocal cnt
        cnt += x
        return cnt

    def test(x=SimpleNamespace(c=1)):
        flag(x.c)
        return x

    test().c += 1
    test().c += 1

    res1 = test()
    if cnt != 6:
        print("side effect test 1 error!")
    else:
        print("side effect test 1 passed!")

    if str(res1) != "namespace(c=3)":
        print("side effect test 2 error!")
    else:
        print("side effect test 2 passed!")

    if [test(), cnt][1] != 9:
        print("side effect test 3 error!")
    else:
        print("side effect test 3 passed!")


if __name__ == "__main__":
    closu()
    cefefe()
    kwtest()
    attrer()
    sideff()
