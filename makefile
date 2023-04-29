IDIR = ./include
CC=gcc
CFLAGS=-I$(IDIR) -Werror -Wall

TEST_TARGET=test.so

_OBJ = Oscillator.o Envelope.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

_DEPS = Constants.h Oscillator.h Envelope.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

ODIR=obj
SRCDIR=src

all: $(TEST_TARGET)

$(TEST_TARGET): test/test.c $(OBJ)
	$(CC) -o $@ -shared -Wl,-install_name,$@ -fPIC $^ $(CFLAGS)

$(ODIR)/%.o: $(SRCDIR)/%.c $(DEPS)
	$(CC) -o $@ -c $< $(CFLAGS)

clean:
	rm $(TEST_TARGET) $(ODIR)/*.o

