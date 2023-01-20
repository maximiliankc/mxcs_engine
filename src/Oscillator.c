#include "Oscillator.h"
#include "Constants.h"
#include <stdint.h>
#include <math.h>


void osc_init(Oscillator * self, float f) {
    osc_setF(self, f);
    self->yrPrev = 1.0;
    self->yjPrev = 0.0;
}

void osc_setF(Oscillator * self, float f) {
    self->c = cosf(2*M_PI*f);
    self->s = sinf(2*M_PI*f);
}

void osc_step(Oscillator * self, float * yr, float * yj) {
    // thinking of it as a complex exponential
    // y[n] = e^j*theta*y[n-1]
    uint8_t i;

    // use the state to calculate the first samples in the block
    yr[0] = self->c*self->yrPrev - self->s*self->yrPrev;
    yj[0] = self->s*self->yrPrev + self->c*self->yrPrev;

    // calculate the rest of the block
    for(i = 1; i < BLOCK_SIZE; i++)
    {
        yr[i] = self->c*yr[i-1] - self->s*yj[i-1];
        yj[i] = self->s*yr[i-1] + self->c*yj[i-1];
    }

    // save the last values into the oscillator state
    self->yrPrev = yr[BLOCK_SIZE-1];
    self->yjPrev = yj[BLOCK_SIZE-1];
}
