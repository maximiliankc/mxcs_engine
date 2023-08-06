/* MXCS Core Modulator header
   copyright Maximilian Cornwell 2023
*/
#ifndef MODULATOR_H_
#define MODULATOR_H_

#include "Oscillator.h"

typedef struct Modulator_t {
    Oscillator_t lfo;
    float modRatio;
} Modulator_t;

void mod_init(Modulator_t * self);
void mod_step(Modulator_t * self, float * signal);

#endif // MODULATOR_H_