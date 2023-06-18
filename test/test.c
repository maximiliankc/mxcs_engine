#include <stdint.h>
#include <stdio.h>
#include "Constants.h"
#include "Oscillator.h"
#include "Envelope.h"
#include "Utils.h"
#include "Voice.h"


void test_oscillator(const float f, const unsigned int n, float * cosOut, float * sinOut) {
    // parameters:  f: normalised frequency (i.e. fraction of fs)
    //              n: number of samples to iterate over.
    //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
    //              sinOut/cosOut: sin/cos output of the oscillator

    Oscillator_t osc;
    osc_init(&osc, f);
    for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
        osc_step(&osc, cosOut+i, sinOut+i);
    }
}


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
    env_init(&env, a, d, s, r);
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


void test_voice(const float a, const float d, const float s, const float r, const float f,\
                   const unsigned int presses, unsigned int pressNs[],\
                   const unsigned int releases, unsigned int releaseNs[],\
                   const unsigned int n, float envOut[]) {
    // parameters:  a: attack time (in samples)
    //              d: decay time (in samples)
    //              s: sustain level (amplitude between 0 and 1)
    //              r: release time (in samples)
    //              f: frequency to run at (normalised)
    //              pressNs: times at which to press
    //              presses: number of presses
    //              releaseNs: times at which to release
    //              releaseNs: number of releases
    //              n: number of samples to iterate over.
    //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
    //              envOut: generated envelope
    Voice_t voice;
    unsigned int pressCount = 0;
    unsigned int releaseCount = 0;
    voice_init(&voice, a, d, s, r, f);
    for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
        if(pressCount < presses && i >= pressNs[pressCount]) {
            voice_press(&voice, f);
            pressCount++;
        }
        if(releaseCount < releases && i >= releaseNs[releaseCount]) {
            voice_release(&voice);
            releaseCount++;
        }
        voice_step(&voice, envOut + i);
    }
}


void test_db2mag(const unsigned int n, float inOut[]) {
    // parameters: inOut: input/output array
    //             n: number of values in input/output array
    for(unsigned int i = 0; i<n; i++) {
        inOut[i] = db2mag(inOut[i]);
    }
}