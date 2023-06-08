#ifndef ENVELOPE_H_
#define ENVELOPE_H_
#define LOG10 (2.302585092994046)

typedef enum EnvelopeState_t {
    off = 0,
    attack = 1,
    decay = 2,
    sustain = 3,
    release = 4} EnvelopeState_t;

typedef struct Envelope_t {
    EnvelopeState_t state;
    float amp;
    float a_increment;
    float d_increment;
    float s_level;
    float r_increment;
} Envelope_t;


void env_init(Envelope_t * self, float a, float d, float s, float r);
void env_step(Envelope_t * self, float * envelope);
void env_press(Envelope_t * self);
void env_release(Envelope_t * self);
void env_set_adsr(Envelope_t * self, float a, float d, float s, float r);


#endif // ENVELOPE_H_
