/* MXCS synthesizer core BLIT implementation
   copyright Maximilian Cornwell 2023
*/

#include "Blit.h"
#include "Constants.h"


const float threshold = 0.01; // Could be further refined

Blit_t::Blit_t() {
    m = 0;
}

void Blit_t::set_freq(float freq) {
    int16_t period = (int16_t)(0.4f/freq);
    m = (float)(2*period + 1);
    lfo.set_freq(freq/2.f);
    hfo.set_freq(m*freq/2.f); // why f/2?
}

void Blit_t::step(float * out) {
    lfo.step(lfCos, lfSin);
    hfo.step(hfCos, hfSin);
    // calculate msinc
    for(uint8_t i = 0; i<blockSize; i++) {
        if (m*m*lfSin[i]*lfSin[i] > threshold) {
            out[i] = hfSin[i]/(m*lfSin[i]);
        } else {
            out[i] = hfCos[i]/(lfCos[i]);
            // printf("%g over %g \n", out[i], hfSin[i]/(m*lfSin[i]));
        }
        if (out[i] > 1) {
            // printf("Bottom: %g", m*m*lfSin[i]*lfSin[i]);
            // printf("  Sin: %g", hfSin[i]/(m*lfSin[i]));
            // printf("  Cos: %g\n", hfCos[i]/(lfCos[i]));
            // printf("Sin Bottom: %g\n", lfSin[i]);
        }

    }
    // PLL, needed to keep low/high frequencies in sync
    // might be better to adjust frequency instead of phase!
    // but this seems to work well enough
    float phase_error = m*lfo.get_phase() - hfo.get_phase();
    hfo.adjust_phase(phase_error);
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
        Blit_t blit;

        blit.set_freq(f);
        for(unsigned int i = 0; i < samples-blockSize; i+=blockSize) {
            blit.step(&out[i]);
        }
    }

    float test_blit_m(float f) {
        return blit_m(f);
    }
}

#endif
