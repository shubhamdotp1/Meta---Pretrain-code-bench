#include <gtest/gtest.h>  // Include GoogleTest: keep this.
// Add the necessary libraries here

#include "../include/prototype.h" // Include Prototype: keep this.

// Add all test cases here.

// The following function will run all created test cases:
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}