/* MXCS Engine Filter Header
   copyright Maximilian Cornwell 2024
*/
#ifndef DELAY_LINE_H_
#define DELAY_LINE_H_

#include <stdint.h>

// could make a template out of this, but implementing specifically for floats now
class DelayLine_t {
    float * memory;
    int32_t length;
    int32_t index;

    public:
    DelayLine_t(float * memory_, int32_t length);
    void insert(float);
    float access(uint32_t delay);
};

#endif // DELAY_LINE_H_
