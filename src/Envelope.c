/* MXCS Core Envelope implementation
   copyright Maximilian Cornwell 2023
*/
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
void set_adsr(EnvelopeSettings_t * self);

typedef void (*run_state_t)(Envelope_t *);

// the order here needs to be kept in sync with the EnvelopeState_t enum
const run_state_t run_state[] = {run_off,
                                 run_attack,
                                 run_decay,
                                 run_sustain,
                                 run_release};

void env_init(Envelope_t * self, EnvelopeSettings_t * settings) {
    self->state = release;
    self->amp = 0;
    self->settings = settings;
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

void run_off(Envelope_t * self) {
    self->amp = 0;
}

void run_attack(Envelope_t * self) {
    self->amp *= self->settings->a_increment;
    if (self->amp >= 1.0) {
        self->amp = 1.0;
        self->state = decay;
    }
}

void run_decay(Envelope_t * self) {
    self->amp *= self->settings->d_increment;
    if (self->amp <= self->settings->s_level) {
        self->amp = self->settings->s_level;
        self->state = sustain;
    }
}

void run_sustain(Envelope_t * self) {
    self->amp = self->settings->s_level;
}

void run_release(Envelope_t * self) {
    self->amp *= self->settings->r_increment; // linear shift for now
}

void env_set_attack(EnvelopeSettings_t * self, float a) {
    self->a = a;
    set_adsr(self);
}

void env_set_decay(EnvelopeSettings_t * self, float d) {
    self->d = d;
    set_adsr(self);
}

void env_set_sustain(EnvelopeSettings_t * self, float s) {
    self->s = s;
    set_adsr(self);
}

void env_set_release(EnvelopeSettings_t * self, float r) {
    self->r = r;
    set_adsr(self);
}

void env_settings_init(EnvelopeSettings_t * self) {
    self->a = 0;
    self->d = 0;
    self->s = 0;
    self->r = 0;
    set_adsr(self);
}

void set_adsr(EnvelopeSettings_t * self) {
    self->a_increment = db2mag(BASE_LEVEL_DB/self->a);      // a is the number of samples per 100 dB
    self->d_increment = db2mag(self->s/self->d);               // d is a number of samples per 100 dB
    self->s_level = db2mag(self->s);                     // s is a level in dBFS
    self->r_increment = db2mag(-(BASE_LEVEL_DB+self->s)/self->r); // r is a number of samples
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
    EnvelopeSettings_t adsr;
    unsigned int pressCount = 0;
    unsigned int releaseCount = 0;
    env_init(&env, &adsr);
    env_set_attack(&adsr, a);
    env_set_decay(&adsr, d);
    env_set_sustain(&adsr, s);
    env_set_release(&adsr, r);
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
