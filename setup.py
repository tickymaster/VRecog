# setup.py
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext

# ... (version management and extension definition)

# extension used as an external module for python
class CMakeExtension(Extension):
 def __init__(self, name, sourcedir=""):
  Extension.__init__(self, name, sources=[])
  self.sourcedir = os.path.abspath(sourcedir)

# call subprocess to run cmake on the library
class CMakeBuild(build_ext):
 def run(self):
  repo_path = Path(__file__).parent
  subprocess.call(["git", "--work-tree", str(repo_path),
       "submodule", "update", "--init"])
  for ext in self.extensions:
   self.build_extension(ext)

 def build_extension(self, ext):
  extdir = os.path.abspath(
   os.path.dirname(self.get_ext_fullpath(ext.name))
  )

  if not extdir.endswith(os.path.sep):
   extdir += os.path.sep

  # debug or release build flag for cmake. If you want to create
  # a debug build, you should export DEBUG_BUILD=1 before running
  # your setup script
  build_flag = os.environ.get("DEBUG_BUILD", "0")
  cfg = "Debug" if build_flag == "1" else "Release"
  cmake_args = [
   f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
   f"-DPYTHON_EXECUTABLE={sys.executable}",
   f"-DCMAKE_BUILD_TYPE={cfg}",
  ]
  os.makedirs(self.build_temp, exist_ok=True)
  subprocess.check_call(
   ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp
  )
  subprocess.check_call(
   ["cmake", "--build", ".", "--config",cfg,
    "--", f"-j{os.cpu_count()-1}"],
    cwd=self.build_temp,
  )

setup(
 name="formant_detector",
 version="1.0.0",
 author="",
 author_email="",
 description="Real-time formant frequency detection using C++ and Python bindings",
 long_description="A Python module for real-time formant frequency detection from audio input using FFT analysis and peak detection algorithms.",
 packages=find_packages(exclude=[]),
 package_data={"formant_detector": ["./../VERSION"]},
 install_requires=[
     "numpy",
     "scikit-learn",
     "pandas",
     "matplotlib",
 ],
 python_requires=">=3.7",
 ext_modules=[CMakeExtension("formant_detector")],
 cmdclass={"build_ext": CMakeBuild},
 zip_safe=False,
)