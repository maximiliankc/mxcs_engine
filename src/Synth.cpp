/* MXCS Core Synthesizer implementation
   copyright Maximilian Cornwell 2023
*/
#include "Synth.h"

#define SEMITONE (1.0594630943592953)
#define C_MINUS_1 (8.175798915643707/SAMPLING_FREQUENCY)

void synth_init(Synth_t * self) {
    // calculate the frequency table
    self->currentNote = 0;
    self->frequencyTable[0] = C_MINUS_1;
    for(uint8_t i = 1; i < NOTES; i++) {
        self->frequencyTable[i] = SEMITONE*(self->frequencyTable[i-1]);
    }
    voice_init(&(self->voice), &(self->settings));
    env_settings_init(&(self->settings));
    mod_init(&(self->mod));
}

void synth_set_attack(Synth_t * self, float a) {
    env_set_attack(&(self->settings), a);
}

void synth_set_decay(Synth_t * self, float d) {
    env_set_decay(&(self->settings), d);
}

void synth_set_sustain(Synth_t * self, float s) {
    env_set_sustain(&(self->settings), s);
}

void synth_set_release(Synth_t * self, float r) {
    env_set_release(&(self->settings), r);
}

void synth_set_mod_f(Synth_t * self, float freq) {
    osc_setF(&(self->mod.lfo), freq/SAMPLING_FREQUENCY);
}

void synth_set_mod_depth(Synth_t * self, float depth) {
    self->mod.modRatio = depth;
}

void synth_press(Synth_t * self, uint8_t note) {
    float f = self->frequencyTable[note];
    voice_press(&(self->voice), f);
    self->currentNote = note;
}

void synth_release(Synth_t * self, uint8_t note) {
    if (note==self->currentNote) {
        voice_release(&(self->voice));
    }
}

void synth_step(Synth_t * self, float * out) {
    voice_step(&(self->voice), out);
    mod_step(&(self->mod), out);
}

#ifdef SYNTH_TEST_
extern "C" {
    void test_synth(const float a, const float d, const float s, const float r,\
                    const float modDepth, const float modFreq,\
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
        synth_init(&synth);
        synth_set_attack(&synth, a);
        synth_set_decay(&synth, d);
        synth_set_sustain(&synth, s);
        synth_set_release(&synth, r);
        synth_set_mod_depth(&synth, modDepth);
        synth_set_mod_f(&synth, modFreq);
        for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
            if(pressCount < presses && i >= pressNs[pressCount]) {
                synth_press(&synth, pressNotes[pressCount]);
                pressCount++;
            }
            if(releaseCount < releases && i >= releaseNs[releaseCount]) {
                synth_release(&synth, releaseNotes[releaseCount]);
                releaseCount++;
            }
            synth_step(&synth, envOut + i);
        }
    }

    void test_frequency_table(float freqs[]) {
        // parameters:
        Synth_t synth;
        synth_init(&synth);
        for(unsigned int i = 0; i<NOTES; i++) {
            freqs[i] = synth.frequencyTable[i];
        }
}
}
#endif // SYNTH_TEST_