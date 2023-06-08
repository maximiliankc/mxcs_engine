#include <math.h>
#define LOG10 (2.302585092994046)

float db2mag(float x) {
    return expf(LOG10*x/(20));
}