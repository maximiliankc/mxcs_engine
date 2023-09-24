/* MXCS Core Oscillator implementation
   copyright Maximilian Cornwell 2023
*/

#include <stdint.h>
#include <math.h>
#include "Oscillator.h"
#include "Constants.h"


void osc_init(Oscillator_t * self) {
    osc_setF(self, 0);
    self->yrPrev = 1.0;
    self->yjPrev = 0.0;
}

void osc_setF(Oscillator_t * self, float f) {
    // f should be relative to fs,
    self->c = cosf(2*M_PI*f);
    self->s = sinf(2*M_PI*f);
}

void osc_step(Oscillator_t * self, float * yr, float * yj) {
    // thinking of it as a complex exponential
    // y[n] = e^(j*theta)*y[n-1]
    // alternatively, like a matrix:
    // (yr[n]  = (cos(theta) -sin(theta) (yr[n-1]
    //  yj[n]) =  sin(theta)  cos(theta)) yj[n-1])
    float pwr;
    float scale;

    // use the state to calculate the first samples in the block
    yr[0] = self->c*self->yrPrev - self->s*self->yjPrev;
    yj[0] = self->s*self->yrPrev + self->c*self->yjPrev;

    // need to normalise the power, otherwise magnitude will drift due to numerical error
    // once per block should be enough (depending on block length!)
    pwr = yr[0]*yr[0] + yj[0]*yj[0];
    // scale is 1st order taylor series approximation of inverse square root
    scale = 1.5 - 0.5*pwr;
    yr[0] = scale*yr[0];
    yj[0] = scale*yj[0];

    // calculate the rest of the block
    for (uint8_t i = 1; i < BLOCK_SIZE; i++) {
        yr[i] = self->c*yr[i-1] - self->s*yj[i-1];
        yj[i] = self->s*yr[i-1] + self->c*yj[i-1];
    }

    // save the last values into the oscillator state
    self->yrPrev = yr[BLOCK_SIZE-1];
    self->yjPrev = yj[BLOCK_SIZE-1];
}


#ifdef SYNTH_TEST_
extern "C" {
    void test_oscillator(const float f, const unsigned int n, float * cosOut, float * sinOut) {
        // parameters:  f: normalised frequency (i.e. fraction of fs)
        //              n: number of samples to iterate over.
        //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
        //              sinOut/cosOut: sin/cos output of the oscillator

        Oscillator_t osc;
        osc_init(&osc);
        osc_setF(&osc, f);
        for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
            osc_step(&osc, cosOut+i, sinOut+i);
        }
    }
}
#endif // SYNTH_TEST_
