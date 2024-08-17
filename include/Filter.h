/* MXCS Engine Filter Header
   copyright Maximilian Cornwell 2024
*/
#ifndef FILTER_H_
#define FILTER_H_

#include <stdint.h>
#include "DelayLine.h"

class Filter_t {
    protected:
    float * a;
    float * b;
    uint32_t order;

    public:
    void set_coeffs(float * b, float * a);
    virtual void step(float * in, float * out) = 0;
};

class Filter_DFI_t: public Filter_t {
    DelayLine_t x_delay_line;
    DelayLine_t y_delay_line;
    public:
    Filter_DFI_t();
    Filter_DFI_t(float * Memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Filter_DFII_t: public Filter_t {
    DelayLine_t v_delay_line;
    public:
    Filter_DFII_t();
    Filter_DFII_t(float * Memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Filter_TDFI_t: public Filter_t {
    float * back_state;
    float * forwared_state;
    Filter_TDFI_t();
    Filter_TDFI_t(float * Memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Filter_TDFII_t: public Filter_t {
    float * state;
    Filter_TDFII_t();
    Filter_TDFII_t(float * Memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

#endif // FILTER_H_
