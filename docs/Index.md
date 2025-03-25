# SWORD Health MLE Challenge - Bernardo de Lemos

This document summarizes the process I followed to complete the challenge.

Solutions are provided as code. Details and explanations are provided in the `docs` directory.

## Index

- [Question 1](question_1.ipynb): Step-by-step transformation walkthrough in a Jupyter Notebook.
- [Question 1 - Testing Structure and Methodology](Question_1_Tests.md): Testing structure and methodology.
- [Question 2a](question_2a.md): Solution and explanation.
- [Question 2b](question_2b.md): Solution and explanation.

---

## Process Overview

**Initial Setup**
- Started by reading the `README.md` file to understand the instructions and project structure.
- Unzipped and inspected the data files in the `data` directory (parquet viewer and Jupyter notebook).

**Environment Configuration**
- Encountered version conflicts due to Python 3.13 on my local machine.
- Resolved the issue by modifying the `Makefile` to use Python 3.11.
- Used `uv` as the package manager.
- Created a `dev` extra in `setup.py`.
    - Added `pytest` to `dev`.
    - Added `mkdocs`, `mkdocs-material`, `mkdocs-jupyter`, and `mkdocstrings[python]` to `dev`.
- Created a `dev` target in the `Makefile` for development setup.
- Added a `get-message` command in the `Makefile` to run with a session group parameter.

## Installation Guide

### Installing `uv`
Follow the instructions in the [uv repository](https://github.com/astral-sh/uv) to install `uv`.

### Makefile Modifications

```diff
@@ -2,12 +2,20 @@
 
 .ONESHELL:
 venv:
-	python3 -m venv venv
-	source venv/bin/activate && \
-	python -m pip install --upgrade pip setuptools wheel pipenv && \
-	python -m pip install -e .
+	uv venv --python 3.11
+	uv pip install --upgrade pip setuptools wheel pipenv
+	uv pip install -e .
+
+.PHONY: dev
+dev:
+	uv venv --python 3.11
+	uv pip install --upgrade pip setuptools wheel pipenv
+	uv pip install -e .[dev]
 
-# transform
 .PHONY: transform
 transform:
-	message transform
\ No newline at end of file
+	message transform
+
+.PHONY: get-message
+get-message:
+	message get-message $(session_group)
```

### `setup.py` Modifications

```diff
@@ -12,6 +12,16 @@ packages = [
     "pyarrow==14.0.2",
     "SQLAlchemy==1.4.46",
     "typer==0.9.0",
+    "pyyaml"
+]
+
+dev_packages = [
+    "pytest",
+    "mkdocs",
+    "mkdocs-material",
+    "mkdocs-jupyter",
+    "mkdocstrings[python]",
+    *packages,
 ]
 
 setup(
@@ -19,7 +29,7 @@ setup(
     version="0.1.0",
     author="Sword Health",
     author_email="ai@swordhealth.com",
-    python_requires=">=3.8",
+    python_requires=">=3.8, <=3.11",
     packages=find_packages(exclude=("tests", "resources")),
     install_requires=packages,
     entry_points={
@@ -27,4 +37,7 @@ setup(
             "message = message.main:app",
         ],
     },
+    extras_require={
+        "dev": dev_packages,
+    },
 )
```

---

### Documentation

Documentation is powered by mkdocs. Configuration is in [mkdocs.yml](mkdocs.yml).

You can either read the documentation on your browser (using built docs) or read it on your IDE directly from files.

### Building Documentation

To build the documentation to target directory, run:

```bash
mkdocs build
```

### Opening Built Documentation

To open the built documentation you must open the `docs_build/index.html` file on your browser.

On mac:

```bash
open docs_build/index.html
```

### Serving Documentation

To serve the documentation, run:

```bash
mkdocs serve
```
