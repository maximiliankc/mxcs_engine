IDIR = ./include
CC=g++
CFLAGS=-I$(IDIR) -Werror -Wall -Wpedantic -DSYNTH_TEST_

TEST_TARGET=test.so

_OBJ = Blit.o DelayLine.o Envelope.o Filter.o Modulator.o Oscillator.o OscillatorLut.o Synth.o Utils.o Voice.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

_DEPS = Blit.h Constants.h DelayLine.h Envelope.h Filter.h Modulator.h Oscillator.h OscillatorLut.h SineTable.h Synth.h Utils.h Voice.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

ODIR=obj
SRCDIR=src

all: $(TEST_TARGET)

$(TEST_TARGET): $(OBJ)
	$(CC) -o $@ -shared -Wl,-install_name,$@ -fPIC $^ $(CFLAGS)

$(ODIR)/%.o: $(SRCDIR)/%.cpp $(DEPS)
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	rm $(TEST_TARGET) $(ODIR)/*.o
