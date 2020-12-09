"""
inline C in python
"""

import ctypes
import os
import distutils.ccompiler
import shutil


class C:
    cc = distutils.ccompiler.new_compiler()
    cache_dir = "__cscriptcache__"
    libs = {}

    @staticmethod
    def exist_dl(name):
        if name in C.libs:
            return C.libs[name].__dl
        return None

    @staticmethod
    def clean():
        """
        Close all dynamic libraries and remove cscript cache
        """
        C.libs.clear()
        shutil.rmtree(C.cache_dir, ignore_errors=True)

    def __init__(self, name: str, code: str):
        self.__code = code
        self.__name = name
        self.__src_path = ""
        self.__lib_path = ""
        self.__dl = C.exist_dl(self.__name)
        self.lib = None

    def __del__(self):
        self.__dlclose()
        self.__dldelete()
        if not C.libs:
            shutil.rmtree(C.cache_dir, ignore_errors=True)

    def update(self, code: str):
        """
        Update C code
        """
        self.__code = code

    def append(self, code: str):
        """
        Append C code
        """
        self.__code += code

    def compile(self, cc=None, flags=["-fPIC", "-O2"]):
        """
        Compile C code

        Parameters
        ----------
        cc: c compiler
        flags: compiler flags

        Example
        -------
        >>>src = C('int a() { return 1; }'); obj = src.compile()

        Return
        ------
        object
        """
        if not cc:
            cc = C.cc

        if self.__dl:
            self.__dlclose()
            self.__dldelete()

        dir_path = C.cache_dir
        src_path = os.path.join(dir_path, self.__name + ".c")
        self.__src_path = src_path
        lib_name = cc.library_filename(self.__name, "shared")
        lib_path = os.path.join(dir_path, lib_name)
        self.__lib_path = lib_path

        os.makedirs(dir_path, exist_ok=True)

        with open(src_path, "w") as f:
            f.write(self.__code)

        objs = cc.compile([src_path], extra_postargs=flags)
        cc.link_shared_lib(objs, self.__name, output_dir=dir_path)
        self.__dlopen(lib_path)
        self.lib = self.__dl

        return self.lib

    def __dldelete(self):
        try:
            os.remove(self.__src_path)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.__lib_path)
        except FileNotFoundError:
            pass

    def __dlopen(self, lib: str):
        self.__dlclose()
        self.__dl = ctypes.CDLL(lib)
        return self.__dl

    # See https://stackoverflow.com/questions/50964033/forcing-ctypes-cdll-loadlibrary-to-reload-library-from-file
    def __dlclose(self):
        if self.__dl:
            dlclose_func = ctypes.CDLL(None).dlclose
            dlclose_func.argtypes = [ctypes.c_void_p]
            dlclose_func.restype = ctypes.c_int
            dlclose_func(self.__dl._handle)
            self.__dl = None
            self.lib = None
