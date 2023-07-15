#include <stdint.h>
#include "Modulator.h"
#include "Constants.h"

void mod_init(Modulator_t * self) {
    osc_init(&(self->lfo));
    self->modRatio = 0;
}


void mod_step(Modulator_t * self, float * signal) {
    float modCos[BLOCK_SIZE];
    float modSin[BLOCK_SIZE];
    osc_step(&(self->lfo), modCos, modSin);

    for (uint8_t i = 0; i < BLOCK_SIZE; i++) {
        signal[i] *= self->modRatio*modCos[i] + 1 - self->modRatio;
    }
}