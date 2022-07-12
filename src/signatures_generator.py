#! /usr/bin/env python

"""
Generate the .cc file with the signatures
of the vector functions and if requested 
the ones for the preload
"""

from optparse import OptionParser
import os

RESTRICT = "__restrict__"

LIBM_FUNCTIONS_LIST = ["exp",
                       "log",
                       "sin",
                       "cos",
                       "tan",
                       "tanh",
                       "asin",
                       "acos",
                       "atan",
                       "atan2"]

FUNCTIONS_LIST = LIBM_FUNCTIONS_LIST +\
    ["isqrt",
     "inv",
     "identity",
     "identity2D",
     "fast_exp",
     "fast_log",
     "fast_sin",
     "fast_cos",
     "fast_tan",
     "fast_tanh",
     "fast_asin",
     "fast_acos",
     "fast_atan",
     "fast_atan2",
     "fast_inv",
     "fast_approx_inv",
     "fast_isqrt",
     "fast_approx_isqrt"]

VDT_VECTOR_HEADER = 'vdtMath.h'
VDT_VECTOR_IMPL = 'vdtMath_signatures.cc'

#------------------------------------------------------------------

def create_vector_signature(fcn_name, type, preload=False):
  
  if type == "float":           # single precision
    vfcn_name = fcn_name + "fv"
    impl_fcn_name = fcn_name + "f"
  elif type == "double":        # double precision
    vfcn_name = fcn_name + "v"
    impl_fcn_name = fcn_name
  else:
    raise ValueError("Unknown type: " + type)

  if preload and fcn_name in LIBM_FUNCTIONS_LIST:
    impl_fcn_name = "fast_" + impl_fcn_name
  in_data_type = f"{type} const * {RESTRICT}"
  out_data_type = f"{type}* {RESTRICT}"
  code = []

  # Special case
  if "atan2" in fcn_name or "identity2D" in fcn_name:
    code.append(
      f"void {vfcn_name}(const uint32_t size, {in_data_type} iarray1, {in_data_type} iarray2, {out_data_type} oarray)"
    )
    impl_code = [
      "{",
      "  for (uint32_t i=0;i<size;++i)",
      f"    oarray[i]={impl_fcn_name}(iarray1[i],iarray2[i]);",
      "}\n"
    ]
  else:
    code.append(
      f"void {vfcn_name}(const uint32_t size, {in_data_type} iarray, {out_data_type} oarray)"
    )
    impl_code = [
      "{",
      "  for (uint32_t i=0;i<size;++i)",
      f"    oarray[i]={impl_fcn_name}(iarray[i]);",
      "}\n"
    ]

  code += impl_code
  return code

#------------------------------------------------------------------

def create_vector_signatures(preload=False):
  code = []

  code.append("// Double Precision")
  for fcn_name in FUNCTIONS_LIST:
    code += create_vector_signature(fcn_name, "double", preload)

  code.append("// Single Precision")
  for fcn_name in FUNCTIONS_LIST:
    code += create_vector_signature(fcn_name, "float",  preload)

  return code

#------------------------------------------------------------------


def create_impl(preload: bool, outdir):
  code = ["// Automatically generated\n",
      f"#include \"{VDT_VECTOR_HEADER}\"\n",
      "namespace vdt{",
    ]
  code += create_vector_signatures(preload=preload)
  code += [
      "} // end of vdt namespace",
      ""  # the final newline
    ]

  with open(os.path.join(outdir, VDT_VECTOR_IMPL), 'w') as ofile:
    ofile.write("\n".join(code))

#------------------------------------------------------------------


if __name__ == "__main__":
  parser = OptionParser(usage="usage: %prog [options]")
  parser.add_option("-p",
                    action="store_true",
                    dest="preload_flag",
                    default=False,
                    help="Create symbols for the preload")
  parser.add_option("-o",
                    dest="outdir",
                    default="./",
                    help="specify output directory")
  (options, args) = parser.parse_args()
  create_impl(preload=options.preload_flag,
              outdir=options.outdir)
