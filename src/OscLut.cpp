#include "OscLut.h"
#include "SineTable.h"
#include "Constants.h"
#include "math.h"

OscillatorLut_t::OscillatorLut_t() {
    phase = 0;
}

void OscillatorLut_t::set_freq(float f) {
    frequency = f/samplingFrequency;
}

float OscillatorLut_t::get_phase() {
    return 2*M_PI*phase;
}

void OscillatorLut_t::adjust_phase(float phase_) {
    phase = phase_/(2*M_PI);
}

void OscillatorLut_t::step(float * out) {
    uint16_t phase_index;
    for (uint16_t i = 0; i < blockSize; i++) {
        phase_index = (uint16_t)(phase*((float)table_length));
        out[i] = sine_table[phase_index];
        // update phase
        phase += frequency;
        if (phase > 1.0) {
            phase -= 1.0;
        }
    }
}
