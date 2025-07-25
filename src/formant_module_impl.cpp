// ---------------------------------------------------------------------------------
//
// Header
//
// ---------------------------------------------------------------------------------

#include "formant_module.h"

// ---------------------------------------------------------------------------------
// 
// Global Variables
//
// ---------------------------------------------------------------------------------

static streamCallbackData* spectroData;

// ---------------------------------------------------------------------------------
// 
// Helper functions - Implementation
//
// ---------------------------------------------------------------------------------

// Formant class implementation
void Formant::set_formants(double f1, double f2) {
    formants.f1 = f1;
    formants.f2 = f2;
}

std::vector<double> Formant::get_formants() {
    return {formants.f1, formants.f2};
}

void checkError(PaError err) {
		if (err != paNoError)
		{
				printf("Port audio error: %s\n", Pa_GetErrorText(err));
				exit(EXIT_FAILURE);
		}
}

inline float max(float a, float b) {
		return a > b ? a : b;
}

inline float min(float a, float b) {
		return a < b ? a : b;
}

inline bool isPositive(double a) {
		return a >= 0 ? true : false;
}

inline int clamp(int value, int min, int max) {
		return std::max(min, std::min(value, max));
}

double G(int x) {
		return std::exp((-(x * x)) / (2 * (STANDARD_DEVIATION * STANDARD_DEVIATION)));
}

std::vector<double> computeKernelFilter() {
		int kernel_size = 2 * RADIUS_OF_THE_KERNEL + 1;
		std::vector<double> kernel(kernel_size);
		double sum = 0.0;

		for (int i = -RADIUS_OF_THE_KERNEL; i <= RADIUS_OF_THE_KERNEL; i++)
		{
				double value = G(i);
				kernel[i + RADIUS_OF_THE_KERNEL] = value;
				sum += value;
		};

		for (auto& val : kernel)
		{
				val /= sum;
		}

		return kernel;
}


// ---------------------------------------------------------------------------------
// 
// Callback function
//
// ---------------------------------------------------------------------------------


int streamCallback(
		const void* inputBuffer,
		void* outputBuffer,
		unsigned long framesPerBuffer,
		const PaStreamCallbackTimeInfo* timeInfo,
		PaStreamCallbackFlags statusFlags,
		void* userData
) {
		float* in = (float*)inputBuffer;
		(void)outputBuffer;
		CallbackState* cb = (CallbackState*)userData;
		streamCallbackData* callbackData = cb->spectroData;
		Formant* formant = cb->formant;

		for (size_t i = 0; i < framesPerBuffer; i++)
		{
				callbackData->in[i] = in[i * NUM_CHANNELS];
		}

		fftw_execute(callbackData->p);

		// SpectroData->out is now filled with the FFT results
		// Initialise an array absolouteResult
		
		int halfSize = callbackData->startIndex + callbackData->spectralSize;

		std::vector<double> absolouteResult;
		absolouteResult.resize(halfSize);

		std::vector<double> kernel = computeKernelFilter();

		std::vector<double> smoothed;
		smoothed.resize(halfSize,0);

		std::vector<double> firstDif; // basically the first derivative
		firstDif.resize(halfSize-1);

		std::vector<double> secondDif; // basically the second derivative
		secondDif.resize(halfSize - 2);

		std::vector<FrequencyMagnitude> aproxPeakValeyFreq;

		for (size_t i = 0; i < halfSize; i++)
		{
				absolouteResult[i] = abs(spectroData->out[i]);
		}

		for (size_t i = 0; i < smoothed.size(); i++)
		{
				for (int j = -RADIUS_OF_THE_KERNEL; j <= RADIUS_OF_THE_KERNEL; j++)
				{
						smoothed[i] += kernel[j + RADIUS_OF_THE_KERNEL] * absolouteResult[clamp(i + j, 0, halfSize-1)];
				}
		}

		for (size_t i = 0; i < halfSize-1; i++)
		{
				firstDif[i] = smoothed[i + 1] - smoothed[i];
		}

		for (size_t i = 0; i < halfSize - 2; i++)
		{
				secondDif[i] = firstDif[i + 1] - firstDif[i];
		}


		bool currentPositive;
		bool nextPositive;

		for (size_t i = 0; i < halfSize - 2; i++)
		{
				currentPositive = isPositive(firstDif[i]);
				nextPositive = isPositive(firstDif[i + 1]);

				if (currentPositive != nextPositive)
				{
						FrequencyMagnitude freqmag;
						freqmag.frequency = std::round((SAMPLE_RATE / FRAMES_PER_BUFFER) * (i + callbackData->startIndex + 0.5));
						freqmag.magnitude = smoothed[i];
						secondDif[i] < 0 ? freqmag.isMaxima = true : freqmag.isMaxima = false;
						aproxPeakValeyFreq.push_back(freqmag);
				}
		}

		std::vector<FrequencyMagnitude> speechPeaks;

		for (auto& f : aproxPeakValeyFreq)
		{
				if (f.isMaxima && f.frequency >= 300 && f.frequency <= 3200)
				{
						speechPeaks.push_back(f);
				}
		}

		double maxMag = 0.0;
		for (auto& f : speechPeaks)
		{
				maxMag = max(maxMag, f.magnitude);
		}

		std::vector<FrequencyMagnitude> strongPeaks;

		for (auto& f : speechPeaks)
		{
				if (f.magnitude > 0.7 * maxMag)
				{
						strongPeaks.push_back(f);
				}
		}

		std::sort(strongPeaks.begin(), strongPeaks.end(), [](const FrequencyMagnitude& a, const FrequencyMagnitude& b) {
				return a.frequency > b.frequency;
		});

		// for (auto& peak : strongPeaks)
		//{
		//		std::cout << "Strong peak at: Freq: " << peak.frequency << " Magnitude: " << peak.magnitude << '\n';
		//}

		if (strongPeaks.size() >= 2) {
				double f1 = std::min(strongPeaks[0].frequency, strongPeaks[1].frequency);
				double f2 = std::max(strongPeaks[0].frequency, strongPeaks[1].frequency);
				std::cout << "Detected: F1=" << f1 << " Hz, F2=" << f2 << " Hz" << '\n';
				formant->set_formants(f1,f2);
		}

		// can call formant.get_formants() to get the formants - can be used to pass into the python file

		std::cout << "EOB \n";

		fflush(stdout);

		return 0;
}

// ---------------------------------------------------------------------------------
// 
// API - streamClass Implementation
//
// ---------------------------------------------------------------------------------

streamClass::streamClass() {
    this->err = Pa_Initialize();
    checkError(err);

	spectroData = (streamCallbackData*)malloc(sizeof(streamCallbackData));
	spectroData->in = (double*)malloc(sizeof(double) * FRAMES_PER_BUFFER);
	spectroData->out = (double*)malloc(sizeof(double) * FRAMES_PER_BUFFER);
	if (spectroData->in == NULL || spectroData->out == NULL)
	{
		printf("Could not allocate specto data\n");
		exit(EXIT_FAILURE);
	}
	spectroData->p = fftw_plan_r2r_1d(
		FRAMES_PER_BUFFER,
		spectroData->in,
		spectroData->out,
		FFTW_R2HC,
		FFTW_ESTIMATE
	);
	double sampleRatio = FRAMES_PER_BUFFER / SAMPLE_RATE;
	spectroData->startIndex = std::ceil(sampleRatio * SPECTRO_FREQ_START);
	spectroData->spectralSize = min(
		std::ceil(sampleRatio * SPECTRO_FREQ_END),
		FRAMES_PER_BUFFER/2.0) 
		- spectroData->startIndex;

	cbState = new CallbackState{spectroData, &formant};
}

void streamClass::start_stream(int deviceInput) {
	PaStreamParameters inputParameters;

	memset(&inputParameters, 0, sizeof(inputParameters));
	inputParameters.channelCount = NUM_CHANNELS;
	inputParameters.device = deviceInput;
	inputParameters.hostApiSpecificStreamInfo = NULL;
	inputParameters.sampleFormat = paFloat32;
	inputParameters.suggestedLatency = Pa_GetDeviceInfo(deviceInput)->defaultLowInputLatency;

	err = Pa_OpenStream(
		&stream,
		&inputParameters,
		NULL,
		SAMPLE_RATE,
		FRAMES_PER_BUFFER,
		paNoFlag,
		streamCallback,
		cbState
	);

        checkError(err);

        err = Pa_StartStream(stream);
        checkError(err);
}

void streamClass::stop_stream() {
    err = Pa_CloseStream(stream);
	checkError(err);

	err = Pa_Terminate();
	checkError(err);

	fftw_destroy_plan(spectroData->p);
	fftw_free(spectroData->in);
	fftw_free(spectroData->out);
	free(spectroData);
}

void streamClass::print_devices() {
	int numDevices = Pa_GetDeviceCount();
	printf("Number of devices %d\n", numDevices);

	if (numDevices < 0)
	{
		printf("Error getting device count!");
		exit(EXIT_FAILURE);
	}
	else if (numDevices == 0)
	{
		printf("No available audio devices on this machine!");
		exit(EXIT_SUCCESS);
	}

	const PaDeviceInfo* deviceInfo;
	for (size_t i = 0; i < numDevices; i++)
	{
		deviceInfo = Pa_GetDeviceInfo(i);
		printf("Device %d:\n", (int)i);
		printf("   name: %s\n", deviceInfo->name);
		printf("   maxInputChannels: %d\n", deviceInfo->maxInputChannels);
		printf("   maxOutputChannels: %d\n", deviceInfo->maxOutputChannels);
		printf("   defaultSampleRate: %f\n", deviceInfo->defaultSampleRate);
	}
}

std::vector<double> streamClass::get_formants() {
	return formant.get_formants();
}

// ---------------------------------------------------------------------------------
// 
// Main function // Add some ifdef to make it only compile if the standalone file is compiled.
//
// ---------------------------------------------------------------------------------

int main() {

    streamClass strmcls;

    // strmcls.print_devices();

    strmcls.start_stream();

	Pa_Sleep(10 * 1000);

    strmcls.stop_stream();

	return EXIT_SUCCESS;
} 

// ---------------------------------------------------------------------------------
// 
// Main function // Add some ifdef to make it only compile if the standalone file is compiled.
//
// ---------------------------------------------------------------------------------
