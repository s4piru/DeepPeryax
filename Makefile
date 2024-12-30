CXX = g++

# Release
CXXFLAGS = -std=c++11 -Wall -Wno-unused-const-variable -Wno-strict-aliasing -Wno-maybe-uninitialized -Wno-unused-variable -Wno-unknown-warning-option -Ivendor/gflags -O3 -DNDEBUG
LDFLAGS = -O3 -lpthread

# Debug
# CXXFLAGS = -std=c++11 -Wall -Wno-unused-const-variable -Wno-tautological-constant-out-of-range-compare -Ivendor/gflags -O1 -g -fsanitize=address #-pg -DNDEBUG
# LDFLAGS = -O1 -fsanitize=address -fno-omit-frame-pointer -lpthread #-pg -DNDEBUG

trax.o: trax.cc trax.h

gflags.o: vendor/gflags/gflags.cc
	$(CXX) -std=c++03 -c $^ -o $@

gflags_completions.o: vendor/gflags/gflags_completions.cc
	$(CXX) -std=c++03 -c $^ -o $@

gflags_reporting.o: vendor/gflags/gflags_reporting.cc
	$(CXX) -std=c++03 -c $^ -o $@

clean:
	rm -f *.o trax

lint:
	cpplint *.cc *.h
	cloc *.cc *.h

.PHONY: all test clean lint
