# VDT Math Library
cmake_minimum_required(VERSION 3.15)
project (Vdt VERSION 0.5.0)

set(CMAKE_CXX_STANDARD 11)
# set(CMAKE_CXX_STANDARD_REQUIRED True)

#-------------------------------------------------------------------------------
# Include the defaults
include ( CMakeDefaults.txt )
#-------------------------------------------------------------------------------

# configuration options -- you may change them when running cmake ==============
# with 'cmake -D <OPT>=<value> .'

option( DIAG "Build in diagnostic mode - all diagnostic exes (default cache entry: OFF)" OFF)
option( AVX "Use AVX instruction set (default cache entry: OFF)" OFF)
option( AVX2 "Use AVX2 instruction set (default cache entry: OFF)" OFF)
option( FMA "Use FMA instruction set (default cache entry: OFF)" OFF)
option( USERFLAGS "Pass arbitrary flags to the compiler")
option( SSE "Use SSE instruction set (default cache entry: ON)" ON)
option( NEON "Use NEON instruction set (default cache entry: OFF)" OFF)
option( BUILD_SHARED_LIBS "Build libraries as SHARED instead of STATIC (default cache entry: OFF)" OFF)
option( PRELOAD "Create in the library the symbols to preload the library (default cache entry: OFF)" OFF)
option( USE_VC "Use Vc library - requires symlink to Vc from ${CMAKE_SOURCE_DIR} (default cache entry: OFF)" OFF)
option( DEBUG "Compile library with debug symbols (default is OFF)" OFF)

message(${CMAKE_CXX_COMPILER_ID})

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 4.8)
    message(FATAL_ERROR "VDT requires GCC version >= 4.8")
    set(COMP_IS_GCC TRUE)
  endif()
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
  if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 5.0)
    message(FATAL_ERROR "VDT requires AppleClang version >= 5.0")
  endif()
  set(COMP_IS_CLANG TRUE)
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 3.3)
    message(FATAL_ERROR "VDT requires Clang version >= 3.3")
  endif()
  set(COMP_IS_CLANG TRUE)
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
  if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 15.0)
    message(FATAL_ERROR "VDT requires ICC >= 15.0")
    set(COMP_IS_ICC TRUE)
  endif()
else()
  message(WARNING "You are using an unsupported compiler! Compilation has only been tested with Clang, ICC and GCC.")
endif()

# SIMD and FMA instructions set-------------------------------------------------
if (NEON)
  message(STATUS "Using NEON instructions!")
  list(APPEND vdt_common_cxx_flags "-mfpu=neon")
else()
  if (SSE AND (NOT (AVX OR AVX2) ))
    message(STATUS "Using SSE instructions!")
    list(APPEND vdt_common_cxx_flags "-msse")
  endif ()

  if (AVX AND (NOT AVX2))
    message(STATUS "Using AVX instructions!")
    if(CMAKE_COMPILER_IS_ICC)
      list(APPEND vdt_common_cxx_flags "-xavx")
    else()
      list(APPEND vdt_common_cxx_flags "-mavx")
    endif()
  endif ()

  if (AVX2)
    message(STATUS "Using AVX2 instructions!")
    if(CMAKE_COMPILER_IS_ICC)
      list(APPEND vdt_common_cxx_flags "-xavx2")
    else()
      list(APPEND vdt_common_cxx_flags "-mavx2")
    endif()
  endif ()

  if (FMA)
    message(STATUS "Using FMA instructions!")
    list(APPEND vdt_common_cxx_flags "-mfma")
  endif ()

endif()

# To use svml at CERN ----------------------------------------------------------
if (SVML)
  message (STATUS "Linking SVML library")
  list(APPEND vdt_common_cxx_flags
    "-mveclibabi=svml" "-lsvml" "-lirc"
    "-L/afs/cern.ch/sw/IntelSoftware/linux/x86_64/Compiler/11.1/072/lib/intel64/")
endif (SVML)

# Vc setup ---------------------------------------------------------------------

if(USE_VC)
  message(STATUS "VC usage is turned on now, if you do not intend to use it, run 'cmake -D USE_VC=0 .'")
  set (VC_SYMLINK_MSG "To use Vc you must have a (symlink) 'Vc' leading to the Vc rootdir in your ${CMAKE_SOURCE_DIR}")
  #check for files
  set (VC_LIB_NAME "${CMAKE_SOURCE_DIR}/Vc/libVc.a")
  set (VC_HEADER_NAME "${CMAKE_SOURCE_DIR}/Vc/include/Vc/Vc")

  if(NOT EXISTS ${VC_LIB_NAME})
    message(STATUS "Vc lib not found at ${VC_LIB_NAME}, turning off Vc usage")
    message(STATUS ${VC_SYMLINK_MSG})
    change_option(USE_VC 0)
  endif(NOT EXISTS ${VC_LIB_NAME})

  if (EXISTS ${VC_LIB_NAME})
    if(NOT EXISTS ${VC_HEADER_NAME})
      message(STATUS "Vc header not found at ${VC_HEADER_NAME}, turning off Vc usage")
      message(STATUS ${VC_SYMLINK_MSG})
      change_option(USE_VC 0)
    endif(NOT EXISTS ${VC_HEADER_NAME})
  endif(EXISTS ${VC_LIB_NAME})

  link_directories( ${CMAKE_SOURCE_DIR}/Vc )
endif(USE_VC)

# set compiler options =========================================================
if(DIAG)
  # Library for time measurement: macOS and Linux
  set (LIBTIMING "rt")
  # do not set it if on macOS
  if (APPLE AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS 8.0)
    set (LIBTIMINGAPPLE "-framework Carbon")
  endif ()
endif(DIAG)

#-------------------------------------------------------------------------------
# Compiler optimisations

if (NOT CMAKE_COMPILER_IS_ICC)
  list(APPEND vdt_common_cxx_flags "-Ofast")
endif()

if (${COMP_IS_GCC})
   set (VECTORIZER_VERBOSITY "-ftree-vectorizer-verbose=0")
   list(APPEND vdt_common_cxx_flags "--param vect-max-version-for-alias-checks=50"
   "--param inline-unit-growth=150")   
endif()   

set (VERBOSITY_OPT "-Winline")

# set it for clang until it understands __always_inline
if (${COMP_IS_CLANG})
  list(APPEND vdt_common_cxx_flags "-D__extern_always_inline=inline")
endif()

# compiler dependent changes ---------------------------------------------------
if(${COMP_IS_ICC})
  set (VECTORIZER_VERBOSITY "")
endif()

list(APPEND vdt_common_cxx_flags "-W" "-Wall" "-Werror"
  "-Wno-error=unused-parameter")

if (DEBUG)
  message(STATUS "Adding debugging symbols")
  list(APPEND vdt_common_cxx_flags "-g")
endif ()

set (COMMON_FLAGS "${PACKED_INSTR}")
if (USERFLAGS)
  list(APPEND vdt_common_cxx_flags ${USERFLAGS})
endif()

list(APPEND vdt_lib_cxx_flags ${VERBOSITY_OPT} ${VECTORIZER_VERBOSITY} "${vdt_common_cxx_flags}")
list(APPEND vdt_diag_cxx_flags ${LIBTIMINGAPPLE} "${vdt_common_cxx_flags}")

#-------------------------------------------------------------------------------

# Positions
set(vdt_BIN_DIR ${CMAKE_CURRENT_LIST_DIR}/bin)
set(vdt_INCLUDE_DIR ${CMAKE_CURRENT_LIST_DIR}/include)

# Public Headers
list(APPEND vdt_HEADERS
  include/asin.h
  include/atan.h
  include/tanh.h
  include/atan2.h
  include/cos.h
  include/exp.h
  include/identity.h
  include/inv.h
  include/log.h
  include/sincos.h
  include/sin.h
  include/sqrt.h
  include/tan.h
  include/vdtcore_common.h
  include/vdtMath.h
)

#-------------------------------------------------------------------------------

add_subdirectory( src )

if (DIAG)
    message("DIAG option is now on, building diagnostic programs")

    configure_file( externalLibcfg.h.in include/externalLibcfg.h)
    include_directories(include include/diagnostic
      $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>)

    add_subdirectory( progs )
else(DIAG)
  message("DIAG option is now off, building library only")
endif(DIAG)

# -------------------------------------------------------------------------------
# Rules of installation
include(GNUInstallDirs)

# Installation of the lib
install(TARGETS vdt
  EXPORT vdtTargets
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/vdt
  # ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} # let user define by CMAKE_ARCHIVE_OUTPUT_DIRECTORY
  # LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} # let user define by CMAKE_LIBRARY_OUTPUT_DIRECTORY
  # RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} # let user define by CMAKE_RUNTIME_OUTPUT_DIRECTORY
)

# target configurations for install-tree
install(EXPORT vdtTargets
  NAMESPACE vdt::
  FILE vdtTargets.cmake
  DESTINATION lib/cmake/vdt
)

# target configurations for build-tree
export(EXPORT vdtTargets
  NAMESPACE vdt::
  FILE vdtTargets.cmake
)

include( CMakePackageConfigHelpers )

configure_package_config_file(vdtConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/vdtConfig.cmake
  INSTALL_DESTINATION lib/cmake/vdt
  NO_SET_AND_CHECK_MACRO
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/vdtConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMinorVersion )

install (
  FILES 
    ${CMAKE_CURRENT_BINARY_DIR}/vdtConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/vdtConfigVersion.cmake
  DESTINATION lib/cmake/vdt)
