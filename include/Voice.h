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

struct VoiceConfig_t {
    EnvelopeConfig_t envConfig;
    Generator_e generator;

    VoiceConfig_t(float samplingFrequency);
    void set_fs(float samplingFrequency);
    void set_attack(float a);
    void set_decay(float d);
    void set_sustain(float s);
    void set_release(float r);
    void set_generator(Generator_e gen);
};

class Voice_t {
    VoiceConfig_t * config = nullptr;
    Envelope_t envelope;
    Oscillator_t osc;
    Blit_t blitOsc;
    BpBlit_t bpBlitOsc;

    public:
    Voice_t();
    Voice_t(VoiceConfig_t * config);
    void set_config(VoiceConfig_t * config);
    void set_frequency(float f);
    bool is_active();
    void step(float * out);
    void press();
    void release();
};

#endif // define VOICE_H_
