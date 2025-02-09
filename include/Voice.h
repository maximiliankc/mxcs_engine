/* MXCS Core Voice header
   copyright Maximilian Cornwell 2023
*/

#ifndef VOICE_H_
#define VOICE_H_
#include "Blit.h"
#include "Envelope.h"
#include "OscillatorLut.h"

enum Generator_e {
    sine = 0,
    blit = 1,
    bpblit = 2
};

class Voice_t {
    Envelope_t envelope;
    OscillatorLut_t osc;
    Blit_t blitOsc;
    BpBlit_t bpBlitOsc;
    Generator_e * generator;

    public:
    Voice_t(EnvelopeSettings_t * settings, Generator_e * generator);
    void step(float * out);
    void press(float f);
    void release();
};

#endif // define VOICE_H_
