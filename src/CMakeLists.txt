# Define this directory's flags:
add_compile_options(${vdt_lib_cxx_flags})

# We need Python for the following.
find_package (Python COMPONENTS Interpreter REQUIRED)

if(vdt_BUILD_SHARED_LIBS)
  message(STATUS "Libraries are configured as: SHARED")
else()
  message(STATUS "Libraries are configured as: STATIC")
endif()

if(PRELOAD)
  message(STATUS "Symbols for the preload requested")
endif()

# Generate the code for the lib
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_LIST_DIR}/vdtMath_signatures.cc
  COMMAND ${Python_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/signatures_generator.py
    $<$<BOOL:${PRELOAD}>:-p>
    -o ${CMAKE_CURRENT_LIST_DIR}
  )

#generare Vc wrapper and config file
if(USE_VC)
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_LIST_DIR}/vdtdiag_vcWrapper.h
           ${CMAKE_CURRENT_LIST_DIR}/vdtdiag_vcWrapper.cc
    COMMAND ${Python_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/vc_wrapper_generator.py
      -o ${CMAKE_CURRENT_LIST_DIR}
    )
endif(USE_VC)

configure_file( ${CMAKE_SOURCE_DIR}/include/externalLibcfg.h.in
  ${CMAKE_SOURCE_DIR}/include/externalLibcfg.h)

#========================================================================================
# Rules for making the so library with the vector and libm-like signatures

# # The library
if(vdt_BUILD_SHARED_LIBS)
  add_library(vdt SHARED ${CMAKE_CURRENT_LIST_DIR}/vdtMath_signatures.cc)
else()
  add_library(vdt STATIC ${CMAKE_CURRENT_LIST_DIR}/vdtMath_signatures.cc)
endif()

target_include_directories(vdt PUBLIC ${CMAKE_SOURCE_DIR}/include)

# Build Vc wrapper (without c++11)
if(USE_VC)
    add_library(VcWrapper
      ${CMAKE_CURRENT_LIST_DIR}/vdtdiag_vcWrapper.h
      ${CMAKE_CURRENT_LIST_DIR}/vdtdiag_vcWrapper.cc
    )
    target_compile_options("-fabi-version=6")
    target_include_directories(VcWrapper PUBLIC ${CMAKE_SOURCE_DIR}/Vc
      PUBLIC ${CMAKE_SOURCE_DIR}/Vc/include )
    target_link_libraries(VcWrapper libVc.a)
endif()

#-------------------------------------------------------------------------------
# Installation

# Installation of the lib
install(TARGETS vdt  
        DESTINATION lib)

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
