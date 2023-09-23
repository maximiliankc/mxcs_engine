/* MXCS Core Voice header
   copyright Maximilian Cornwell 2023
*/

#ifndef VOICE_H_
#define VOICE_H_
#include "Envelope.h"
#include "Oscillator.h"

typedef struct Voice_t {
    Envelope_t envelope;
    Oscillator_t osc;
} Voice_t;

void voice_init(Voice_t * self, EnvelopeSettings_t * settings);
void voice_step(Voice_t * self, float * out);
void voice_press(Voice_t * self, float f);
void voice_release(Voice_t * self);

#endif // define VOICE_H_