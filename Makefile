CXX = g++

MODE ?= Release

CXXFLAGS_MAIN_RELEASE = -std=c++11 -Wall \
    -Wno-unused-const-variable \
    -Wno-strict-aliasing \
    -Wno-maybe-uninitialized \
    -Wno-unused-variable \
    -Ivendor/gflags \
    -I. \
    -O3 -DNDEBUG -fPIC -Wno-literal-suffix

CXXFLAGS_MAIN_DEBUG = -std=c++11 -Wall \
    -Wno-unused-const-variable \
    -Wno-tautological-constant-out-of-range-compare \
    -Ivendor/gflags \
    -I. \
    -O1 -g -fsanitize=address -fPIC -Wno-literal-suffix

CXXFLAGS_GFLAGS = -std=c++03 -Wall -fPIC \
    -Ivendor/gflags

ifeq ($(MODE), Debug)
    CXXFLAGS_MAIN = $(CXXFLAGS_MAIN_DEBUG)
    LDFLAGS = -O1 -fsanitize=address -fno-omit-frame-pointer -lpthread
else
    CXXFLAGS_MAIN = $(CXXFLAGS_MAIN_RELEASE)
    LDFLAGS = -O3 -lpthread
endif

PYBIND11_INCLUDE = $(shell python3 -m pybind11 --includes)

TRAX_SRC = trax.cc
TRAX_OBJ = trax.o

GFLAGS_SRC = vendor/gflags/gflags.cc
GFLAGS_OBJ = gflags.o
GFLAGS_COMPLETIONS_SRC = vendor/gflags/gflags_completions.cc
GFLAGS_COMPLETIONS_OBJ = gflags_completions.o
GFLAGS_REPORTING_SRC = vendor/gflags/gflags_reporting.cc
GFLAGS_REPORTING_OBJ = gflags_reporting.o

BINDINGS_SRC = bindings/bindings.cpp
BINDINGS_SO = trax_bindings.so

all: $(BINDINGS_SO)

$(TRAX_OBJ): $(TRAX_SRC) trax.h
	$(CXX) $(CXXFLAGS_MAIN) -c $< -o $@

$(GFLAGS_OBJ): $(GFLAGS_SRC)
	$(CXX) $(CXXFLAGS_GFLAGS) -c $< -o $@

$(GFLAGS_COMPLETIONS_OBJ): $(GFLAGS_COMPLETIONS_SRC)
	$(CXX) $(CXXFLAGS_GFLAGS) -c $< -o $@

$(GFLAGS_REPORTING_OBJ): $(GFLAGS_REPORTING_SRC)
	$(CXX) $(CXXFLAGS_GFLAGS) -c $< -o $@

$(BINDINGS_SO): $(BINDINGS_SRC) $(TRAX_OBJ) $(GFLAGS_OBJ) $(GFLAGS_COMPLETIONS_OBJ) $(GFLAGS_REPORTING_OBJ)
	$(CXX) $(CXXFLAGS_MAIN) $(PYBIND11_INCLUDE) -shared $^ -o $@ $(LDFLAGS)

clean:
	rm -f *.o $(BINDINGS_SO) vendor/gflags/*.o

.PHONY: all clean
