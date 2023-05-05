# Proxy-DLL-Generator
A library generator held together by scotch tape. I might update this a few times but no promisses.

## Requirements
pefile (`pip install pefile`)

## Example
Example hook with the 32-bit `ffmpeg.dll` library.

### PROXY.cpp source code
This will remain the same for both examples.

```cpp
#include "PROXY.h"
#include <Windows.h>
#include <iostream>

__attribute__((constructor)) void OnLoad() {
    AllocConsole();
    freopen("CONOUT$", "w", stdout);
    std::cout << "Hello, World!" << std::endl;
}
```

### Without the `--dynamic` option

1. Creating the files: `python3 generate.py -n ffmpeg_proxy.dll ffmpeg.dll`
2. Rename `ffmpeg.dll` to `ffmpeg_proxy.dll`
3. Compiling everything (using a 32-bit version of g++): `g++ -shared -fPIC PROXY.cpp PROXY.def -o ffmpeg.dll -L. -lffmpeg_proxy -mwindows`
4. Done, `ffmpeg_proxy.dll` is the unedited version of ffmpeg and `ffmpeg.dll` is our magic DLL

### With the `--dynamic` option

1. Creating the files: `python3 generate.py -n ffmpeg_proxy.dll --dynamic ffmpeg.dll`
2. Rename `ffmpeg.dll` to `ffmpeg_proxy.dll`
3. Compiling everything (using a 32-bit version of g++): `g++ -shared -fPIC PROXY.cpp PROXY.def -o ffmpeg.dll -mwindows`
4. Done, `ffmpeg_proxy.dll` is the unedited version of ffmpeg and `ffmpeg.dll` is our magic DLL

glhf
