/* MXCS Core Voice header
   copyright Maximilian Cornwell 2023
*/

#ifndef VOICE_H_
#define VOICE_H_
#include "Blit.h"
#include "Envelope.h"
#include "Oscillator.h"

enum Generator_e {
    sine = 0,
    blit = 1,
    bpblit = 2
};

struct Voice_Config_t {
    Envelope_Config_t env_config;
    Generator_e generator;

    Voice_Config_t(float samplingFrequency);
    void set_attack(float a);
    void set_decay(float d);
    void set_sustain(float s);
    void set_release(float r);
    void set_generator(Generator_e gen);
};

class Voice_t {
    Voice_Config_t * config;
    Envelope_t envelope;
    Oscillator_t osc;
    Blit_t blitOsc;
    BpBlit_t bpBlitOsc;

    public:
    Voice_t(Voice_Config_t * config);
    void step(float * out);
    void press(float f);
    void release();
};

#endif // define VOICE_H_
