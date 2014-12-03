cmake_minimum_required( VERSION 2.8.12 )

set( CMAKE_OSX_RPATH 1 )

add_compile_options( -Wall -Wextra )
if( CMAKE_C_COMPILER_ID MATCHES Clang )
    add_compile_options( -XClang -fcolor-diagnostics )
endif( )
