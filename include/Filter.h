/* MXCS Engine Filter Header
   copyright Maximilian Cornwell 2024
*/
#ifndef FILTER_H_
#define FILTER_H_

#include <stdint.h>
#include "DelayLine.h"

class IIR_Filter_t {
    protected:
    float * a;
    float * b;
    uint32_t order;

    public:
    void set_coeffs(float * b, float * a);
    void configure_lp(float frequency, float depth);
    virtual void step(float * in, float * out) = 0;
};

class Filter_DFI_t: public IIR_Filter_t {
    DelayLine_t x_delay_line;
    DelayLine_t y_delay_line;
    public:
    Filter_DFI_t();
    Filter_DFI_t(float * memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Filter_DFII_t: public IIR_Filter_t {
    DelayLine_t v_delay_line;
    public:
    Filter_DFII_t();
    Filter_DFII_t(float * memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Filter_TDFI_t: public IIR_Filter_t {
    float * back_state;
    float * forward_state;
    public:
    Filter_TDFI_t();
    Filter_TDFI_t(float * memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Filter_TDFII_t: public IIR_Filter_t {
    float * state;
    public:
    Filter_TDFII_t();
    Filter_TDFII_t(float * memory, float * b, float * a, uint32_t order);
    void step(float * in, float * out);
};

class Biquad_Filter_t: public IIR_Filter_t {
    float state[2];
    float a[3];
    float b[3];
    public:
    Biquad_Filter_t();
    Biquad_Filter_t(float * b, float * a);
    void step(float * in, float * out);
    void set_coeffs(float * b, float * a);
    void configure_lowpass(float f, float res);
    void configure_highpass(float f, float res);
};

#endif // FILTER_H_
