/* MXCS synthesizer core BLIT implementation
   copyright Maximilian Cornwell 2023
*/

#include "Blit.h"
#include "Constants.h"


const float threshold = 0.005; // Could be further refined?

float blit_m(float f);

Blit_t::Blit_t() {
    m = 0;
}

void Blit_t::set_freq(float freq) {
    m = blit_m(freq);
    if (freq > 0.4) {
        freq = 0; // frequencies above 0.4 are unsupproted
    }
    lfo.set_freq(freq/2.f);
    hfo.set_freq(m*freq/2.f);
    sync_phase();
}

void Blit_t::step(float * out) {
    lfo.step(lfCos, lfSin);
    hfo.step(hfCos, hfSin);
    // calculate msinc
    for(uint8_t i = 0; i<blockSize; i++) {
        out[i] = hfSin[i]/(m*lfSin[i]);
        if ((m*m*lfSin[i]*lfSin[i] < threshold) || (out[i]*out[i] > 1)) {
            out[i] = hfCos[i]/(lfCos[i]);
        }
    }
    sync_phase();
}

void Blit_t::sync_phase(void) {
    // PLL, needed to keep low/high frequencies in sync
    // might be better to adjust frequency instead of phase!
    // but this seems to work well enough
    float phase_error = m*lfo.get_phase() - hfo.get_phase();
    hfo.adjust_phase(phase_error);
}

void BpBlit_t::set_freq(float freq) {
    if (freq > 0.2) {
        freq = 0; // frequencies above 0.25 aren't supported by bpblit!
    }
    m = blit_m(2*freq) - 1;
    lfo.set_freq(freq);
    hfo.set_freq(m*freq);
    sync_phase();
}

float blit_m(float f) {
    int16_t period = (int16_t)(0.4f/f);
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

    void test_bp_blit(float * out, float f, unsigned int samples) {
        BpBlit_t bpBlit;

        bpBlit.set_freq(f);
        for(unsigned int i = 0; i < samples-blockSize; i+=blockSize) {
            bpBlit.step(&out[i]);
        }
    }

    float test_blit_m(float f) {
        return blit_m(f);
    }
}

#endif
