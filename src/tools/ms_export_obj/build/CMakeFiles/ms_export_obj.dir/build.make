# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canoncical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/Cellar/cmake/2.8.6/bin/cmake

# The command to remove a file.
RM = /usr/local/Cellar/cmake/2.8.6/bin/cmake -E remove -f

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/local/Cellar/cmake/2.8.6/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /projects/Mayaseed/src/tools/ms_export_obj/src

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /projects/Mayaseed/src/tools/ms_export_obj/build

# Include any dependencies generated for this target.
include CMakeFiles/ms_export_obj.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/ms_export_obj.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/ms_export_obj.dir/flags.make

CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o: CMakeFiles/ms_export_obj.dir/flags.make
CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o: /projects/Mayaseed/src/tools/ms_export_obj/src/ms_export_obj.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /projects/Mayaseed/src/tools/ms_export_obj/build/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o -c /projects/Mayaseed/src/tools/ms_export_obj/src/ms_export_obj.cpp

CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /projects/Mayaseed/src/tools/ms_export_obj/src/ms_export_obj.cpp > CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.i

CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /projects/Mayaseed/src/tools/ms_export_obj/src/ms_export_obj.cpp -o CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.s

CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.requires:
.PHONY : CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.requires

CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.provides: CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.requires
	$(MAKE) -f CMakeFiles/ms_export_obj.dir/build.make CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.provides.build
.PHONY : CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.provides

CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.provides.build: CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o

# Object files for target ms_export_obj
ms_export_obj_OBJECTS = \
"CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o"

# External object files for target ms_export_obj
ms_export_obj_EXTERNAL_OBJECTS =

libms_export_obj.dylib: CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o
libms_export_obj.dylib: CMakeFiles/ms_export_obj.dir/build.make
libms_export_obj.dylib: CMakeFiles/ms_export_obj.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX shared library libms_export_obj.dylib"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/ms_export_obj.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/ms_export_obj.dir/build: libms_export_obj.dylib
.PHONY : CMakeFiles/ms_export_obj.dir/build

CMakeFiles/ms_export_obj.dir/requires: CMakeFiles/ms_export_obj.dir/ms_export_obj.cpp.o.requires
.PHONY : CMakeFiles/ms_export_obj.dir/requires

CMakeFiles/ms_export_obj.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/ms_export_obj.dir/cmake_clean.cmake
.PHONY : CMakeFiles/ms_export_obj.dir/clean

CMakeFiles/ms_export_obj.dir/depend:
	cd /projects/Mayaseed/src/tools/ms_export_obj/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /projects/Mayaseed/src/tools/ms_export_obj/src /projects/Mayaseed/src/tools/ms_export_obj/src /projects/Mayaseed/src/tools/ms_export_obj/build /projects/Mayaseed/src/tools/ms_export_obj/build /projects/Mayaseed/src/tools/ms_export_obj/build/CMakeFiles/ms_export_obj.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/ms_export_obj.dir/depend
