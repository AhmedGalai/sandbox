# Collect all source files from subdirectories
file(GLOB_RECURSE CORE_SOURCES
    ${CMAKE_SOURCE_DIR}/src/core/*.cpp
)

file(GLOB_RECURSE GUI_SOURCES
    ${CMAKE_SOURCE_DIR}/src/gui/*.cpp
)

file(GLOB_RECURSE COMPONENTS_SOURCES
    ${CMAKE_SOURCE_DIR}/src/components/*.cpp
)

file(GLOB_RECURSE SERIALIZATION_SOURCES
    ${CMAKE_SOURCE_DIR}/src/serialization/*.cpp
)

file(GLOB_RECURSE REGISTRY_SOURCES
    ${CMAKE_SOURCE_DIR}/src/registry/*.cpp
)

# Collect all header files (for IDE integration and dependency tracking)
file(GLOB_RECURSE HEADERS
    ${CMAKE_SOURCE_DIR}/include/*.h
    ${CMAKE_SOURCE_DIR}/include/*.hpp
)

# Combine all sources
set(VSE_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
    ${CORE_SOURCES}
    ${GUI_SOURCES}
    ${COMPONENTS_SOURCES}
    ${SERIALIZATION_SOURCES}
    ${REGISTRY_SOURCES}
)

# Optional: collect UI files for Qt Designer forms
file(GLOB_RECURSE UI_FILES
    ${CMAKE_SOURCE_DIR}/src/gui/*.ui
)

# Optional: collect resource files
file(GLOB_RECURSE QRC_FILES
    ${CMAKE_SOURCE_DIR}/resources/*.qrc
)

# Create the executable target
add_executable(VSE
    ${VSE_SOURCES}
    ${HEADERS}
    ${UI_FILES}
    ${QRC_FILES}
)

# Link Qt6 libraries
target_link_libraries(VSE PRIVATE
    Qt6::Core
    Qt6::Widgets
    Qt6::Network
    Qt6::Gui
)

# Link nlohmann_json if found via find_package
if(TARGET nlohmann_json::nlohmann_json)
    target_link_libraries(VSE PRIVATE nlohmann_json::nlohmann_json)
endif()

# Set additional compile options for better warnings and optimization
target_compile_options(VSE PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)

# Platform-specific configurations
if(WIN32)
    # On Windows, create a GUI application (not console)
    set_target_properties(VSE PROPERTIES
        WIN32_EXECUTABLE TRUE
    )
endif()

# Install rules (optional)
install(TARGETS VSE
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# Print source file count for debugging
list(LENGTH VSE_SOURCES SOURCE_COUNT)
message(STATUS "Building VSE with ${SOURCE_COUNT} source files")
