/* MXCS Core Voice implementation
   copyright Maximilian Cornwell 2023
*/

#include <stdint.h>
#include "Voice.h"
#include "Constants.h"

VoiceConfig_t::VoiceConfig_t(float samplingFrequency): envConfig(samplingFrequency) {
}

void VoiceConfig_t::set_attack(float a) {
    envConfig.set_attack(a);
}

void VoiceConfig_t::set_decay(float d) {
    envConfig.set_decay(d);
}

void VoiceConfig_t::set_sustain(float s) {
    envConfig.set_sustain(s);
}

void VoiceConfig_t::set_release(float r) {
    envConfig.set_release(r);
}

void VoiceConfig_t::set_generator(Generator_e gen) {
    generator = gen;
}

Voice_t::Voice_t(){
}

Voice_t::Voice_t(VoiceConfig_t * _config): envelope(&(_config->envConfig)) {
    config = _config;
}

void Voice_t::set_config(VoiceConfig_t * _config) {
    config = _config;
    envelope.set_config(&(config->envConfig));
}


void Voice_t::step(float * out) {
    if (config == nullptr) {
        return;
    }
    float envOut[blockSize];
    switch (config->generator)
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
                    const unsigned int n, const float fs, float envOut[]) {
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
        Generator_e generator = (Generator_e)gen;
        VoiceConfig_t voice_config(fs);
        Voice_t voice(&voice_config);
        voice_config.set_generator(generator);
        voice_config.set_attack(a);
        voice_config.set_decay(d);
        voice_config.set_sustain(s);
        voice_config.set_release(r);
        unsigned int pressCount = 0;
        unsigned int releaseCount = 0;
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
