/* MXCS Core Modulator header
   copyright Maximilian Cornwell 2023
*/
#ifndef MODULATOR_H_
#define MODULATOR_H_

#include "Oscillator.h"

class Modulator_t {
    float samplingFrequency;
    public:
    Oscillator_t lfo;
    float modRatio;

    Modulator_t(float samplingFrequency);
    void set_freq(float frequency);
    void step(float * signal);
};

#endif // MODULATOR_H_
