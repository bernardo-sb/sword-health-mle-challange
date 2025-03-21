# SWORD Health MLE Challange - Bernardo Costa

I started by reading the README.md file and go over the instructions and project.

I unzipped and inspected the data files in the `data` directory.

Then I tried setting up my environment but ran into version conflicts since my system was running Python 3.13. I addressed this issue by changing the `Makefile` to use Python 3.11 and used `uv` as the package manager. In addition, I added `pytest` to the `dev` extra in the `setup.py` file, and created a `dev` target in the `Makefile`.

To install uv, follow the instructions in the [uv](https://github.com/astral-sh/uv) repository.

**Makefile diff:**
```diff
--- a/Makefile
+++ b/Makefile
@@ -2,10 +2,15 @@
 
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
 
 # transform
 .PHONY: transform
 ```

 **setup.py diff:**
 
```diff
--- a/setup.py
+++ b/setup.py
@@ -14,12 +14,16 @@ packages = [
     "typer==0.9.0",
 ]
 
+dev_packages = [
+    "pytest",
+]
+
 setup(
     name="message",
     version="0.1.0",
     author="Sword Health",
     author_email="ai@swordhealth.com",
-    python_requires=">=3.8",
+    python_requires=">=3.8, <=3.11",
     packages=find_packages(exclude=("tests", "resources")),
     install_requires=packages,
     entry_points={
@@ -27,4 +31,7 @@ setup(
             "message = message.main:app",
         ],
     },
+    extras_require={
+        "dev": dev_packages,
+    },
 )
diff --git a/setup.py b/setup.py
index 283eb80..c073711 100644
--- a/setup.py
+++ b/setup.py
@@ -14,12 +14,17 @@ packages = [
     "typer==0.9.0",
 ]
 
+dev_packages = [
+    "pytest",
+    *packages,
+]
+
 setup(
     name="message",
     version="0.1.0",
     author="Sword Health",
     author_email="ai@swordhealth.com",
-    python_requires=">=3.8",
+    python_requires=">=3.8, <=3.11",
     packages=find_packages(exclude=("tests", "resources")),
     install_requires=packages,
     entry_points={
@@ -27,4 +32,7 @@ setup(
             "message = message.main:app",
         ],
     },
+    extras_require={
+        "dev": dev_packages,
+    },
 )
```

---

Question 1

- There seems to be some values mismatches in provided expected and input.
- Input does not contain records in the output; differente samples