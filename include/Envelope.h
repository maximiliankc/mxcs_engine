/* MXCS Core Envelope header
   copyright Maximilian Cornwell 2023
*/
#ifndef ENVELOPE_H_
#define ENVELOPE_H_

enum EnvelopeState_t {
    off = 0,
    attack = 1,
    decay = 2,
    sustain = 3,
    release = 4};

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

typedef struct Envelope_t {
    EnvelopeState_t state;
    EnvelopeSettings_t * settings;
    float amp;
} Envelope_t;


void env_init(Envelope_t * self, EnvelopeSettings_t * settings);
void env_step(Envelope_t * self, float * envelope);
void env_press(Envelope_t * self);
void env_release(Envelope_t * self);



#endif // ENVELOPE_H_
