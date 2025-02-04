# generateDependence.py

This script analyzes the dependencies of a Python file and generates a JSON file representing the dependency graph.

## Usage

To use this script, run the following command in your terminal:

```bash
python generateDependence.py <python_file_path>
```

Replace `<python_file_path>` with the path to the Python file you want to analyze.

## Output

The script will generate a JSON file with the same name as the input Python file but with a `.json` extension. This JSON file contains a list of edges representing the dependencies between the Python files. Each edge has a `source` and a `target` field, indicating the dependency relationship.

## Example

Given a Python file `example.py`, running the script:

```bash
python generateDependence.py example.py
```

Will generate a `example.json` file with content similar to:

```json
[
    {"source": "example.py", "target": "module1.py"},
    {"source": "example.py", "target": "module2.py"},
    {"source": "module1.py", "target": "module3.py"}
]
```

This indicates that `example.py` depends on `module1.py` and `module2.py`, and `module1.py` further depends on `module3.py`.

