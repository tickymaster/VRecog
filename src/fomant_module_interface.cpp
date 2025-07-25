// formant_module_interface.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "formant_module.h"

namespace py = pybind11;

PYBIND11_MODULE(formant_detector, m) {
    m.doc() = "Formant detection module";

    // Expose only the main streamClass API
    py::class_<streamClass>(m, "FormantDetector")
        .def(py::init<>(), "Initialize the formant detector")
        .def("start_stream", &streamClass::start_stream, 
             "Start audio stream for formant detection",
             py::arg("deviceInput") = 4)
        .def("stop_stream", &streamClass::stop_stream, 
             "Stop the audio stream")
        .def("print_devices", &streamClass::print_devices, 
             "Print available audio devices")
        .def("get_formants", &streamClass::get_formants, 
             "Get the latest detected formant frequencies as a list [F1, F2]");
}
