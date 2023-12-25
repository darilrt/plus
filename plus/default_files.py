
class Defualt:
    MAIN = """\
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""

    LIB_SOURCE = """\
#include <iostream>

#include "lib.hpp"

void hello() {
    std::cout << "Hello, World!" << std::endl;
}

"""

    STATIC_LIB_HEADER = """\
#pragma once

void hello();

"""

    SHARED_LIB_HEADER = """\
#pragma once

#if defined(_MSC_VER)
#   if defined(SHARED_LIB)
#       define API __declspec(dllexport)
#   else
#       define API __declspec(dllimport)
#   endif
#elif defined(__GNUC__)
#   if defined(SHARED_LIB)
#       define API __attribute__((visibility("default")))
#   else
#       define API
#   endif
#else
#   define API
#endif

API void hello();
"""
    
    GITIGNORE = """\
# Compiled Object files
*.slo
*.lo
*.o
*.obj

# Precompiled Headers
*.gch
*.pch

# Compiled Dynamic libraries
*.so
*.dylib
*.dll

# Fortran module files
*.mod
*.smod

# Compiled Static libraries
*.lai
*.la
*.a
*.lib

# Executables
*.exe
*.out

# Vendor
vendor/
"""
