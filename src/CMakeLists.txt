# Auto generate the code for the vector signatures and if needed preload

# Location of sources
set( SRC_DIR ${CMAKE_SOURCE_DIR}/src )

# We need Python for the following.
find_package (Python COMPONENTS Interpreter REQUIRED)

# Generate the code for the lib
if (PRELOAD)
set (SIGGENOPTS  " -p")
else()
set (SIGGENOPTS  " ")
endif()
EXEC_PROGRAM ("cd src;${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/src/signatures_generator.py ${SIGGENOPTS} -o ${CMAKE_SOURCE_DIR}/src;cd -")
# message(STATUS "BEFORE: ")
# add_custom_command(
#   OUTPUT ${CMAKE_CURRENT_LIST_DIR}/vdtMath_signatures.cc
#   COMMAND ${Python_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/signatures_generator.py ${SIGGENOPTS}
#     -o ${CMAKE_CURRENT_LIST_DIR}
#   DEPENDS ${CMAKE_CURRENT_LIST_DIR}/vdtMath_signatures.cc
#   USE_TERMINAL
#   )
# message(STATUS "AFTER: ")

#generare Vc wrapper and config file
if(USE_VC)
  EXEC_PROGRAM ("cd src;${Python_EXECUTABLE} vc_wrapper_generator.py;cd -")
endif(USE_VC)
configure_file( ${CMAKE_SOURCE_DIR}/include/externalLibcfg.h.in ${CMAKE_SOURCE_DIR}/include/externalLibcfg.h)

#========================================================================================
# Rules for making the so library with the vector and libm-like signatures

# Define this directory's flags:
string(APPEND CMAKE_CXX_FLAGS ${vdt_lib_cxx_flags})
cmake_print_variables(CMAKE_CXX_FLAGS)

include_directories ( ${CMAKE_SOURCE_DIR}/include )

if(BUILD_SHARED_LIBS)
  message(STATUS "Libraries are configured as: SHARED")
else()
  message(STATUS "Libraries are configured as: STATIC")
endif()

if(PRELOAD)
  message(STATUS "Symbols for the preload requested")
endif()

# The library
add_library(vdt ${SRC_DIR}/vdtMath_signatures.cc ${CMAKE_SOURCE_DIR}/include/vdtMath.h)

# Installation of the lib
install(TARGETS vdt  
        DESTINATION lib)
        

# Build Vc wrapper (without c++11)
if(USE_VC)
    string(APPEND CMAKE_CXX_FLAGS ${vdt_lib_cxx_flags} " -fabi-version=6")
    include_directories( ${CMAKE_SOURCE_DIR}/Vc  ${CMAKE_SOURCE_DIR}/Vc/include )
    add_library(VcWrapper ${SRC_DIR}/vdtdiag_vcWrapper.cc ${SRC_DIR}/vdtdiag_vcWrapper.h)
    target_link_libraries(VcWrapper libVc.a)
endif()

#-------------------------------------------------------------------------------
# Installation

# Install location
INSTALL(FILES
        ${CMAKE_SOURCE_DIR}/include/asin.h
        ${CMAKE_SOURCE_DIR}/include/atan.h
        ${CMAKE_SOURCE_DIR}/include/tanh.h
        ${CMAKE_SOURCE_DIR}/include/atan2.h
        ${CMAKE_SOURCE_DIR}/include/cos.h
        ${CMAKE_SOURCE_DIR}/include/exp.h
        ${CMAKE_SOURCE_DIR}/include/identity.h
        ${CMAKE_SOURCE_DIR}/include/inv.h
        ${CMAKE_SOURCE_DIR}/include/log.h
        ${CMAKE_SOURCE_DIR}/include/sincos.h
        ${CMAKE_SOURCE_DIR}/include/sin.h
        ${CMAKE_SOURCE_DIR}/include/sqrt.h
        ${CMAKE_SOURCE_DIR}/include/tan.h
        ${CMAKE_SOURCE_DIR}/include/vdtcore_common.h
        ${CMAKE_SOURCE_DIR}/include/vdtMath.h
        DESTINATION include/vdt)
