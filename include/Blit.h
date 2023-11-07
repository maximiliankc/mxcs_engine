/* MXCS Core BLIT header
   copyright Maximilian Cornwell 2023
   */
#ifndef BLIT_H
#define BLIT_H

#include <stdint.h>

#include "Constants.h"
#include "Oscillator.h"

class Blit_t {
   Oscillator_t lfo;
   Oscillator_t hfo;
   float lfSin[blockSize];
   float hfSin[blockSize];
   float lfCos[blockSize];
   float hfCos[blockSize];
   float m;

   public:
   Blit_t();
   void set_freq(float freq);
   void step(float * out);
};

#endif // BLIT_H_
