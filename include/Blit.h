/* MXCS Core BLIT header
   copyright Maximilian Cornwell 2023
   */
#ifndef BLIT_H
#define BLIT_H

#include <stdint.h>

void msinc(float * out, float * lfSin, float * lfCos, float * hfSin, float * hfCos, int16_t M);
int16_t blit_m(float f);

#endif // BLIT_H_