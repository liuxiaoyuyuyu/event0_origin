GCC=g++


PYTHIAINC=${shell /wsu/home/he/he92/he9215/XETSCAPE/code_running/software_code/pythia8306_installed/bin/pythia8-config --includedir}
PYTHIALIBS=${shell /wsu/home/he/he92/he9215/XETSCAPE/code_running/software_code/pythia8306_installed/bin/pythia8-config --libdir}

FASTJETINC=${shell /wsu/home/he/he92/he9215/XETSCAPE/code_running/software_code/fastjet/fastjet_install/bin/fastjet-config --cxxflags}
FASTJETLIBS=${shell /wsu/home/he/he92/he9215/XETSCAPE/code_running/software_code/fastjet/fastjet_install/bin/fastjet-config --libs}




EXE=fastjet_hadron
all: $(EXE)

fastjet_hadron.o: fastjet_hadron.cc
	$(GCC) -I$(PYTHIAINC) $(ROOTINC) $(FASTJETINC) -c fastjet_hadron.cc

$(EXE): fastjet_hadron.o
	$(GCC) -O3 -I$(PYTHIAINC) $(ROOTINC) $(FASTJETINC) -o $(EXE) fastjet_hadron.o $(PYTHIALIBS)/libpythia8.a $(ROOTLIBS) $(FASTJETLIBS) 

.PHONY:clean
clean:
	-rm *.o $(EXE)	
