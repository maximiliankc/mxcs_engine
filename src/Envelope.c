#include <stdint.h>
#include "Envelope.h"
#include "Constants.h"
#include "Utils.h"

#define BASE_LEVEL (0.00001)
#define BASE_LEVEL_DB (100)


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

void env_init(Envelope_t * self) {
    self->state = release;
    self->amp = 0;
    env_set_adsr(self, 0, 0, 0, 0);
};

void env_step(Envelope_t * self, float * envelope) {
    for(uint8_t i = 0; i < BLOCK_SIZE; i++) {
        run_state[self->state](self);
        envelope[i] = self->amp;
    };
}

void env_press(Envelope_t * self) {
    if (self->amp < BASE_LEVEL) {
        self->amp = BASE_LEVEL; // -100 dB, and initial value
    }
    self->state = attack;
}

void env_release(Envelope_t * self) {
    self->state = release;
}

void env_set_adsr(Envelope_t * self, float a, float d, float s, float r) {
    self->a_increment = db2mag(BASE_LEVEL_DB/a);      // a is the number of samples per 100 dB
    self->d_increment = db2mag(s/d);               // d is a number of samples per 100 dB
    self->s_level = db2mag(s);                     // s is a level in dBFS
    self->r_increment = db2mag(-(BASE_LEVEL_DB+s)/r); // r is a number of samples
}

void run_off(Envelope_t * self) {
    self->amp = 0;
}

void run_attack(Envelope_t * self) {
    self->amp *= self->a_increment;
    if (self->amp >= 1.0) {
        self->amp = 1.0;
        self->state = decay;
    }
}

void run_decay(Envelope_t * self) {
    self->amp *= self->d_increment;
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

#ifdef SYNTH_TEST_
void test_envelope(const float a, const float d, const float s, const float r,\
                   const unsigned int presses, unsigned int pressNs[],\
                   const unsigned int releases, unsigned int releaseNs[],\
                   const unsigned int n, float envOut[]) {
    // parameters:  a: attack time (in samples)
    //              d: decay time (in samples)
    //              s: sustain level (amplitude between 0 and 1)
    //              r: release time (in samples)
    //              pressNs: times at which to press
    //              presses: number of presses
    //              releaseNs: times at which to release
    //              releaseNs: number of releases
    //              n: number of samples to iterate over.
    //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
    //              envOut: generated envelope
    Envelope_t env;
    unsigned int pressCount = 0;
    unsigned int releaseCount = 0;
    env_init(&env);
    env_set_adsr(&env, a, d, s, r);
    for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
        if(pressCount < presses && i >= pressNs[pressCount]) {
            env_press(&env);
            pressCount++;
        }
        if(releaseCount < releases && i >= releaseNs[releaseCount]) {
            env_release(&env);
            releaseCount++;
        }
        env_step(&env, envOut + i);
    }
}
#endif // SYNTH_TEST_
