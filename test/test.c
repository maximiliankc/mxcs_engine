#include <stdint.h>
#include "Constants.h"
#include "Oscillator.h"
#include "Envelope.h"


void test_oscillator(const float f, const unsigned int n, float * cosOut, float * sinOut) {
    // parameters:  f: normalised frequency (i.e. fraction of fs)
    //              n: number of samples to iterate over.
    //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
    //              sinOut/cosOut: sin/cos output of the oscillator

    Oscillator_t osc;
    osc_init(&osc, f);
    for(unsigned int i=0; i<n; i+= BLOCK_SIZE) {
        osc_step(&osc, cosOut+i, sinOut+i);
    }
}


void test_envelope(const float a, const float d, const float s, const float r,\
                   const unsigned int pressNs[], const unsigned int presses,\
                   const unsigned int releaseNs[], const unsigned int releases,\
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
    env_init(&env, a, d, s, r);
    for(unsigned int i=0; i<n; i+= BLOCK_SIZE) {
        if(pressCount < presses && n >= pressNs[pressCount]) {
            env_press(&env);
            pressCount++;
        }
        if(releaseCount < releases && n >= releaseNs[releaseCount]) {
            env_release(&env);
            releaseCount++;
        }
        env_step(&env, envOut + i);
    }
}
