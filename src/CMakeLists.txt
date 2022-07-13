# Define this directory's flags:
add_compile_options(${vdt_lib_cxx_flags})

# We need Python for the following.
find_package (Python COMPONENTS Interpreter REQUIRED)

if(BUILD_SHARED_LIBS)
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

#========================================================================================
# Rules for making the so library with the vector and libm-like signatures

# # The library
add_library( vdt )
add_library( vdt::vdt ALIAS vdt )   # necessory for fetch_content imported target vdt::vdt
target_sources(vdt
  PRIVATE ${CMAKE_CURRENT_LIST_DIR}/vdtMath_signatures.cc
)
target_include_directories( vdt
  PUBLIC $<BUILD_INTERFACE:${vdt_INCLUDE_DIR}>$<INSTALL_INTERFACE:include/vdt>
)
set_target_properties( vdt PROPERTIES
  POSITION_INDEPENDENT_CODE ON
  PUBLIC_HEADER "${vdt_HEADERS}"
  VERSION "${PROJECT_VERSION}"
  SOVERSION "${ABI_VERSION}"
)

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
