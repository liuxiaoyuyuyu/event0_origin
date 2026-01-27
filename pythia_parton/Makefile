EXE=mymain06
GCC=g++

PYTHIAINC=${shell /afs/cern.ch/user/x/xiaoyul/pythia8310_install/bin/pythia8-config --includedir}
PYTHIALIBS=${shell /afs/cern.ch/user/x/xiaoyul/pythia8310_install/bin/pythia8-config --libdir}

FASTJETINC=${shell /afs/cern.ch/user/x/xiaoyul/fastjet-install/bin/fastjet-config --cxxflags}
FASTJETLIBS=${shell /afs/cern.ch/user/x/xiaoyul/fastjet-install/bin/fastjet-config --libs}

all: $(EXE)

mymain06.o: mymain06.cc
	$(GCC) -I$(PYTHIAINC) $(FASTJETINC) -c mymain06.cc

$(EXE): mymain06.o
	$(GCC) -O3 -I$(PYTHIAINC) $(FASTJETINC) -o $(EXE) mymain06.o $(PYTHIALIBS)/libpythia8.a -ldl $(FASTJETLIBS)

.PHONY:clean
clean:
	-rm *.o $(EXE)
