/* MXCS Core Utility implementation
   copyright Maximilian Cornwell 2023
*/
#include <math.h>

const float c_log10 = 2.302585092994046;


float db2mag(float x) {
    return expf(c_log10*x/20);
}


#ifdef SYNTH_TEST_
extern "C" {
    void test_db2mag(const unsigned int n, float inOut[]) {
        // parameters: inOut: input/output array
        //             n: number of values in input/output array
        for(unsigned int i = 0; i<n; i++) {
            inOut[i] = db2mag(inOut[i]);
        }
    }
}
#endif // SYNTH_TEST_
