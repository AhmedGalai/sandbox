# VSE - Visual Scripting Environment

A modern, component-based visual scripting environment built with Qt6 and C++17.

## Overview

VSE (Visual Scripting Environment) is a node-based visual programming tool that allows users to create complex logic flows through an intuitive graphical interface. It features a flexible component architecture with a topic/data bus system for inter-node communication.

## Features

- **Visual Node Graph**: Intuitive drag-and-drop interface for building logic flows
- **Component-Based Architecture**: Modular design with reusable components
- **Topic/Data Bus System**: Flexible publish-subscribe communication pattern
- **Multiple Component Types**:
  - Logic components (AND, OR, NOT, conditional gates)
  - Math components (arithmetic, trigonometric, comparison)
  - Network components (TCP, UDP, HTTP client/server)
  - I/O components (file read/write, console, GPIO)
- **Real-time Execution**: Live execution with visual feedback
- **Serialization**: Save and load graph configurations as JSON
- **Extensible Design**: Easy to add custom components
- **Cross-platform**: Built on Qt6 for Linux, Windows, and macOS support

## Requirements

### Build Dependencies

- **CMake** 3.16 or higher
- **C++17** compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- **Qt6** with the following modules:
  - Qt6::Core
  - Qt6::Widgets
  - Qt6::Network
  - Qt6::Gui
- **nlohmann/json** (header-only library for JSON parsing)

### Installing Dependencies

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install cmake build-essential qt6-base-dev nlohmann-json3-dev
```

#### Fedora/RHEL

```bash
sudo dnf install cmake gcc-c++ qt6-qtbase-devel json-devel
```

#### Arch Linux

```bash
sudo pacman -S cmake gcc qt6-base nlohmann-json
```

#### macOS (via Homebrew)

```bash
brew install cmake qt@6 nlohmann-json
```

#### Windows

1. Install CMake from https://cmake.org/download/
2. Install Qt6 from https://www.qt.io/download
3. Download nlohmann/json header from https://github.com/nlohmann/json

## Building VSE

### Clone and Build

```bash
# Clone the repository (if from git)
# git clone <repository-url>
# cd VSE

# Create build directory
mkdir build
cd build

# Configure with CMake
cmake ..

# Build the project
cmake --build .

# Optionally install
sudo cmake --install .
```

### Build Options

- **BUILD_TESTS**: Enable/disable test suite (default: OFF)

```bash
cmake -DBUILD_TESTS=ON ..
```

### Build Output

The compiled executable will be located at:
```
build/bin/VSE
```

## Usage

### Running VSE

```bash
./build/bin/VSE
```

### Basic Workflow

1. **Create Nodes**: Right-click on the canvas to add nodes from the component library
2. **Connect Nodes**: Drag connections between output and input pins
3. **Configure Nodes**: Double-click nodes to set parameters and properties
4. **Execute Graph**: Click the "Run" button to execute the visual script
5. **Save/Load**: Use File menu to save graphs as JSON or load existing configurations

### Example Use Cases

- **Data Processing Pipelines**: Read data, transform it, and output results
- **Network Automation**: Create TCP/UDP servers and clients visually
- **Logic Controllers**: Build state machines and control logic
- **Math Calculations**: Perform complex calculations with visual feedback
- **I/O Automation**: Read/write files and interact with system I/O

## Project Structure

```
VSE/
├── CMakeLists.txt          # Root CMake configuration
├── README.md               # This file
├── ARCHITECTURE.md         # Detailed architecture documentation
├── include/                # Public header files
│   ├── core/              # Core system headers (Node, Edge, Topic, DataBus)
│   ├── gui/               # GUI headers (MainWindow, NodeView, NodeScene)
│   ├── components/        # Component headers
│   │   ├── logic/         # Logic component headers
│   │   ├── math/          # Math component headers
│   │   ├── network/       # Network component headers
│   │   └── io/            # I/O component headers
│   ├── serialization/     # Serialization system headers
│   └── registry/          # Component registry headers
├── src/                   # Implementation files
│   ├── main.cpp           # Application entry point
│   ├── core/              # Core system implementation
│   ├── gui/               # GUI implementation
│   ├── components/        # Component implementations
│   │   ├── logic/
│   │   ├── math/
│   │   ├── network/
│   │   └── io/
│   ├── serialization/     # Serialization implementation
│   └── registry/          # Component registry implementation
├── resources/             # Application resources
│   ├── icons/            # Icon files
│   └── styles/           # Qt stylesheets
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures and data
├── examples/            # Example VSE graphs
├── docs/               # Additional documentation
└── external/           # Third-party libraries (nlohmann/json)
```

## Development

### Adding Custom Components

1. Create header in `include/components/<category>/`
2. Implement in `src/components/<category>/`
3. Register component in `ComponentRegistry`
4. Rebuild the project

See `ARCHITECTURE.md` for detailed component development guidelines.

### Code Style

- Follow C++17 best practices
- Use Qt naming conventions for Qt-related code
- Use camelCase for methods, PascalCase for classes
- Document public APIs with Doxygen-style comments

## Testing

To build and run tests:

```bash
mkdir build && cd build
cmake -DBUILD_TESTS=ON ..
cmake --build .
ctest --output-on-failure
```

## Contributing

Contributions are welcome! Please:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

[Specify your license here]

## Authors

[Specify authors/contributors here]

## Acknowledgments

- Built with [Qt6](https://www.qt.io/)
- JSON parsing by [nlohmann/json](https://github.com/nlohmann/json)
- Inspired by visual scripting systems like Unreal Engine Blueprints and Node-RED

## Support

For issues, questions, or contributions, please [specify contact method or issue tracker].
