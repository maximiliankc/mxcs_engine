/* MXCS Core Envelope header
   copyright Maximilian Cornwell 2023
*/
#ifndef ENVELOPE_H_
#define ENVELOPE_H_

class Envelope_t {
    float samplingFrequency;
    float a;
    float d;
    float s;
    float r;
    float aIncrement;
    float dIncrement;
    float sMag;
    float rIncrement;
    float amp;

    void set_adsr();

    void run_off();
    void run_attack();
    void run_decay();
    void run_sustain();
    void run_release();

    public:
    Envelope_t(float samplingFrequency);

    void set_attack(float a);
    void set_decay(float d);
    void set_sustain(float s);
    void set_release(float r);
    void (Envelope_t::*run_state)(void);

    public:
    void step(float * envelope);
    void press();
    void release();
};

#endif // ENVELOPE_H_
