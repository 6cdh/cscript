from cscript import C

src = C(
    r"""
int add(int a, int b) {
    return a + b;
}
"""
)

obj = src.compile()

assert obj.add(1, 2) == 3

src.update(
    r"""
int flo() {
    return 1;
}
"""
)

obj = src.compile()

assert obj.flo() == 1

src.update(
    r"""
#include <stdio.h>
void print() {
    printf("print in csript\n");
}
"""
)

obj = src.compile()
obj.print()

C.clean()
