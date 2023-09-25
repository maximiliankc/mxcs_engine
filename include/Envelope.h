/* MXCS Core Envelope header
   copyright Maximilian Cornwell 2023
*/
#ifndef ENVELOPE_H_
#define ENVELOPE_H_

class EnvelopeSettings_t {
    public:
    float a;
    float d;
    float s;
    float r;
    float aIncrement;
    float dIncrement;
    float sMag;
    float rIncrement;

    EnvelopeSettings_t();
    void set_attack(float a);
    void set_decay(float d);
    void set_sustain(float s);
    void set_release(float r);

    private:
    void set_adsr();
};

class Envelope_t {
    void (Envelope_t::*run_state)(void);
    EnvelopeSettings_t * settings;
    float amp;

    void run_off();
    void run_attack();
    void run_decay();
    void run_sustain();
    void run_release();

    public:
    Envelope_t(EnvelopeSettings_t * _settings);
    void step(float * envelope);
    void press();
    void release();
};

#endif // ENVELOPE_H_
