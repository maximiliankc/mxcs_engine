/* MXCS Core Modulator header
   copyright Maximilian Cornwell 2023
*/
#ifndef MODULATOR_H_
#define MODULATOR_H_

#include "Oscillator.h"

class Modulator_t {
    public:
        Oscillator_t lfo;
        float modRatio;
        Modulator_t();
        void step(float * signal);
};

#endif // MODULATOR_H_