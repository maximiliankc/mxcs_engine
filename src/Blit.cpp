/* MXCS synthesizer core BLIT implementation
   copyright Maximilian Cornwell 2023
*/
#include <stdio.h>

#include "Blit.h"
#include "Constants.h"

const float threshold = 1e-6f; // TODO figure out the best threshold

void msinc(float * out, float * lfCos, float * lfSin, float * hfCos, float * hfSin, float M) {
    for(uint8_t i = 0; i<blockSize; i++) {
        printf("%d %g %g %g %g", i, lfSin[i], hfSin[i], lfCos[i], hfCos[i]);
        if (lfCos[i] > threshold || lfCos[i] < -threshold) {
            out[i] = hfCos[i]/(M*lfCos[i]);
            printf(" . ");
        } else {
            out[i] = hfSin[i]/lfSin[i];
            printf(" - ");
        }
        printf("%g\n", out[i]);
    }
    printf("\n----------------\n");
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
        float lfSin[blockSize];
        float lfCos[blockSize];
        float hfSin[blockSize];
        float hfCos[blockSize];
        Oscillator_t lfOsc;
        Oscillator_t hfOsc;

        float M = blit_m(f);

        lfOsc.set_freq(f/2);
        hfOsc.set_freq(M*f/2);
        printf("M = %g\n", M);
        for(unsigned int i = 0; i < samples-blockSize; i+=blockSize) {
            printf("%d\n", i);
            lfOsc.step(lfCos, lfSin);
            hfOsc.step(hfCos, hfSin);
            msinc(&out[i], lfCos, lfSin, hfCos, hfSin, M);
        }
    }
}

#endif