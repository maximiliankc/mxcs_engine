/* MXCS Core Synth header
   copyright Maximilian Cornwell 2023
*/
#ifndef SYNTH_H_
#define SYNTH_H_

#include <stdint.h>
#include "Constants.h"
#include "Voice.h"
#include "Modulator.h"

// Defining a monophonic synth for now
class Synth_t {
    EnvelopeSettings_t settings;
    Voice_t voice;
    Modulator_t mod;
    float frequencyTable[NOTES];
    uint8_t currentNote;

    public:
    Synth_t();
    void set_attack(float a);
    void set_decay(float d);
    void set_sustain(float s);
    void set_release(float r);
    void set_mod_f(float freq);
    void set_mod_depth(float depth);
    void press(uint8_t note);
    void release(uint8_t note);
    void step(float * out);

    #ifdef SYNTH_TEST_
    float * get_freq_table();
    #endif
};

#endif // SYNTH_H_
