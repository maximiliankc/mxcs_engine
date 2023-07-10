/* MXCS synthesizer core BLIT implementation
   copyright Maximilian Cornwell 2023
*/
#include "Blit.h"

#include "Constants.h"

#define THRESHOLD (0.0000000000001f) // TODO figure out the best threshold

void msinc(float * out, float * lfSin, float * lfCos, float * hfSin, float * hfCos, int16_t M) {
    for(uint8_t i = 0; i<BLOCK_SIZE; i++) {
        if (lfSin[i] > THRESHOLD || lfSin[i] < -THRESHOLD) {
            out[i] = hfSin[i]/(M*lfSin[i]);
        } else {
            out[i] = hfCos[i]/lfCos[i];
        }
    }
}

int16_t blit_m(float f) {
    int16_t period = (int16_t)(0.5f/f);
    period = 2*period + 1;
}
