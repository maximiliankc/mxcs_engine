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
typedef struct Synth_t {
    Voice_t voice;
    EnvelopeSettings_t settings;
    Modulator_t mod;
    float frequencyTable[NOTES];
    uint8_t currentNote;
} Synth_t;

void synth_init(Synth_t * self);
void synth_set_attack(Synth_t * self, float a);
void synth_set_decay(Synth_t * self, float d);
void synth_set_sustain(Synth_t * self, float s);
void synth_set_release(Synth_t * self, float r);
void synth_press(Synth_t * self, uint8_t note);
void synth_release(Synth_t * self, uint8_t note);
void synth_step(Synth_t * self, float * out);

#endif // SYNTH_H_