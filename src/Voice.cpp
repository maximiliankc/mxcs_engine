/* MXCS Core Voice implementation
   copyright Maximilian Cornwell 2023
*/

#include <stdint.h>
#include "Voice.h"
#include "Constants.h"

Voice_t::Voice_t(EnvelopeSettings_t * settings) {
    env_init(&envelope, settings);
}

void Voice_t::step(float * out) {
    float cosOut[BLOCK_SIZE];
    float sinOut[BLOCK_SIZE];

    env_step(&envelope, out);
    osc.step(cosOut, sinOut);

    // apply envelope to sine out
    for (uint8_t i=0; i < BLOCK_SIZE; i++) {
        out[i] *= sinOut[i];
    }
}

void Voice_t::press(float f) {
    env_press(&envelope);
    osc.set_freq(f);
}

void Voice_t::release() {
    env_release(&envelope);
}


#ifdef SYNTH_TEST_
extern "C" {
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
        EnvelopeSettings_t settings;
        Voice_t voice(&settings);
        unsigned int pressCount = 0;
        unsigned int releaseCount = 0;
        env_set_attack(&settings, a);
        env_set_decay(&settings, d);
        env_set_sustain(&settings, s);
        env_set_release(&settings, r);
        for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
            if(pressCount < presses && i >= pressNs[pressCount]) {
                voice.press(f);
                pressCount++;
            }
            if(releaseCount < releases && i >= releaseNs[releaseCount]) {
                voice.release();
                releaseCount++;
            }
            voice.step(envOut + i);
        }
    }
}
#endif // SYNTH_TEST_
