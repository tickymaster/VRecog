# CMakeLists.txt
cmake_minimum_required(VERSION 3.12)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS ON)
project(formant_detector)

# Find required packages
find_package(PkgConfig REQUIRED)
pkg_check_modules(FFTW REQUIRED fftw3)
pkg_check_modules(PORTAUDIO REQUIRED portaudio-2.0)

# Manage external libraries with submodules
add_subdirectory(third-party/pybind11)

# Compile source files for the python binding
pybind11_add_module(formant_detector
  src/fomant_module_interface.cpp
  src/formant_module_impl.cpp
)

# Include header directory for compilation
target_include_directories(formant_detector
  PUBLIC
  include
  ${FFTW_INCLUDE_DIRS}
  ${PORTAUDIO_INCLUDE_DIRS}
)

# Link required libraries
target_link_libraries(formant_detector
  PRIVATE
  ${FFTW_LIBRARIES}
  ${PORTAUDIO_LIBRARIES}
)