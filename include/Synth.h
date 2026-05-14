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

const uint8_t stackDepth = 32;
// base class for actual synth implementations
class Synth_t {
    float samplingFrequency;
    float lpF;
    float lpRes;
    float hpF;
    float hpRes;

    Modulator_t mod;
    Biquad_Filter_t lpFilter;
    Biquad_Filter_t hpFilter;

    protected:
    VoiceConfig_t voiceConfig;
    float frequencyTable[notes];

    void run_effects(float *out);

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
    virtual void press(uint8_t note) = 0;
    virtual void release(uint8_t note) = 0;
    virtual void step(float * out) = 0;

    #ifdef SYNTH_TEST_
    float * get_freq_table();
    #endif
};

// Defining a monophonic synth for now
class MonoSynth_t: public Synth_t {
    Voice_t voice;
    uint8_t currentNote;
    // should these be encapsulated into an object?
    uint8_t noteStackIndex = 0;
    uint8_t noteStack[stackDepth] = {0};
    bool enabledNotes[notes] = {0};

    public:
    MonoSynth_t(float _samplingFrequency);
    void press(uint8_t note);
    void release(uint8_t note);
    void step(float * out);
};

class PolySynth_t: public Synth_t {
    Voice_t voices[notes];

    public:
    PolySynth_t(float _samplingFrequency);
    void press(uint8_t note);
    void release(uint8_t note);
    void step(float * out);
};

#endif // SYNTH_H_
