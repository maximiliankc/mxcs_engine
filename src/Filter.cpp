/* MXCS Engine Filter implementation
   copyright Maximilian Cornwell 2024
*/
#include "Constants.h"
#include "Filter.h"
#include <math.h>

void IIR_Filter_t::set_coeffs(float * b_, float * a_) {
    b = b_;
    a = a_;
    for(uint32_t i = 0; i < order; i++) {
        b[i] = b[i]/a[0];
    }
    for(uint32_t i = 0; i < order; i++) {
        a[i] = a[i]/a[0];
    }
}

Filter_DFI_t::Filter_DFI_t():
    x_delay_line(nullptr, 0), y_delay_line(nullptr, 0) {
    order = 0;
}

Filter_DFI_t::Filter_DFI_t(float * memory_, float * b_, float * a_, uint32_t order_):
    x_delay_line(memory_, order_), y_delay_line(memory_ + order_, order_) {
    // memory length needs to be 2*order
    order = order_;
    set_coeffs(b_, a_);
}

void Filter_DFI_t::step(float * in, float * out) {
    for (uint32_t i = 0; i < blockSize; i++) {
        out[i] = b[0]*in[i];
        for (uint32_t j=0; j<order; j++) {
            out[i] += b[j+1]*x_delay_line.access(j);
            out[i] -= a[j+1]*y_delay_line.access(j); // *y_delay_line.access(j);
        }
        x_delay_line.insert(in[i]);
        y_delay_line.insert(out[i]);
    }
}

Filter_DFII_t::Filter_DFII_t():
    v_delay_line(nullptr, 0) {
    order = 0;
}

Filter_DFII_t::Filter_DFII_t(float * memory_, float * b_, float * a_, uint32_t order_):
    v_delay_line(memory_, order_) {
    order = order_;
    set_coeffs(b_, a_);
}

void Filter_DFII_t::step(float * in, float * out) {
    float v;
    float vn;
    float y;
    for (uint32_t i = 0; i < blockSize; i++) {
        v = in[i];
        y = 0;
        for (uint32_t j = 0; j < order; j++) {
            vn = v_delay_line.access(j);
            y += b[j+1]*vn;
            v -= a[j+1]*vn;
        }
        v_delay_line.insert(v);
        out[i] = y + b[0]*v;
    }
}

Filter_TDFI_t::Filter_TDFI_t() {
    order = 0;
}

Filter_TDFI_t::Filter_TDFI_t(float * memory_, float * b_, float * a_, uint32_t order_) {
    order = order_;
    set_coeffs(b_, a_);
    back_state = memory_;
    forward_state = memory_ + order;
    for (uint32_t i = 0; i < order; i++) {
        back_state[i] = 0;
        forward_state[i] = 0;
    }
}

void Filter_TDFI_t::step(float * in, float * out) {
    float v;
    for (uint32_t i = 0; i < blockSize; i++) {
        v = in[i] + back_state[0];
        out[i] = forward_state[0] + b[0]*v;
        for (uint32_t j = 0; j < order-1; j++) {
            back_state[j] = back_state[j+1] - a[j+1]*v;
            forward_state[j] = forward_state[j+1] + b[j+1]*v;
        }
        back_state[order-1] = -a[order]*v;
        forward_state[order-1] = b[order]*v;
    }
}

Filter_TDFII_t::Filter_TDFII_t(float * memory_, float * b_, float * a_, uint32_t order_) {
    order = order_;
    set_coeffs(b_, a_);
    state = memory_;
    for (uint32_t i = 0; i < order; i++){
        state[i] = 0;
    }
}

void Filter_TDFII_t::step(float * in, float * out) {
    for (uint32_t i = 0; i < blockSize; i++) {
        out[i] = b[0]*in[i] + state[0];
        for (uint32_t j = 0; j < order-1; j++) {
            state[j] = state[j+1] + b[j+1]*in[i] - a[j+1]*out[i];
        }
        state[order-1] = b[order]*in[i] - a[order]*out[i];
    }
}

Biquad_Filter_t::Biquad_Filter_t(float _samplingFrequency) {
    samplingFrequency = _samplingFrequency;
    float a_[3] = {1, 0, 0};
    float b_[3] = {1, 0, 0};
    set_coeffs(a_, b_);
    state[0] = 0;
    state[1] = 0;
}

Biquad_Filter_t::Biquad_Filter_t(float _samplingFrequency, float * b_, float * a_) {
    samplingFrequency = _samplingFrequency;
    set_coeffs(b_, a_);
    state[0] = 0;
    state[1] = 0;
}

void Biquad_Filter_t::step(float * in, float * out) {
    for (uint32_t i = 0; i < blockSize; i++) {
        out[i] = b[0]*in[i] + state[0];
        state[0] = state[1] + b[1]*in[i] - a[1]*out[i];
        state[1] = b[2]*in[i] - a[2]*out[i];
    }
}

void Biquad_Filter_t::set_coeffs(float * b_, float * a_) {
    for (unsigned int i = 0; i < 3; i++) {
        b[i] = b_[i]/a_[0];
        a[i] = a_[i]/a_[0];
    }
}

float res_2_q(float resonance) {
    return pow(10, resonance/20);
}

void Biquad_Filter_t::configure_lowpass(float f, float resonance) {
    float tau = tanf(f*M_PI/samplingFrequency);
    float b_[3];
    float a_[3];
    float q = res_2_q(resonance);

    // normalise by q?
    b_[0] = tau*tau;
    b_[1] = 2*tau*tau;
    b_[2] = tau*tau;
    a_[0] = 1 + (tau/q) + tau*tau;
    a_[1] = (2*tau*tau) - 2;
    a_[2] = 1 - (tau/q) + tau*tau;
    set_coeffs(b_, a_);
}

void Biquad_Filter_t::configure_highpass(float f, float resonance) {
    float tau = tanf(f*M_PI/samplingFrequency);
    float b_[3];
    float a_[3];
    float q = res_2_q(resonance);

    b_[0] = 1;
    b_[1] = -2;
    b_[2] = 1;
    a_[0] = 1 + (tau/q) + tau*tau;
    a_[1] = (2*tau*tau) - 2;
    a_[2] = 1 - (tau/q) + tau*tau;
    set_coeffs(b_, a_);
}

#ifdef SYNTH_TEST_

#define DFI 0
#define DFII 1
#define TDFI 2
#define TDFII 3
#define BIQUAD 4

extern "C" {
    void run_df1_filter(unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Filter_DFI_t filter(memory, b, a, order);
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

    void run_df2_filter(unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Filter_DFII_t filter(memory, b, a, order);
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

    void run_tdf1_filter(unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Filter_TDFI_t filter(memory, b, a, order);
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

    void run_tdf2_filter(unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Filter_TDFII_t filter(memory, b, a, order);
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

    void run_biquad_filter(float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Biquad_Filter_t filter(1, b, a); // sampling frequency irrelevant for this test
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

    void test_filter(unsigned int filterType, unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {

        switch (filterType)
        {
        case DFI:
            run_df1_filter(order, memory, b, a, ioLength, input, output);
            break;
        case DFII:
            run_df2_filter(order, memory, b, a, ioLength, input, output);
            break;
        case TDFI:
            run_tdf1_filter(order, memory, b, a, ioLength, input, output);
            break;
        case TDFII:
            run_tdf2_filter(order, memory, b, a, ioLength, input, output);
            break;
        case BIQUAD:
            run_biquad_filter(b, a, ioLength, input, output);
            break;
        default:
            // don't do anything! We want things to break in this situation
            break;
        }
    }

    void test_lowpass(float freq, float res, unsigned int ioLength, float * input, float * output, float fs) {
        Biquad_Filter_t filter(fs);
        filter.configure_lowpass(freq, res);
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

    void test_highpass(float freq, float res, unsigned int ioLength, float * input, float * output, float fs) {
        Biquad_Filter_t filter(fs);
        filter.configure_highpass(freq, res);
        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }

}
#endif // SYNTH_TEST_
