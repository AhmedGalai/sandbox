# VSE Build Instructions

Quick reference for building the Visual Scripting Environment.

## Prerequisites

Ensure you have the following installed:

```bash
# Check versions
cmake --version    # Should be 3.16+
g++ --version      # Should support C++17
qmake6 --version   # Qt6 installation check
```

## Quick Build

### Standard Build

```bash
# From VSE root directory
mkdir build && cd build
cmake ..
cmake --build .
```

### Debug Build

```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
```

### Release Build

```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
```

### Build with Tests

```bash
mkdir build && cd build
cmake -DBUILD_TESTS=ON ..
cmake --build .
ctest --output-on-failure
```

## Running VSE

After building:

```bash
./build/bin/VSE
```

## CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| BUILD_TESTS | OFF | Build the test suite |
| CMAKE_BUILD_TYPE | Debug | Build type (Debug, Release, RelWithDebInfo, MinSizeRel) |
| CMAKE_INSTALL_PREFIX | /usr/local | Installation directory |

### Using Options

```bash
cmake -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Release ..
```

## Cleaning Build

```bash
# Remove build directory
rm -rf build

# Or clean within build directory
cd build
cmake --build . --target clean
```

## Installation

```bash
cd build
sudo cmake --install .
```

This will install:
- Binary: `/usr/local/bin/VSE`
- Libraries: `/usr/local/lib/`
- Headers: `/usr/local/include/VSE/` (if configured)

## Troubleshooting

### Qt6 Not Found

```bash
# Specify Qt6 path manually
cmake -DCMAKE_PREFIX_PATH=/path/to/Qt6 ..

# Example on Linux
cmake -DCMAKE_PREFIX_PATH=/usr/lib/qt6 ..

# Example on macOS with Homebrew
cmake -DCMAKE_PREFIX_PATH=/usr/local/opt/qt@6 ..
```

### nlohmann/json Not Found

Download the single-header file:

```bash
mkdir -p external/nlohmann
cd external/nlohmann
wget https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp
cd ../..
```

Or install system-wide:

```bash
# Ubuntu/Debian
sudo apt install nlohmann-json3-dev

# Fedora
sudo dnf install json-devel

# Arch Linux
sudo pacman -S nlohmann-json
```

### Compiler Errors

Ensure C++17 support:

```bash
# GCC 7+ or Clang 5+
g++ --version
clang++ --version

# Specify compiler manually
cmake -DCMAKE_CXX_COMPILER=g++-9 ..
```

### Build Fails with Missing Files

Current status: The build system is set up, but implementation files are still being created. You may see errors about missing source files until all modules are implemented.

**To build successfully right now**, you need to:
1. Implement the header files in `include/`
2. Implement the source files in `src/`
3. The build system is ready and waiting for these files

## Build Output

Successful build produces:

```
build/
├── bin/
│   └── VSE              # Main executable
└── lib/                # Any libraries (if created)
```

## Parallel Build

Speed up compilation with parallel jobs:

```bash
# Use all CPU cores
cmake --build . -j$(nproc)

# Or specify number of jobs
cmake --build . -j4
```

## Build Configuration Summary

After running CMake, you'll see a summary:

```
VSE Configuration Summary:
  CMake version: 3.16.3
  C++ standard: 17
  Build type: Debug
  Qt version: 6.5.0
  Build tests: OFF
```

## IDE Integration

### VS Code

Install CMake Tools extension and use:
- `Ctrl+Shift+P` → "CMake: Configure"
- `Ctrl+Shift+P` → "CMake: Build"

### CLion

CLion automatically detects CMakeLists.txt. Just open the VSE directory.

### Qt Creator

Open CMakeLists.txt as a project. Qt Creator will handle configuration.

## Next Steps After Successful Build

1. Run the executable: `./build/bin/VSE`
2. Read `ARCHITECTURE.md` for development guidance
3. Check `examples/` for usage examples
4. Run tests if built: `cd build && ctest`

## Development Workflow

```bash
# 1. Make changes to source files
vim src/core/Node.cpp

# 2. Rebuild (CMake auto-detects changes)
cd build
cmake --build .

# 3. Run
./bin/VSE

# 4. Test (if BUILD_TESTS=ON)
ctest --output-on-failure
```

## Performance Tips

- Use Release build for production: `-DCMAKE_BUILD_TYPE=Release`
- Enable compiler optimizations: Release builds include `-O3` automatically
- Use parallel builds: `-j$(nproc)`
- Use ccache for faster rebuilds: `cmake -DCMAKE_CXX_COMPILER_LAUNCHER=ccache ..`

## Cross-Platform Notes

### Linux
Standard build should work out of the box.

### macOS
May need to set Qt6 path with Homebrew:
```bash
cmake -DCMAKE_PREFIX_PATH=$(brew --prefix qt@6) ..
```

### Windows
Use Visual Studio or MinGW:
```bash
# Visual Studio
cmake -G "Visual Studio 17 2022" ..
cmake --build . --config Release

# MinGW
cmake -G "MinGW Makefiles" ..
cmake --build .
```

## Getting Help

- Check `README.md` for project overview
- Read `ARCHITECTURE.md` for design details
- Open an issue for build problems
- Consult Qt6 documentation for Qt-specific issues
