/* MXCS Core Synth header
   copyright Maximilian Cornwell 2023
*/
#ifndef SYNTH_H_
#define SYNTH_H_

#include <stdint.h>
#include "Constants.h"
#include "Voice.h"
#include "Modulator.h"
#include "Filter.h"

// Defining a monophonic synth for now
class Synth_t {
    float samplingFrequency;
    EnvelopeSettings_t envelopeSettings;
    Generator_e generator;
    Voice_t voice;
    Modulator_t mod;
    Biquad_Filter_t lpFilter;
    float lpF;
    float lpRes;
    Biquad_Filter_t hpFilter;
    float hpF;
    float hpRes;
    float frequencyTable[notes];
    uint8_t currentNote;

    public:
    Synth_t(float _samplingFrequency);
    void set_attack(float a);
    void set_decay(float d);
    void set_sustain(float s);
    void set_release(float r);
    void set_mod_f(float freq);
    void set_mod_depth(float depth);
    void set_lpf_freq(float freq);
    void set_lpf_res(float res);
    void set_hpf_freq(float freq);
    void set_hpf_res(float res);
    void set_generator(Generator_e gen);
    void press(uint8_t note);
    void release(uint8_t note);
    void step(float * out);

    #ifdef SYNTH_TEST_
    float * get_freq_table();
    #endif
};

#endif // SYNTH_H_
