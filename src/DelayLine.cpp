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
    if (index == 0) {
        index = length-1;
    } else {
        index--;
    }
    memory[index] = value;
}

float DelayLine_t::access(uint32_t delay) {
    // TODO add error condition?: delay > length
    uint32_t wrapped_idx = (index + delay) % length; // there are probably more efficient ways of handling this
    return memory[wrapped_idx];
}
