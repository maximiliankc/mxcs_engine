#include <stdint.h>
#include "Envelope.h"
#include "Constants.h"

void env_init(Envelope_t * self, float a, float d, float s, float r) {
    self->state = off;
    self->amp = 0;
    env_set_adsr(self, a, d, s, r);
};

void env_step(Envelope_t * self, float * envelope) {
    for(uint8_t i = 0; i < BLOCK_SIZE; i++) {
        envelope[i] = 0;
    };
}

void env_press(Envelope_t * self) {
    self->state = off;
}

void env_release(Envelope_t * self) {
    self->state = off;
}

void env_set_adsr(Envelope_t * self, float a, float d, float s, float r) {
    self->state = off;
    self->amp = 0;
};