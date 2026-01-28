GCC=g++

PYTHIAINC=${shell /afs/cern.ch/user/x/xiaoyul/pythia8310_install/bin/pythia8-config --includedir}
PYTHIALIBS=${shell /afs/cern.ch/user/x/xiaoyul/pythia8310_install/bin/pythia8-config --libdir}

FASTJETINC=${shell /afs/cern.ch/user/x/xiaoyul/fastjet-install/bin/fastjet-config --cxxflags}
FASTJETLIBS=${shell /afs/cern.ch/user/x/xiaoyul/fastjet-install/bin/fastjet-config --libs}

ROOTCFLAGS   := $(shell root-config --cflags)
ROOTLIBS     := $(shell root-config --libs)

EXE=fastjet_hadron
all: $(EXE)

fastjet_hadron.o: fastjet_hadron.cc
	$(GCC) -I$(PYTHIAINC) $(FASTJETINC) $(ROOTCFLAGS) -c fastjet_hadron.cc

$(EXE): fastjet_hadron.o
	$(GCC) -O3 -I$(PYTHIAINC) $(FASTJETINC) $(ROOTCFLAGS) -o $(EXE) fastjet_hadron.o $(PYTHIALIBS)/libpythia8.a $(ROOTLIBS) -ldl $(FASTJETLIBS) -lRecursiveTools

.PHONY:clean
clean:
	-rm *.o $(EXE)	
