/* MXCS Engine Filter Header
   copyright Maximilian Cornwell 2024
*/
#ifndef DELAY_LINE_H_
#define DELAY_LINE_H_

#include <stdint.h>

// could make a template out of this, but implementing specifically for floats now
class DelayLine_t {
    float * memory;
    uint32_t length;
    uint32_t index;

    public:
    DelayLine_t(float * memory_, int32_t length);
    void insert(float);
    float access(uint32_t delay);
};

#endif // DELAY_LINE_H_
