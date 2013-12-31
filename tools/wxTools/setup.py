from distutils.core import setup
import py2exe
from glob import glob

data_files = ['appicon.ico',
              'Tools.ini',
              ('bin',glob(r'bin\*.*')),
              ('temp',()),
              ("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
option = {
    "compressed"    :    1    ,
    "optimize"      :    1    ,
    "bundle_files"  :    1
}

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "1.5.0",
    description = "Vim Source Navigator",
    name = "ToolsEnvironment",

    options = {
        "py2exe"    :    option
    },
    # zipfile=None,
    # targets to build
    windows = ["ToolsEnvironment.py"],
    data_files = data_files,
    )
