# Define this directory's flags:
string(APPEND CMAKE_CXX_FLAGS ${vdt_diag_cxx_flags})
cmake_print_variables(CMAKE_CXX_FLAGS)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin )

include_directories ( ${CMAKE_SOURCE_DIR}/include/diagnostic )
include_directories ( ${CMAKE_SOURCE_DIR}/include )

# Benchmarks
add_exe_and_link ( vdtPerfBenchmark vdtPerfBenchmark.cpp ${LIBTIMING})
add_exe_and_link ( vdtArithmBenchmark vdtArithmBenchmark.cpp None)
add_exe_and_link ( vdtArithmComparison vdtArithmComparison.cpp None)

add_subdirectory( units )