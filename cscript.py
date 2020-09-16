"""
inline C in python
"""

import ctypes
import os
import distutils.ccompiler
import shutil


class C:

    cc = distutils.ccompiler.new_compiler()
    dir = "__cscriptcache__"
    __instances = {}

    def __init__(self, code: str, name: str = "cscript"):
        self.code = code
        self.name = name
        self.__dl = None
        if name in C.__instances:
            self.__dl = C.__instances[name].__dl
        else:
            C.__instances[name] = self

    def update(self, code):
        """
        Update C code
        """
        self.code = code

    def compile(self, cc=None, flags=["-fPIC", "-O2"]):
        """
        Compile C code

        Parameters
        ----------
        cc: c compiler
        flags: compiler flags

        Example
        -------
        >>>C('int a();').compile()

        Return
        ------
        object
        """
        if cc is None:
            cc = C.cc
        C.__check_path()
        dir = C.dir
        src = os.path.join(dir, self.name + ".c")
        sharedlib_name = cc.library_filename(self.name, "shared")
        lib = os.path.join(dir, sharedlib_name)

        with open(src, "w") as f:
            f.write(self.code)

        objs = cc.compile([src], extra_postargs=flags)
        try:
            os.remove(lib)
        except FileNotFoundError:
            pass
        cc.link_shared_lib(objs, self.name, output_dir=dir)
        return self.__dlopen(lib)

    def __dlopen(self, lib: str):
        self.__dlclose()
        self.__dl = ctypes.CDLL(lib)
        return self.__dl

    # See https://stackoverflow.com/questions/50964033/forcing-ctypes-cdll-loadlibrary-to-reload-library-from-file
    def __dlclose(self):
        if self.__dl is not None:
            dlclose_func = ctypes.CDLL(None).dlclose
            dlclose_func.argtypes = [ctypes.c_void_p]
            dlclose_func.restype = ctypes.c_int
            dlclose_func(self.__dl._handle)
        self.__dl = None

    @staticmethod
    def __check_path():
        os.makedirs(C.dir, exist_ok=True)

    @classmethod
    def clean(cls):
        """
        Close all dynamic libraries and remove cscript cache
        """
        for _, instance in cls.__instances.items():
            instance.__dlclose()
        cls.__instances = {}
        shutil.rmtree(C.dir)
