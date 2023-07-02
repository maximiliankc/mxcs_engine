/* MXCS Core Voice implementation
   copyright Maximilian Cornwell 2023
*/

#include <stdint.h>
#include "Voice.h"
#include "Constants.h"

void voice_init(Voice_t * self) {
    osc_init(&(self->osc));
    env_init(&(self->envelope));
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


#ifdef SYNTH_TEST_
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
    voice_init(&voice);
    env_set_adsr(&voice.envelope, a, d, s, r);
    osc_setF(&voice.osc, f);
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
#endif // SYNTH_TEST_
