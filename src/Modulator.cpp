/* MXCS Core Modulator implementation
   copyright Maximilian Cornwell 2023
*/
#include <stdint.h>
#include "Modulator.h"
#include "Constants.h"

Modulator_t::Modulator_t() {
    modRatio = 0;
}

void Modulator_t::step(float * signal) {
    float modCos[BLOCK_SIZE];
    float modSin[BLOCK_SIZE];

    lfo.step(modCos, modSin);
    for (uint8_t i = 0; i < BLOCK_SIZE; i++) {
        signal[i] *= modRatio*modCos[i] + 1 - modRatio;
    }
}

#ifdef SYNTH_TEST_
extern "C" {
    void test_modulator(const float f, const float ratio, const unsigned int n, float * out) {
        Modulator_t modulator;
        float signal[BLOCK_SIZE];

        modulator.modRatio = ratio;
        modulator.lfo.set_freq(f);
        for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
            for(unsigned int j = 0; j < BLOCK_SIZE; j++) {
                signal[j] = 1;
            }
            modulator.step(signal);
            for(unsigned int j = 0; j < BLOCK_SIZE; j++) {
                out[i+j] = signal[j];
            }
        }
    }
}
#endif // SYNTH_TEST_