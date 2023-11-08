/* MXCS Core Voice header
   copyright Maximilian Cornwell 2023
*/

#ifndef VOICE_H_
#define VOICE_H_
#include "Blit.h"
#include "Envelope.h"
#include "Oscillator.h"

enum Generator_t {
    sine = 0,
    blit = 1
};

class Voice_t {
    Envelope_t envelope;
    Oscillator_t osc;
    Blit_t blitOsc;
    Generator_t * generator;

    void osc_step(float * out);
    void blit_step(float * out);

    public:
    Voice_t(EnvelopeSettings_t * settings, Generator_t * generator);
    void step(float * out);
    void press(float f);
    void release();
};

#endif // define VOICE_H_
