/* MXCS Core Voice header
   copyright Maximilian Cornwell 2023
*/

#ifndef VOICE_H_
#define VOICE_H_
#include "Envelope.h"
#include "Oscillator.h"

class Voice_t {
        Envelope_t envelope;
        Oscillator_t osc;
    public:
    Voice_t(EnvelopeSettings_t * settings);
    void step(float * out);
    void press(float f);
    void release();
};

#endif // define VOICE_H_