/* MXCS Core Synthesizer implementation
   copyright Maximilian Cornwell 2023
*/
#include "Synth.h"


const float semitone = 1.0594630943592953;
const float c_minus_1 = 8.175798915643707/samplingFrequency;

Synth_t::Synth_t(): voice(&settings, &generator) {
    // calculate the frequency table
    currentNote = 0;
    frequencyTable[0] = c_minus_1;
    for(uint8_t i = 1; i < notes; i++) {
        frequencyTable[i] = semitone*(frequencyTable[i-1]);
    }
    // configure oscillator type
    generator = sine;
}

void Synth_t::set_attack(float a) {
    settings.set_attack(a);
}

void Synth_t::set_decay(float d) {
    settings.set_decay(d);
}

void Synth_t::set_sustain(float s) {
    settings.set_sustain(s);
}

void Synth_t::set_release(float r) {
    settings.set_release(r);
}

void Synth_t::set_mod_f(float freq) {
    mod.lfo.set_freq(freq/samplingFrequency);
}

void Synth_t::set_mod_depth(float depth) {
    mod.modRatio = depth;
}

void Synth_t::set_generator(Generator_e gen) {
    generator = gen;
}

void Synth_t::press(uint8_t note) {
    float f = frequencyTable[note];
    voice.press(f);
    currentNote = note;
}

void Synth_t::release(uint8_t note) {
    if (note==currentNote) {
        voice.release();
    }
}

void Synth_t::step(float * out) {
    voice.step(out);
    mod.step(out);
}


#ifdef SYNTH_TEST_

float * Synth_t::get_freq_table() {
    return frequencyTable;
}

extern "C" {
    void test_synth(const float a, const float d, const float s, const float r,\
                    const float modDepth, const float modFreq, const unsigned int gen,\
                    const unsigned int presses, unsigned int pressNs[], uint8_t pressNotes[],\
                    const unsigned int releases, unsigned int releaseNs[], uint8_t releaseNotes[],\
                    const unsigned int n, float envOut[]) {
        // parameters:  a: attack time (in samples)
        //              d: decay time (in samples)
        //              s: sustain level (amplitude between 0 and 1)
        //              r: release time (in samples)
        //              modDepth: modulation depth
        //              modFreq: modulation frequency
        //              presses: number of presses
        //              pressNs: times at which to press
        //              notes: MIDI notes to press at each time step
        //              releases: number of releases
        //              releaseNs: times at which to release
        //              n: number of samples to iterate over.
        //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
        //              envOut: generated envelope
        Synth_t synth;
        unsigned int pressCount = 0;
        unsigned int releaseCount = 0;
        synth.set_attack(a);
        synth.set_decay(d);
        synth.set_sustain(s);
        synth.set_release(r);
        synth.set_mod_depth(modDepth);
        synth.set_mod_f(modFreq);
        synth.set_generator((Generator_e)gen);
        for(unsigned int i=0; i+blockSize <= n; i+= blockSize) {
            if(pressCount < presses && i >= pressNs[pressCount]) {
                synth.press(pressNotes[pressCount]);
                pressCount++;
            }
            if(releaseCount < releases && i >= releaseNs[releaseCount]) {
                synth.release(releaseNotes[releaseCount]);
                releaseCount++;
            }
            synth.step(envOut + i);
        }
    }

    void test_frequency_table(float freqs[]) {
        // parameters:
        Synth_t synth;
        for(unsigned int i = 0; i<notes; i++) {
            freqs[i] = synth.get_freq_table()[i];
        }
}
}
#endif // SYNTH_TEST_
