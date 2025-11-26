cmake_minimum_required(VERSION 3.16)

# Project configuration
project(VSE VERSION 1.0.0 LANGUAGES CXX)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Output directories for better organization
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Find Qt6 packages
# We need Core for basic Qt functionality, Widgets for GUI,
# Network for network components, and Gui for graphics
find_package(Qt6 REQUIRED COMPONENTS
    Core
    Widgets
    Network
    Gui
)

# Enable Qt's Meta-Object Compiler (MOC), User Interface Compiler (UIC),
# and Resource Compiler (RCC) to run automatically
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/include/core
    ${CMAKE_SOURCE_DIR}/include/gui
    ${CMAKE_SOURCE_DIR}/include/components
    ${CMAKE_SOURCE_DIR}/include/serialization
    ${CMAKE_SOURCE_DIR}/include/registry
)

# Look for nlohmann/json in external directory
# This is a header-only library, so we just need to add the include path
if(EXISTS "${CMAKE_SOURCE_DIR}/external/nlohmann")
    include_directories(${CMAKE_SOURCE_DIR}/external/nlohmann)
    message(STATUS "Found nlohmann/json in external directory")
else()
    # Try to find it via find_package if installed system-wide
    find_package(nlohmann_json QUIET)
    if(nlohmann_json_FOUND)
        message(STATUS "Found nlohmann/json via find_package")
    else()
        message(WARNING "nlohmann/json not found. Please add it to external/ directory or install system-wide")
    endif()
endif()

# Add source directory
add_subdirectory(src)

# Optionally add tests if enabled
option(BUILD_TESTS "Build test suite" OFF)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Print configuration summary
message(STATUS "")
message(STATUS "VSE Configuration Summary:")
message(STATUS "  CMake version: ${CMAKE_VERSION}")
message(STATUS "  C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Qt version: ${Qt6Core_VERSION}")
message(STATUS "  Build tests: ${BUILD_TESTS}")
message(STATUS "")
