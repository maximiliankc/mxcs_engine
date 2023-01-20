#ifndef OSCILLATOR_H
#define OSCILLATOR_H

// Two channels in and out, only control over phase/magnitude is through starting impulse
typedef struct Oscillator {
    float c;        // cos(theta)
    float s;        // sin(theta)
    float yrPrev;   // yr[n-1]
    float yjPrev;   // yj[n-1]
} Oscillator;

void osc_init(Oscillator * self, float f);
void osc_setF(Oscillator * self, float f);
void osc_step(Oscillator * self, float * cosOut, float * sinOut);

#endif
