#include "Synth.h"

void synth_init(Synth_t * self) {
    // TODO calculate frequency table
    voice_init(&(self->voice));
}

void synth_set_adsr(Synth_t * self, float a, float d, float s, float r) {
    env_set_adsr(&(self->voice.envelope), a, d, s, r);
}

void synth_press(Synth_t * self, uint8_t note) {
    float f = self->frequency_table[note];
    voice_press(&(self->voice), f);
}

void synth_release(Synth_t * self) {
    voice_release(&(self->voice));
}
void synth_step(Synth_t * self, float * out) {
    voice_step(&(self->voice), out);
}