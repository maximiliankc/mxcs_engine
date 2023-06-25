#include <math.h>
#define LOG10 (2.302585092994046)

float db2mag(float x) {
    return expf(LOG10*x/(20));
}

#ifdef SYNTH_TEST_
void test_db2mag(const unsigned int n, float inOut[]) {
    // parameters: inOut: input/output array
    //             n: number of values in input/output array
    for(unsigned int i = 0; i<n; i++) {
        inOut[i] = db2mag(inOut[i]);
    }
}
#endif // TEST