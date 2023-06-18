#include <stdint.h>
#include "Voice.h"
#include "Constants.h"

void voice_init(Voice_t * self, float a, float d, float s, float r, float f) {
    osc_init(&(self->osc), f);
    env_init(&(self->envelope), a, d, s, r);
}

void voice_step(Voice_t * self, float * out) {
    float cosOut[BLOCK_SIZE];
    float sinOut[BLOCK_SIZE];

    env_step(&(self->envelope), out);
    osc_step(&(self->osc), cosOut, sinOut);

    // apply envelope to sine out
    for (uint8_t i=0; i < BLOCK_SIZE; i++) {
        out[i] *= sinOut[i];
    }
}

void voice_press(Voice_t * self, float f) {
    env_press(&(self->envelope));
    osc_setF(&(self->osc), f);
}

void voice_release(Voice_t * self) {
    env_release(&(self->envelope));
}