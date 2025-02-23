# Dependency Visualization Tool

This tool is designed to visualize the dependencies of Python files within a project. It generates an interactive HTML graph using the G6 library to represent the dependencies between different Python modules.

## Features

- **Dependency Analysis**: Parses Python files to extract import statements and identifies both internal and external dependencies.
- **Interactive Graph**: Generates an interactive HTML graph that visualizes the dependencies between modules.
- **Directory Support**: Can process a single Python file or an entire directory of Python files.

## Usage

### Prerequisites

- Python 3.x
- Required Python packages (if any) should be installed.

### Running the Tool

You can run the tool using either the Python script or the provided executable.

#### Using Python Script

1. Navigate to the directory containing the `drawDependence.py` script.
2. Run the script with the following command:

   ```bash
   python drawDependence.py <path_to_python_file_or_directory>
   ```

   Replace `<path_to_python_file_or_directory>` with the path to the Python file or directory you want to analyze.

#### Using Executable

1. Ensure that `drawDependence.exe` is in your project directory.
2. Run the executable with the following command:

   ```bash
   drawDependence.exe <path_to_python_file_or_directory>
   ```

   Replace `<path_to_python_file_or_directory>` with the path to the Python file or directory you want to analyze.

### Output

The tool will generate an HTML file for each Python file processed. The HTML file will be named the same as the Python file but with a `.html` extension. For example, if you process `example.py`, the output will be `example.html`.

The generated HTML file contains an interactive graph that visualizes the dependencies between the modules in your project.

## Example

Suppose you have a Python file `example.py` with the following content:

```python
import os
from utils.helper import some_function
import numpy as np
```

Running the tool on `example.py` will generate an HTML file `example.html` that visualizes the dependencies between `example.py`, `utils/helper.py`, and the external package `numpy`.

## Notes

- The tool currently supports standard Python import statements.
- External packages are identified but not visualized in the graph.
- The graph layout is automatically generated, and nodes may overlap if there are many dependencies. You can manually adjust the positions in the generated HTML file if needed.
