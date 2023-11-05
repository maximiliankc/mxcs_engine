/* MXCS synthesizer core BLIT implementation
   copyright Maximilian Cornwell 2023
*/

#include "Blit.h"
#include "Constants.h"

const float threshold = 1e-6f; // TODO figure out the best threshold

BlSigGen_t::BlSigGen_t() {
    m = 0;
}

void BlSigGen_t::set_freq(float freq) {
    int16_t period = (int16_t)(0.5f/freq);
    m = (float)(2*period + 1);
    hfo.set_freq(m*freq); // have this as f/2
    lfo.set_freq(freq);
}

void BlSigGen_t::step(float * out) {
    for(uint8_t i = 0; i<blockSize; i++) {
        if (lfCos[i] > threshold || lfCos[i] < -threshold) {
            out[i] = hfCos[i]/(m*lfCos[i]);
        } else {
            out[i] = hfSin[i]/lfSin[i];
        }
    }
}

float blit_m(float f) {
    int16_t period = (int16_t)(0.5f/f);
    period = 2*period + 1;
    return (float)period;
}

#ifdef SYNTH_TEST_
#include "Oscillator.h"
extern "C" {
    void test_blit(float * out, float f, unsigned int samples) {
        BlSigGen_t blit;

        blit.set_freq(f);
        for(unsigned int i = 0; i < samples-blockSize; i+=blockSize) {
            blit.step(out);
        }
    }

    float test_blit_m(float f) {
        return blit_m(f);
    }
}

#endif
