from distutils.core import setup
import py2exe
from glob import glob

option = {
    "compressed"    :    1    ,
    "optimize"      :    1    ,
    "bundle_files"  :    1    ,
    "includes"      :    "sip"
}

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.1.0",
    description = "Function Test Tool",
    name = "FuncFinder",

    options = {
        "py2exe"    :    option
    },
    # zipfile=None,
    # targets to build
    windows = ["ui/funcfinder.py"],
    )
