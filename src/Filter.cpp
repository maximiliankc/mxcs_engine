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

#ifdef SYNTH_TEST_

#define DFI 0
#define DFII 1
#define TDFI 2
#define TDFII 3

extern "C" {
    void test_filter(unsigned int filterType, unsigned int order, float * memory, float * b, float * a, unsigned int ioLength, float * input, float * output) {
        Filter_DFI_t filter_df1(memory, b, a, order);
        Filter_DFII_t filter_df2(memory, b, a, order);
        // Filter_TDFI_t filter_tdf1(memory, b, a, order);
        // Filter_TDFII_t filter_tdf2(memory, b, a, order);

        Filter_t * filter;

        switch (filterType)
        {
        case DFI:
            filter = &filter_df1;
            break;
        case DFII:
            filter = &filter_df2;
            break;
        // case TDFI:
        //     filter = &filter_tdf1;
        //     break;
        // case TDFII:
        //     filter = &filter_df2;
        //     break;
        default:
            // don't do anything! We want things to break in this situation
            break;
        }

        for(unsigned int i=0; i+blockSize <= ioLength; i+= blockSize) {
            filter->step(&input[i], &output[i]);
        }
    }
}
#endif // SYNTH_TEST_
