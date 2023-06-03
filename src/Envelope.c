#include <stdint.h>
#include "Envelope.h"
#include "Constants.h"

void run_off(Envelope_t * self);
void run_attack(Envelope_t * self);
void run_decay(Envelope_t * self);
void run_sustain(Envelope_t * self);
void run_release(Envelope_t * self);

typedef void (*run_state_t)(Envelope_t *);

// the order here needs to be kept in sync with the EnvelopeState_t enum
const run_state_t run_state[] = {run_off,
                                 run_attack,
                                 run_decay,
                                 run_sustain,
                                 run_release};

void env_init(Envelope_t * self, float a, float d, float s, float r) {
    self->state = release;
    self->amp = 0;
    env_set_adsr(self, a, d, s, r);
};

void env_step(Envelope_t * self, float * envelope) {
    for(uint8_t i = 0; i < BLOCK_SIZE; i++) {
        run_state[self->state](self);
        envelope[i] = self->amp;
    };
}

void env_press(Envelope_t * self) {
    self->amp = 0.00001; // -100 dB, and initial value
    self->state = attack;
}

void env_release(Envelope_t * self) {
    self->state = release;
}

void env_set_adsr(Envelope_t * self, float a, float d, float s, float r) {
    self->a_increment = a;           // a is a number of samples
    self->d_increment = d;     // d is a number of samples
    self->s_level = s;                   // s is a level
    self->r_increment = r;            // r is a number of samples
}

void run_off(Envelope_t * self) {
    self->amp = 0;
}

void run_attack(Envelope_t * self) {
    self->amp *= self->a_increment; // linear shift for now
    if (self->amp >= 1.0) {
        self->amp = 1.0;
        self->state = decay;
    }
}

void run_decay(Envelope_t * self) {
    self->amp *= self->d_increment; // linear shift for now
    if (self->amp <= self->s_level) {
        self->amp = self->s_level;
        self->state = sustain;
    }
}

void run_sustain(Envelope_t * self) {
    self->amp = self->s_level;
}

void run_release(Envelope_t * self) {
    self->amp *= self->r_increment; // linear shift for now
}
