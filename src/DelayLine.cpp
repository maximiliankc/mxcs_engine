/* MXCS Engine Delay Line implementation
   copyright Maximilian Cornwell 2024
*/

#include "DelayLine.h"

DelayLine_t::DelayLine_t(float * memory_, int32_t length_) {
    memory = memory_;
    length = length_;
    for (uint32_t i = 0; i < length; i++) {
        memory[i] = 0;
    }
}

void DelayLine_t::insert(float value) {
    index--;
    if (index < 0) {
        index = length - 1;
    }
    memory[index] = value;
}

float DelayLine_t::access(uint32_t delay) {
    // TODO add error condition?: delay > length
    uint32_t wrapped_idx = (index + delay) % length; // there are probably more efficient ways of handling this
    return memory[wrapped_idx];
}

#ifdef SYNTH_TEST_
extern "C" {
    void test_delay_line(float * in, float * out, uint32_t * delays,\
                         unsigned int ioLen, float * lineMemory, unsigned int lineLength) {
        // params: in: array of input values
        //         out: array of output values
        //         delays: amount of delay to use at each time step
        //         ioLen: length of input/output/delay arrays
        //         lineMemory: memory to initialise delay line with
        //         lineLength: the length of the delay line (should be no more than the memory provided)
        DelayLine_t delayLine(lineMemory, lineLength);
        for (unsigned int i = 0; i < ioLen; i++) {
            delayLine.insert(in[i]);
            out[i] = delayLine.access(delays[i]);
        }
    }
}
#endif
