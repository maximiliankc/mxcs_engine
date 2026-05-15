/* MXCS Core Synthesizer implementation
   copyright Maximilian Cornwell 2023
*/
#include "Synth.h"

const float semitone = 1.0594630943592953;
const float c_minus_1 = 8.175798915643707;

Synth_t::Synth_t(float _samplingFrequency): mod(_samplingFrequency),
                                            lpFilter(_samplingFrequency),
                                            hpFilter(_samplingFrequency),
                                            voiceConfig(_samplingFrequency) {
    // calculate the frequency table
    samplingFrequency = _samplingFrequency;
    frequencyTable[0] = c_minus_1/samplingFrequency;
    for(uint8_t i = 1; i < notes; i++) {
        frequencyTable[i] = semitone*(frequencyTable[i-1]);
    }
    // initial filter configuration
    lpRes = -3;
    lpF = 20000;
    lpFilter.configure_lowpass(lpF, lpRes);
    hpRes = -3;
    hpF = 20;
    hpFilter.configure_highpass(hpF, hpRes);
}

void Synth_t::run_effects(float * out) {
    mod.step(out);
    lpFilter.step(out, out);
    hpFilter.step(out, out);
}

void Synth_t::set_attack(float a) {
    voiceConfig.set_attack(a);
}

void Synth_t::set_decay(float d) {
    voiceConfig.set_decay(d);
}

void Synth_t::set_sustain(float s) {
    voiceConfig.set_sustain(s);
}

void Synth_t::set_release(float r) {
    voiceConfig.set_release(r);
}

void Synth_t::set_mod_f(float freq) {
    mod.set_freq(freq);
}

void Synth_t::set_mod_depth(float depth) {
    mod.modRatio = depth;
}

void Synth_t::set_lpf_freq(float freq) {
    lpF = freq;
    lpFilter.configure_lowpass(lpF, lpRes);
}

void Synth_t::set_lpf_res(float res) {
    lpRes = res;
    lpFilter.configure_lowpass(lpF, lpRes);
}

void Synth_t::set_hpf_freq(float freq) {
    hpF = freq;
    hpFilter.configure_highpass(hpF, hpRes);
}

void Synth_t::set_hpf_res(float res){
    hpRes = res;
    hpFilter.configure_highpass(hpF, hpRes);
}

void Synth_t::set_generator(Generator_e gen) {
    voiceConfig.set_generator(gen);
}

MonoSynth_t::MonoSynth_t(float _sampling_frequency): Synth_t(_sampling_frequency),
                                                     voice(&voiceConfig) {
    currentNote = 0;
}

void MonoSynth_t::press(uint8_t note) {
    voice.set_frequency(frequencyTable[note]);
    voice.press();
    currentNote = note;
    enabledNotes[note] = true;
    // TODO add some protection against over-filling the stack
    noteStack[noteStackIndex++] = note; // add handling for filling stack
                                        // note stack points to lowest empty slot
}

void MonoSynth_t::release(uint8_t note) {
    enabledNotes[note] = false; // released note is no longer active
    if (note == currentNote) {
        // find the next frequency where a note is enabled
        bool searching = true;
        while(noteStackIndex > 0 && searching) {
            noteStackIndex--; // noteStack now points at highest note that (might) be active
            if (enabledNotes[noteStack[noteStackIndex]]) {
                float f = frequencyTable[noteStack[noteStackIndex]];
                voice.set_frequency(f);
                currentNote = noteStack[noteStackIndex++]; // point index back to lowest empty slow
                searching = false;
            } // otherwise, just keep searching
        }
        // noteStackIndex now points to 0 (searching true) or the active notes (searching false)
        if (searching) {
            // no active notes found, just release the current note
            voice.release();
        }
    }
}

void MonoSynth_t::step(float * out) {
    voice.step(out);
    run_effects(out);
}

PolySynth_t::PolySynth_t(float _sampling_frequency): Synth_t(_sampling_frequency) {
    for (uint8_t i = 0; i < notes; i++) {
        voices[i].set_config(&voiceConfig);
        voices[i].set_frequency(frequencyTable[i]);
    }
}

void PolySynth_t::press(uint8_t note) {
    voices[note].press();
}

void PolySynth_t::release(uint8_t note) {
    voices[note].release();
}

void PolySynth_t::step(float * out){
    float voiceSamples[blockSize];
    // initialise out vector to all zeros
    for (uint8_t i = 0; i < blockSize; i++) {
        out[i] = 0;
    }
    for (uint8_t i = 0; i < blockSize; i++) {
        if (voices[i].is_active()) {
            voices[i].step(voiceSamples);
            for (uint8_t j = 0; j < blockSize; j++) {
                out[j] += voiceSamples[j];
            }
        }
    }
    run_effects(out);
}

#ifdef SYNTH_TEST_

float * Synth_t::get_freq_table() {
    return frequencyTable;
}

extern "C" {
    void test_synth(const float a, const float d, const float s, const float r,\
                    const float modDepth, const float modFreq, const unsigned int gen,\
                    const float fs, const unsigned int synthType, \
                    const unsigned int presses, unsigned int pressNs[], uint8_t pressNotes[],\
                    const unsigned int releases, unsigned int releaseNs[], uint8_t releaseNotes[],\
                    const unsigned int n, float envOut[]) {
        // parameters:  a: attack time (in samples)
        //              d: decay time (in samples)
        //              s: sustain level (amplitude between 0 and 1)
        //              r: release time (in samples)
        //              modDepth: modulation depth
        //              modFreq: modulation frequency
        //              fs: sampling frequency
        //              synth_type: 0 (mono) or 1 (poly)
        //              gen: type of generator
        //              presses: number of presses
        //              pressNs: times at which to press
        //              pressNotes: MIDI notes to press at each time step
        //              releases: number of releases
        //              releaseNs: times at which to release
        //              releaseNotes: MIDI notes to release at each time step
        //              n: number of samples to iterate over.
        //                  if n is not a multiple of block_size, the last fraction of a block won't be filled in
        //              envOut: generated envelope
        Synth_t * synth_p;
        if (synthType == 0) {
            MonoSynth_t monoSynth(fs);
            synth_p = &monoSynth;
        } else {
            PolySynth_t polySynth(fs);
            synth_p = &polySynth;
        }
        unsigned int pressCount = 0;
        unsigned int releaseCount = 0;
        synth_p->set_attack(a);
        synth_p->set_decay(d);
        synth_p->set_sustain(s);
        synth_p->set_release(r);
        synth_p->set_mod_depth(modDepth);
        synth_p->set_mod_f(modFreq);
        synth_p->set_generator((Generator_e)gen);
        for(unsigned int i=0; i+blockSize <= n; i+= blockSize) {
            if(pressCount < presses && i >= pressNs[pressCount]) {
                synth_p->press(pressNotes[pressCount]);
                pressCount++;
            }
            if(releaseCount < releases && i >= releaseNs[releaseCount]) {
                synth_p->release(releaseNotes[releaseCount]);
                releaseCount++;
            }
            synth_p->step(envOut + i);
        }
    }

    void test_frequency_table(float freqs[], float fs) {
        // parameters:
        MonoSynth_t synth(fs);
        for(unsigned int i = 0; i<notes; i++) {
            freqs[i] = synth.get_freq_table()[i];
        }
}
}
#endif // MonoSynth_tEST_
