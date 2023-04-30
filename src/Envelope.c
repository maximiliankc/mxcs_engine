#include <stdint.h>
#include "Envelope.h"
#include "Constants.h"

void run_off(Envelope_t * self, float * envelope);
void run_attack(Envelope_t * self, float * envelope);
void run_decay(Envelope_t * self, float * envelope);
void run_sustain(Envelope_t * self, float * envelope);
void run_release(Envelope_t * self, float * envelope);

typedef void (*run_state_t)(Envelope_t *, float *);

// the order here needs to be kept in sync with the EnvelopeState_t enum
const run_state_t run_state[] = {run_off,
                                 run_attack,
                                 run_decay,
                                 run_sustain,
                                 run_release};

void env_init(Envelope_t * self, float a, float d, float s, float r) {
    self->state = off;
    self->amp = 0;
    env_set_adsr(self, a, d, s, r);
};

void env_step(Envelope_t * self, float * envelope) {
    for(uint8_t i = 0; i < BLOCK_SIZE; i++) {
        run_state[self->state](self, envelope+i);
    };
}

void env_press(Envelope_t * self) {
    self->state = attack;
}

void env_release(Envelope_t * self) {
    self->state = attack;
}

void env_set_adsr(Envelope_t * self, float a, float d, float s, float r) {
    self->state = off;
    self->amp = 0;
}

void run_off(Envelope_t * self, float * envelope) {
    *envelope = 0;
    self->state = off;
}

void run_attack(Envelope_t * self, float * envelope) {
    *envelope = 1.0;
    self->state = decay;
}

void run_decay(Envelope_t * self, float * envelope) {
    *envelope = 0.5;
    self->state = sustain;
}

void run_sustain(Envelope_t * self, float * envelope) {
        *envelope = 0.25;
    self->state = release;
}

void run_release(Envelope_t * self, float * envelope) {
    *envelope = 0.1;
    self->state = off;
}
