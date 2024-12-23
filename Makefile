# Define the source directory and the main entry point
SRC_DIR := src
MAIN_SCRIPT := $(SRC_DIR)/main.py

# Define the output directory
DIST_DIR := dist

# Define the name of the executable
EXECUTABLE := kptl

# Clean previous builds
.PHONY: clean
clean:
	rm -rf $(DIST_DIR) build *.spec

# Package the Python code
.PHONY: package
package: clean
	pyinstaller --onefile --name $(EXECUTABLE) $(MAIN_SCRIPT)

# Create executables for various distributions
.PHONY: build
build: package
	@echo "Executable created in $(DIST_DIR)/$(EXECUTABLE)"

# Default target
.PHONY: all
all: build
