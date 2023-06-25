#ifndef OSCILLATOR_H
#define OSCILLATOR_H

// Two channels in and out, only control over phase/magnitude is through starting impulse
typedef struct Oscillator_t {
    float c;        // cos(theta)
    float s;        // sin(theta)
    float yrPrev;   // yr[n-1]
    float yjPrev;   // yj[n-1]
} Oscillator_t;

void osc_init(Oscillator_t * self);
void osc_setF(Oscillator_t * self, float f);
void osc_step(Oscillator_t * self, float * cosOut, float * sinOut);

#endif
