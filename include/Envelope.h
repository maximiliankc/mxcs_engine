#ifndef ENVELOPE_H_
#define ENVELOPE_H_

enum EnvelopeState_t {off = 0, attack = 1, decay = 2, sustain = 3, release = 4};

typedef struct Envelope_t {
    EnvelopeState_t state;
    float amp;
} Envelope_t;

void init_envelope(Envelope_t self);
void run_envelope(Envelope_t self, float * envelope);
void press_envelope(Envelope_t self);
void release_envelope(Envelope_t self);


#endif // ENVELOPE_H_