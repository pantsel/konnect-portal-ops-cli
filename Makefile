SRC_DIR := src/kptl
MAIN_SCRIPT := $(SRC_DIR)/main.py

DIST_DIR := dist

EXECUTABLE := kptl

# Clean previous builds
.PHONY: clean
clean:
	rm -rf $(DIST_DIR) build *.spec

.PHONY: package
package: clean
	pyinstaller --onefile --name $(EXECUTABLE) $(MAIN_SCRIPT)

.PHONY: build
build: package
	@echo "Executable created in $(DIST_DIR)/$(EXECUTABLE)"

.PHONY: setup
setup:
	python setup.py sdist bdist_wheel
	@echo "Setup complete"

.PHONY: install
install: setup
	pip install .
	kptl --version
	@echo "Local install complete, run 'kptl --help' to verify"

.PHONY: publish
publish: setup
	twine upload --non-interactive dist/*
	@echo "Publish complete"

.PHONY: uninstall
uninstall:
	pip uninstall kptl
	@echo "Uninstall complete"

.PHONY: test
test:
	PYTHONPATH=src pytest tests/ -vv


# Default target
.PHONY: all
all: build

