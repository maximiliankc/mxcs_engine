#ifndef OSC_LUT_H
#define OSC_LUT_H
#include <stdint.h>

class OscillatorLut_t {
    uint32_t phase; // <0,32> format
    uint32_t frequency; // <0,32> format

    public:
    OscillatorLut_t();
    void set_freq(float f);
    float get_phase();
    void adjust_phase(float phase);
    void step(float * out);
};

#endif
