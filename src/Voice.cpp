/* MXCS Core Voice implementation
   copyright Maximilian Cornwell 2023
*/

#include <stdint.h>
#include "Voice.h"
#include "Constants.h"


Voice_t::Voice_t(EnvelopeSettings_t * settings, Generator_e * _generator): envelope(settings) {
    generator = _generator;
}

void Voice_t::step(float * out) {
    float envOut[blockSize];

    switch (*generator)
    {
    case sine:
        osc.step(out);
        break;

    case blit:
        blitOsc.step(out);
        break;

    case bpblit:
        bpBlitOsc.step(out);
        break;
    }
    envelope.step(envOut);

    // apply envelope to osc out
    for (uint8_t i=0; i < blockSize; i++) {
        out[i] *= envOut[i];
    }
}

void Voice_t::press(float f) {
    envelope.press();
    osc.set_freq(f);
    blitOsc.set_freq(f);
    bpBlitOsc.set_freq(f);
}

void Voice_t::release() {
    envelope.release();
}


#ifdef SYNTH_TEST_
extern "C" {
    void test_voice(const float a, const float d, const float s, const float r,\
                    const float f, const unsigned int gen,\
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
        EnvelopeSettings_t settings(44100);
        Generator_e generator = (Generator_e)gen;
        Voice_t voice(&settings, &generator);
        unsigned int pressCount = 0;
        unsigned int releaseCount = 0;
        settings.set_attack(a);
        settings.set_decay(d);
        settings.set_sustain(s);
        settings.set_release(r);
        for(unsigned int i=0; i+blockSize <= n; i+= blockSize) {
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
