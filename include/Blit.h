/* MXCS Core BLIT header
   copyright Maximilian Cornwell 2023
   */
#ifndef BLIT_H
#define BLIT_H

#include <stdint.h>

#include "Constants.h"
#include "Oscillator.h"

class Blit_t {
   float lfSin[blockSize];
   float hfSin[blockSize];
   float lfCos[blockSize];
   float hfCos[blockSize];

   protected:
   Oscillator_t lfo;
   Oscillator_t hfo;
   float m;
   void sync_phase(void);

   public:
   Blit_t();
   void set_freq(float freq);
   void step(float * out);
};

class BpBlit_t: public Blit_t {
   public:
   void set_freq(float freq);
};

#endif // BLIT_H_
