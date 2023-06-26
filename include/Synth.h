#ifndef SYNTH_H_
#define SYNTH_H_

#include <stdint.h>
#include "Voice.h"
#include "Constants.h"

// Defining a monophonic synth for now
typedef struct Synth_t {
    Voice_t voice;
    float frequencyTable[NOTES];
} Synth_t;

void synth_init(Synth_t * self);
void synth_set_adsr(Synth_t * self, float a, float d, float s, float r);
void synth_press(Synth_t * self, uint8_t note);
void synth_release(Synth_t * self);
void synth_step(Synth_t * self, float * out);

#endif // SYNTH_H_