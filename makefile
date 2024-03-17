IDIR = ./include
CC=g++
CFLAGS=-I$(IDIR) -Werror -Wall -Wpedantic -DSYNTH_TEST_

TEST_TARGET=test.so

_OBJ = Blit.o DelayLine.o Envelope.o Modulator.o Oscillator.o Synth.o Voice.o Utils.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

_DEPS = Blit.h Constants.h DelayLine.h Envelope.h Modulator.h Oscillator.h Synth.h Voice.h Utils.h
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
