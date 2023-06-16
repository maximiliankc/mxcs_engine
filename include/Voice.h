#ifndef VOICE_H_
#define VOICE_H_
#include "Envelope.h"
#include "Oscillator.h"

typedef struct Voice_t {
    Envelope_t envelope;
    Oscillator_t osc;
} Voice_t;

void voice_init(Voice_t * self, float a, float d, float s, float r, float f);
void voice_step(Voice_t * self, float * out);

#endif // define VOICE_H_