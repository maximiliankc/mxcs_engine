#ifndef OSC_LUT_H
#define OSC_LUT_H

class OscillatorLut_t {
    float phase;
    float frequency;

    public:
    OscillatorLut_t();
    void set_freq(float f);
    float get_phase();
    void adjust_phase(float phase);
    void step(float * out);
};


#endif