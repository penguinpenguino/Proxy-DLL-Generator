# Generates headers to create proxy DLLs
# Just include the header in your DLL to proxy it

import sys, os, argparse, pefile, win32file

parser = argparse.ArgumentParser(prog="generate", description="Generates headers for proxy DLLs", epilog="The naming convention is quite strict, you MUST rename the DLL you are proxying to the name supplied to \'--name\' and rename the compiled DLL to the name of the DLL you are proxying.")
parser.add_argument("target")
parser.add_argument("-o", "--output", nargs=2, default=['PROXY.h', 'PROXY.def'], help="File outputs (at least one .h and one .def)")
parser.add_argument("-n", "--name", nargs=1, required=True, help="Name for what you will rename the DLL to.")
parser.add_argument("--arg-count", nargs=1, default=[25], help="Number of arguments functions should take, making this too few will cause undefined behavior.", type=int)
parser.add_argument("--prefix", nargs=2, default=["FUNC_", "PROXY_"], help="Prefix for function names from the proxied DLL (Order: OriginalFunctionPrefix, ProxyFunctionprefix)")
args = parser.parse_args()

for item in args.prefix:
    if item == "":
        print("Prefix cannot be empty")
        sys.exit(1)

header = None
_def = None
for item in args.output:
    if item.endswith('.h'):
        header = item
    if item.endswith('.def'):
        _def = item
if header == None:
    header = "PROXY.h"
if _def == None:
    _def = "PROXY.def"

if args.name[0].split('.').__len__() > 2:
    print("More than one \'.\' character in the DLLs name (I don\'t make the rules)")
    sys.exit(1)

if not os.path.exists(args.target):
    print(f"\'{args.target}\' does not exist.")
    sys.exit(1)

header_file = open(header, 'w')
def_file = open(_def, 'w')
def_file.write(f"LIBRARY    {args.target.split('.')[0]}\n")

header_file.write(f"#pragma once\n\n// Edit functions named {args.prefix[1]}* to change behavior when a function is called.\n\n")
header_file.write("extern \"C\" {\n")
def_file.write("IMPORTS\n")

InFunctionArgs = ""
WhenCallingArgs = ""
for i in range(args.arg_count[0]):
    InFunctionArgs += f"void* arg{i}"
    WhenCallingArgs += f"arg{i}"
    if i <= args.arg_count[0] - 2:
        InFunctionArgs += ", "
        WhenCallingArgs += ", "

dll = pefile.PE(args.target)
for export in dll.DIRECTORY_ENTRY_EXPORT.symbols:
    header_file.write(f"    void* {args.prefix[0]}{export.name.decode()}({InFunctionArgs});\n")
    def_file.write(f"    {args.prefix[0]}{export.name.decode()} = {args.name[0]}.{export.name.decode()}\n")

def_file.write("EXPORTS\n")

for export in dll.DIRECTORY_ENTRY_EXPORT.symbols:
    header_file.write(f"    void* {args.prefix[1]}{export.name.decode()}({InFunctionArgs});\n")
    def_file.write(f"    {export.name.decode()} = {args.prefix[1]}{export.name.decode()}\n")

def_file.close()

header_file.write("}\n\n")

for export in dll.DIRECTORY_ENTRY_EXPORT.symbols:
    header_file.write(f"void* {args.prefix[1]}{export.name.decode()}({InFunctionArgs})")
    header_file.write(" {\n")
    header_file.write(f"    return {args.prefix[0]}{export.name.decode()}({WhenCallingArgs});")
    header_file.write("\n}\n\n")

header_file.close()
