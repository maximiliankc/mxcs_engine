#include <math.h>

#include "OscillatorLut.h"
#include "SineTable.h"
#include "Constants.h"

#define FLOAT_CONVERSION 4294967296 //2**32

OscillatorLut_t::OscillatorLut_t() {
    phase = 0;
}

void OscillatorLut_t::set_freq(float f) {
    double float_freq = (double)f;
    float_freq = FLOAT_CONVERSION*float_freq;
    frequency = (uint32_t)float_freq;
}

float OscillatorLut_t::get_phase() {
    return 2*M_PI*(double)phase/FLOAT_CONVERSION;
}

void OscillatorLut_t::adjust_phase(float phase_) {
    double normalised_phase = phase_/(2*M_PI);
    normalised_phase *= FLOAT_CONVERSION;
    phase = (uint32_t)normalised_phase;
}

void OscillatorLut_t::step(float * out) {
    uint32_t phase_index;
    for (uint16_t i = 0; i < blockSize; i++) {
        phase_index = phase>>20;
        out[i] = sine_table[phase_index];
        // update phase
        // printf("phase_index %d, phase %d\n", phase_index, phase);
        phase += frequency; // relying on overflow!
    }
}

#ifdef SYNTH_TEST_
extern "C" {
    void test_lut_oscillator(const float f, const unsigned int n, float * cosOut, float * sinOut) {
        // parameters:  f: normalised frequency (i.e. fraction of fs)
        //              n: number of samples to iterate over.
        //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
        //              sinOut/cosOut: sin/cos output of the oscillator

        OscillatorLut_t osc_sin;
        OscillatorLut_t osc_cos;
        osc_sin.set_freq(f);
        osc_cos.set_freq(f);
        osc_cos.adjust_phase(M_PI/2);
        for(unsigned int i=0; i+blockSize <= n; i+= blockSize) {
            osc_sin.step(sinOut+i);
            osc_cos.step(cosOut+i);
        }
    }
}
#endif
