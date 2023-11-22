/* MXCS Core Oscillator header
   copyright Maximilian Cornwell 2023
*/
#ifndef OSCILLATOR_H
#define OSCILLATOR_H

// Two channels in and out, only control over phase/magnitude is through starting impulse
class Oscillator_t {
    float c;        // cos(theta)
    float s;        // sin(theta)
    float yrPrev;   // yr[n-1]
    float yjPrev;   // yj[n-1]

    public:
    Oscillator_t();
    void set_freq(float f);
    float get_phase();
    void adjust_phase(float phase);
    void step(float * cosOut, float * sinOut);
};

#endif
