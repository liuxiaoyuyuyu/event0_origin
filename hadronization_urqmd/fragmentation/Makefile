EXE=main_string_fragmentation
GCC=g++

PYTHIAINC=${shell /wsu/home/he/he92/he9215/soft_ware/Pythia8_package/pythia8310_install/bin/pythia8-config --includedir}
PYTHIALIBS=${shell /wsu/home/he/he92/he9215/soft_ware/Pythia8_package/pythia8310_install/bin/pythia8-config --libdir}




all: $(EXE)

main_string_fragmentation.o: main_string_fragmentation.cc
	$(GCC) -I$(PYTHIAINC) -c main_string_fragmentation.cc

$(EXE): main_string_fragmentation.o
	$(GCC) -O3 -I$(PYTHIAINC) -o $(EXE) main_string_fragmentation.o $(PYTHIALIBS)/libpythia8.a -ldl 

.PHONY:clean
clean:
	-rm *.o $(EXE)
