#include "Synth.h"

#define SEMITONE (1.0594630943592953)
#define C_MINUS_1 (0.00017032914407591056) // for fs = 48000

void synth_init(Synth_t * self) {
    // TODO calculate frequency table
    self->frequencyTable[0] = C_MINUS_1;
    for(uint8_t i = 1; i < NOTES; i++) {
        self->frequencyTable[i] = SEMITONE*(self->frequencyTable[i-1]);
    }
    voice_init(&(self->voice));
}

void synth_set_adsr(Synth_t * self, float a, float d, float s, float r) {
    env_set_adsr(&(self->voice.envelope), a, d, s, r);
}

void synth_press(Synth_t * self, uint8_t note) {
    float f = self->frequencyTable[note];
    voice_press(&(self->voice), f);
}

void synth_release(Synth_t * self) {
    voice_release(&(self->voice));
}

void synth_step(Synth_t * self, float * out) {
    voice_step(&(self->voice), out);
}

#ifdef SYNTH_TEST_
void test_synth(const float a, const float d, const float s, const float r,\
                   const unsigned int presses, unsigned int pressNs[], uint8_t notes[],\
                   const unsigned int releases, unsigned int releaseNs[],\
                   const unsigned int n, float envOut[]) {
    // parameters:  a: attack time (in samples)
    //              d: decay time (in samples)
    //              s: sustain level (amplitude between 0 and 1)
    //              r: release time (in samples)
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
    synth_set_adsr(&synth, a, d, s, r);
    for(unsigned int i=0; i+BLOCK_SIZE <= n; i+= BLOCK_SIZE) {
        if(pressCount < presses && i >= pressNs[pressCount]) {
            synth_press(&synth, notes[pressCount]);
            pressCount++;
        }
        if(releaseCount < releases && i >= releaseNs[releaseCount]) {
            synth_release(&synth);
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

#endif // SYNTH_TEST_