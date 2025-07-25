// ---------------------------------------------------------------------------------
//
// formant_module.h
//
// ---------------------------------------------------------------------------------

#ifndef FORMANT_MODULE_H
#define FORMANT_MODULE_H

// ---------------------------------------------------------------------------------
//
// Headers
//
// ---------------------------------------------------------------------------------

#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <cstring>
#include <cmath>
#include <vector>
#include <numeric>
#include <algorithm>

#include <python3.12/Python.h>
#include <fftw3.h>
#include <portaudio.h>
// #include <pybind11/pybind11.h>

// ---------------------------------------------------------------------------------
// 
// Constants
//
// ---------------------------------------------------------------------------------

#define SAMPLE_RATE 44100.0
#define FRAMES_PER_BUFFER 4096
#define NUM_CHANNELS 1

#define SPECTRO_FREQ_START 20
#define SPECTRO_FREQ_END 20000

#define RADIUS_OF_THE_KERNEL 3
#define STANDARD_DEVIATION 0.5

#define FORMANT_ACCURACY 150

// ---------------------------------------------------------------------------------
// 
// Structures and Types
//
// ---------------------------------------------------------------------------------

struct FrequencyMagnitude {
    double frequency;
    double magnitude;
    bool isMaxima;
};

typedef struct {
    double* in;
    double* out;
    fftw_plan p;
    int startIndex;
    int spectralSize;
} streamCallbackData;

struct Formants {
    double f1;
    double f2;
};

// ---------------------------------------------------------------------------------
// 
// Classes
//
// ---------------------------------------------------------------------------------

class Formant {
private:
    Formants formants;
public:
    void set_formants(double f1, double f2);
    std::vector<double> get_formants();
};

struct CallbackState {
    streamCallbackData* spectroData;
    Formant* formant;
};

class streamClass {
private:
    PaError err;
    PaStream* stream;
    Formant formant;
    CallbackState* cbState;
public:
    streamClass();
    void start_stream(int deviceInput = 4);
    void stop_stream();
    void print_devices();
    std::vector<double> get_formants();
};

// ---------------------------------------------------------------------------------
// 
// Function Declarations
//
// ---------------------------------------------------------------------------------

// Helper functions
void checkError(PaError err);
inline float max(float a, float b);
inline float min(float a, float b);
inline bool isPositive(double a);
inline int clamp(int value, int min, int max);
double G(int x);
std::vector<double> computeKernelFilter();

// Callback function
int streamCallback(
    const void* inputBuffer,
    void* outputBuffer,
    unsigned long framesPerBuffer,
    const PaStreamCallbackTimeInfo* timeInfo,
    PaStreamCallbackFlags statusFlags,
    void* userData
);

#endif // FORMANT_MODULE_H
