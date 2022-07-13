# Define this directory's flags:
add_compile_options(${vdt_diag_cxx_flags})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${vdt_BIN_DIR} )

# Benchmarks
add_exe_and_link ( vdtPerfBenchmark vdtPerfBenchmark.cpp ${LIBTIMING})
add_exe_and_link ( vdtArithmBenchmark vdtArithmBenchmark.cpp None)
add_exe_and_link ( vdtArithmComparison vdtArithmComparison.cpp None)

add_subdirectory( units )