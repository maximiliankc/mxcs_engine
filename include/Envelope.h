/* MXCS Core Envelope header
   copyright Maximilian Cornwell 2023
*/
#ifndef ENVELOPE_H_
#define ENVELOPE_H_

typedef enum EnvelopeState_t {
    off = 0,
    attack = 1,
    decay = 2,
    sustain = 3,
    release = 4} EnvelopeState_t;

typedef struct EnvelopeSettings_t {
    float a;
    float d;
    float s;
    float r;
    float a_increment;
    float d_increment;
    float s_level;
    float r_increment;
} EnvelopeSettings_t;

typedef struct Envelope_t {
    EnvelopeState_t state;
    EnvelopeSettings_t * settings;
    float amp;
} Envelope_t;


void env_init(Envelope_t * self, EnvelopeSettings_t * settings);
void env_step(Envelope_t * self, float * envelope);
void env_press(Envelope_t * self);
void env_release(Envelope_t * self);
void env_settings_init(EnvelopeSettings_t * self);
void env_set_attack(EnvelopeSettings_t * self, float a);
void env_set_decay(EnvelopeSettings_t * self, float d);
void env_set_sustain(EnvelopeSettings_t * self, float s);
void env_set_release(EnvelopeSettings_t * self, float r);


#endif // ENVELOPE_H_
