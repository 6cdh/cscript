from cscript import C
from ctypes import c_float, c_double


def test_compile():
    src = C(
        "test_compile",
        r"""
    int add(int a, int b) {
        return a + b;
    }
    """,
    )
    lib = src.compile()
    assert lib.add(1, 2) == 3


def test_update():
    src = C(
        "test_update",
        r"""
    int add(int a, int b) {
        return a + b;
    }
    """,
    )

    obj = src.compile()

    src.update(
        r"""
    int one() {
        return 1;
    }
    """
    )

    obj = src.compile()
    assert obj.one() == 1


def test_append():
    src = C(
        "test_append",
        r"""
    int add(int a, int b) {
        return a + b;
    }
    """,
    )

    obj = src.compile()

    src.append(
        r"""
    int one() {
        return 1;
    }
    """
    )

    obj = src.compile()
    assert obj.add(1, 2) == 3
    assert obj.one() == 1


def test_float():
    src = C(
        "test_float",
        r"""
    float add(float a, float b) {
        return a + b;
    }
    """,
    )
    obj = src.compile()
    obj.add.argtypes = [c_float, c_float]
    obj.add.restype = c_float
    assert obj.add(1.0, 2.0) == 3.0


def test_double():
    src = C(
        "test_double",
        r"""
    double add(double a, double b) {
        return a + b;
    }
    """,
    )
    obj = src.compile()
    obj.add.argtypes = [c_double, c_double]
    obj.add.restype = c_double
    assert obj.add(1.0, 2.0) == 3.0


def test_print():
    src = C(
        "test_print",
        r"""
    #include <stdio.h>
    int print() {
        return printf("print in csript\n");
    }
    """,
    )
    obj = src.compile()

    assert obj.print() == len("print in csript\n")


def test_clean():
    C.clean()


def test_fib():
    def fib(n):
        if n in (0, 1):
            return 1
        return fib(n - 1) + fib(n - 2)

    src = C(
        "test_fib",
        r"""
    int fib(int n) {
        if (n == 0) { return 1; }
        if (n == 1) { return 1; }
        return fib(n - 1) + fib(n - 2);
    }
    """,
    )
    obj = src.compile()
    assert obj.fib(10) == fib(10)
