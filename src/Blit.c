/* MXCS synthesizer core BLIT implementation
   copyright Maximilian Cornwell 2023
*/
#include <stdio.h>

#include "Blit.h"
#include "Constants.h"

#define THRESHOLD (1e-6f) // TODO figure out the best threshold

void msinc(float * out, float * lfCos, float * lfSin, float * hfCos, float * hfSin, float M) {
    for(uint8_t i = 0; i<BLOCK_SIZE; i++) {
        printf("%d %g %g %g %g", i, lfSin[i], hfSin[i], lfCos[i], hfCos[i]);
        if (lfCos[i] > THRESHOLD || lfCos[i] < -THRESHOLD) {
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

void test_blit(float * out, float f, unsigned int samples) {
    float lfSin[BLOCK_SIZE];
    float lfCos[BLOCK_SIZE];
    float hfSin[BLOCK_SIZE];
    float hfCos[BLOCK_SIZE];
    Oscillator_t lfOsc;
    Oscillator_t hfOsc;

    osc_init(&lfOsc);
    osc_init(&hfOsc);
    float M = blit_m(f);
    osc_setF(&lfOsc, f/2);
    osc_setF(&hfOsc, M*f/2);
    printf("M = %g\n", M);
    for(unsigned int i = 0; i < samples-BLOCK_SIZE; i+=BLOCK_SIZE) {
        printf("%d\n", i);
        osc_step(&lfOsc, lfCos, lfSin);
        osc_step(&hfOsc, hfCos, hfSin);
        msinc(&out[i], lfCos, lfSin, hfCos, hfSin, M);
    }
}

#endif