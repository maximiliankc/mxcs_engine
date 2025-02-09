/* MXCS Core Voice header
   copyright Maximilian Cornwell 2023
*/

#ifndef VOICE_H_
#define VOICE_H_
#include "Blit.h"
#include "Envelope.h"
#include "Filter.h"
#include "Oscillator.h"

enum Generator_e {
    sine = 0,
    blit = 1,
    bpblit = 2,
    square = 3,
    triangle = 4,
    sawtooth = 5
};

class Voice_t {
    Envelope_t envelope;
    Oscillator_t osc;
    Blit_t blitOsc;
    BpBlit_t bpBlitOsc;
    Biquad_Filter_t integrator1;
    Biquad_Filter_t integrator2;
    Generator_e * generator;

    public:
    Voice_t(EnvelopeSettings_t * settings, Generator_e * generator);
    void step(float * out);
    void press(float f);
    void release();
};

#endif // define VOICE_H_
