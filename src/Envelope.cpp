/* MXCS Core Envelope implementation
   copyright Maximilian Cornwell 2023
*/
#include <stdint.h>
#include "Envelope.h"
#include "Constants.h"
#include "Utils.h"

#define BASE_LEVEL (0.00001)
#define BASE_LEVEL_DB (100)

typedef void (*run_state_t)(Envelope_t *);

void run_off(Envelope_t * self);
void run_attack(Envelope_t * self);
void run_decay(Envelope_t * self);
void run_sustain(Envelope_t * self);
void run_release(Envelope_t * self);

EnvelopeSettings_t::EnvelopeSettings_t() {
    a = 0;
    d = 0;
    s = 0;
    r = 0;
    set_adsr();
}

void EnvelopeSettings_t::set_adsr() {
    aIncrement = db2mag(BASE_LEVEL_DB/a);      // a is the number of samples per 100 dB
    dIncrement = db2mag(s/d);               // d is a number of samples per 100 dB
    sMag = db2mag(s);                     // s is a level in dBFS
    rIncrement = db2mag(-(BASE_LEVEL_DB+s)/r); // r is a number of samples
}

void EnvelopeSettings_t::set_attack(float attackTime) {
    a = attackTime;
    set_adsr();
}

void EnvelopeSettings_t::set_decay(float decayTime) {
    d = decayTime;
    set_adsr();
}

void EnvelopeSettings_t::set_sustain(float sustainLevel) {
    s = sustainLevel;
    set_adsr();
}

void EnvelopeSettings_t::set_release(float release) {
    r = release;
    set_adsr();
}

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
    self->amp *= self->settings->aIncrement;
    if (self->amp >= 1.0) {
        self->amp = 1.0;
        self->state = decay;
    }
}

void run_decay(Envelope_t * self) {
    self->amp *= self->settings->dIncrement;
    if (self->amp <= self->settings->sMag) {
        self->amp = self->settings->sMag;
        self->state = sustain;
    }
}

void run_sustain(Envelope_t * self) {
    self->amp = self->settings->sMag;
}

void run_release(Envelope_t * self) {
    self->amp *= self->settings->rIncrement; // linear shift for now
}

#ifdef SYNTH_TEST_
extern "C" {
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
        adsr.set_attack(a);
        adsr.set_decay(d);
        adsr.set_sustain(s);
        adsr.set_release(r);
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
}
#endif // SYNTH_TEST_
