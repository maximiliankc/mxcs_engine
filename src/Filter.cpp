/* MXCS Engine Filter implementation
   copyright Maximilian Cornwell 2024
*/
#include "Constants.h"
#include "Filter.h"

void Filter_t::set_coeffs(float * b_, float * a_) {
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
    for (uint8_t i = 0; i < blockSize; i++) {
        out[i] = b[0]*in[i];
        for (uint32_t j=0; j<order; j++) {
            out[i] += b[j+1]*x_delay_line.access(j);
            out[i] -= a[j+1]*y_delay_line.access(j);
        }
        x_delay_line.insert(in[i]);
        y_delay_line.insert(out[i]);
    }
}

#ifdef SYNTH_TEST_
extern "C" {
    void test_filter(unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Filter_DFI_t filter(memory, b, a, order);

        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter.step(&input[i], &output[i]);
        }
    }
}
#endif // SYNTH_TEST_
