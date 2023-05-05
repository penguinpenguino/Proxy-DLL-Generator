import sys, os, argparse, pefile

parser = argparse.ArgumentParser(prog="generate", description="Generates headers for proxy DLLs", epilog="The naming convention is quite strict, you MUST rename the DLL you are proxying to the name supplied to \'--name\' and rename the compiled DLL to the name of the DLL you are proxying.")
parser.add_argument("target")
parser.add_argument("-o", "--output", nargs=2, default=['PROXY.h', 'PROXY.def'], help="File outputs (at least one .h and one .def)")
parser.add_argument("-n", "--name", nargs=1, required=True, help="Name for what you will rename the DLL to.")
parser.add_argument("--arg-count", nargs=1, default=[25], help="Number of arguments functions should take, making this too few will cause undefined behavior.", type=int)
parser.add_argument("--prefix", nargs=2, default=["FUNC_", "PROXY_"], help="Prefix for function names from the proxied DLL (Order: OriginalFunctionPrefix, ProxyFunctionprefix)")
parser.add_argument("--dynamic", action="store_true", help="Load the library via LoadLibraryA")
args = parser.parse_args()

for item in args.prefix:
    if item == "":
        print("Prefix cannot be empty")
        sys.exit(1)
    if any(i in item for i in [';', ':', ' ']):
        print("Cannot include special characters in prefix")
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

if not args.target == ':':
    args.target = os.getcwd() + '\\' + args.target

if not os.path.exists(args.target):
    print(f"\'{args.target}\' does not exist.")
    sys.exit(1)

header_file = open(header, 'w')
def_file = open(_def, 'w')
header_file.write(f"#pragma once\n\n// Edit functions named {args.prefix[1]}* to change behavior when a function is called.\n")
header_file.write("#include <Windows.h>\n\nHMODULE DLL;\n__attribute__((constructor)) void _LoadDLL() {\n    ::DLL = LoadLibraryA(\"" + args.name[0] + "\");\n}\n" if args.dynamic else "")

header_file.write("\nextern \"C\" {\n")

if not args.dynamic:
    def_file.write("IMPORTS\n")

InFunctionArgs = ""
WhenCallingArgs = ""
for i in range(args.arg_count[0]):
    InFunctionArgs += f"void* arg{i}"
    WhenCallingArgs += f"arg{i}"
    if i <= args.arg_count[0] - 2:
        InFunctionArgs += ", "
        WhenCallingArgs += ", "

print("Loading dll...")
dll = pefile.PE(args.target)
print("Preprocessing...")
exports = dll.DIRECTORY_ENTRY_EXPORT.symbols.copy()
RawExports = dll.DIRECTORY_ENTRY_EXPORT.symbols
for i in range(exports.__len__()):
    exports[i] = exports[i].name.decode()
    if any(j in exports[i] for j in ['?', '@', '$', '(', ')']): # half-assed fix for name mangling
        exports[i] = f"FUN_{i}"
print(f"Writing...", end="")

if not args.dynamic:
    for i in range(exports.__len__()):
        header_file.write(f"    void* {args.prefix[0]}{exports[i]}({InFunctionArgs});\n")
        def_file.write(f"    {args.prefix[0]}{exports[i]} = {args.name[0]}.{RawExports[i].name.decode()}\n")

def_file.write("EXPORTS\n")

for i in range(exports.__len__()):
    header_file.write(f"    void* {args.prefix[1]}{exports[i]}({InFunctionArgs});\n")
    def_file.write(f"    {RawExports[i].name.decode()} = {args.prefix[1]}{exports[i]}\n")

def_file.close()

header_file.write("}\n\n")

for i in range(exports.__len__()):
    header_file.write(f"void* {args.prefix[1]}{exports[i]}({InFunctionArgs})")
    header_file.write(" {\n")
    b = ""
    for j in range(args.arg_count[0]):
        b += "void*, " if j <= args.arg_count[0] - 2 else "void*"
    header_file.write(f"    return ((void* (*)({b}))GetProcAddress(::DLL, \"{exports[i]}\"))({WhenCallingArgs});")
    header_file.write("\n}\n\n")

header_file.close()