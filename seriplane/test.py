import os
import ast

PROJECT_DIR = "."

stdlib = set([
    "os","sys","math","time","datetime","json","csv","re","glob",
    "argparse","logging","pathlib","itertools","collections","random",
    "subprocess","threading","multiprocessing"
])

deps = set()

for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=path)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            pkg = n.name.split(".")[0]
                            if pkg not in stdlib:
                                deps.add(pkg)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            pkg = node.module.split(".")[0]
                            if pkg not in stdlib:
                                deps.add(pkg)

            except Exception as e:
                print(f"Skipped {path}: {e}")

print("\n📦 External Dependencies Found:\n")
for d in sorted(deps):
    print(d)
