/* MXCS Core Envelope implementation
   copyright Maximilian Cornwell 2023
*/
#include <stdint.h>
#include "Envelope.h"
#include "Constants.h"
#include "Utils.h"

const float baseLevel = 0.00001;
const float baseLevelDB = 100;


EnvelopeSettings_t::EnvelopeSettings_t() {
    a = 0;
    d = 0;
    s = 0;
    r = 0;
    set_adsr();
}

void EnvelopeSettings_t::set_adsr() {
    aIncrement = db2mag(baseLevelDB/a);      // a is the number of samples per 100 dB
    dIncrement = db2mag(s/d);                  // d is a number of samples per 100 dB
    sMag = db2mag(s);                          // s is a level in dBFS
    rIncrement = db2mag(-(baseLevelDB+s)/r); // r is a number of samples
}

void EnvelopeSettings_t::set_attack(float attackTime) {
    a = attackTime*samplingFrequency;
    set_adsr();
}

void EnvelopeSettings_t::set_decay(float decayTime) {
    d = decayTime*samplingFrequency;
    set_adsr();
}

void EnvelopeSettings_t::set_sustain(float sustainLevel) {
    s = sustainLevel;
    set_adsr();
}

void EnvelopeSettings_t::set_release(float release) {
    r = release*samplingFrequency;
    set_adsr();
}

Envelope_t::Envelope_t(EnvelopeSettings_t * _settings) {
    run_state = &Envelope_t::run_off;
    amp = 0;
    settings = _settings;
}

void Envelope_t::step(float * envelope) {
    for(uint8_t i = 0; i < blockSize; i++) {
        (this->*run_state)();
        envelope[i] = amp;
    };
}

void Envelope_t::press() {
    if (amp < baseLevel) {
        amp = baseLevel; // -100 dB, and initial value
    }
    run_state = &Envelope_t::run_attack;
}

void Envelope_t::release() {
    run_state = &Envelope_t::run_release;
}

void Envelope_t::run_off() {
    amp = 0;
}

void Envelope_t::run_attack() {
    amp *= settings->aIncrement;
    if (amp >= 1.0) {
        amp = 1.0;
        run_state = &Envelope_t::run_decay;
    }
}

void Envelope_t::run_decay() {
    amp *= settings->dIncrement;
    if (amp <= settings->sMag) {
        amp = settings->sMag;
        run_state = &Envelope_t::run_sustain;
    }
}

void Envelope_t::run_sustain() {
    amp = settings->sMag;
}

void Envelope_t::run_release() {
    amp *= settings->rIncrement; // linear shift for now
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
        //              if n is not a multiple of block_size, the last fraction of a block won't be filled in
        //              envOut: generated envelope
        EnvelopeSettings_t adsr;
        Envelope_t env(&adsr);
        unsigned int pressCount = 0;
        unsigned int releaseCount = 0;
        adsr.set_attack(a);
        adsr.set_decay(d);
        adsr.set_sustain(s);
        adsr.set_release(r);
        for(unsigned int i=0; i+blockSize <= n; i+= blockSize) {
            if(pressCount < presses && i >= pressNs[pressCount]) {
                env.press();
                pressCount++;
            }
            if(releaseCount < releases && i >= releaseNs[releaseCount]) {
                env.release();
                releaseCount++;
            }
            env.step(envOut + i);
        }
    }
}
#endif // SYNTH_TEST_
