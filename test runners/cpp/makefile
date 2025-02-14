# Makefile

# If you installed Google Test system-wide, this is not needed:
GTEST_DIR = /path/to/gtest  # Replace with the path to your Google Test installation

# Define the versions to test (just the names of the C files)
VERSIONS = A B C base ideal incorrect

all: $(VERSIONS)

# Rule for each version
$(VERSIONS):
		mkdir -p build_$@
		g++ ./src/$@.cpp ./test/exponent_test.cpp -o build_$@/exponent_test -lgtest -std=c++11

# Run "make clean" to remove previous compilation directories and log files
clean:
		rm -rf build_*
		rm -rf *log

# Just type "make run" to compile all versions and run the test cases on all files
# The system will output separate log files for each execution.
run: all
		@for version in $(VERSIONS); do \
				echo "Running tests for $$version..."; \
				./build_$$version/exponent_test > Results_$$version.log; \
				echo "Wrote log file Results_$$version.log."; \
		done
