# Python Dependency Graph Generator

This project provides a Python script to analyze and visualize the dependencies of a Python file. It generates an interactive graph using the G6 library to display the relationships between different modules and packages.

## Features

- **Dependency Analysis**: Parses a Python file to extract import statements and identifies both internal and external dependencies.
- **Graph Visualization**: Generates an interactive graph to visualize the dependencies.
- **Customizable Output**: Outputs an HTML file with the dependency graph, which can be viewed in any web browser.

## Requirements

- Python 3.x
- `argparse` module
- `ast` module
- `os` module
- `re` module
- `collections` module
- `json` module
- `importlib` module

## Installation

1. Clone the repository or download the script files.
2. Ensure you have Python 3.x installed on your system.
3. Install the required Python modules if not already installed.

## Usage

1. Place the `drawDependence.py` and `template.html` files in your project directory.
2. Run the script with the following command:

   ```bash
   python drawDependence.py path/to/your/python_file.py
	```

3. The script will generate an HTML file in the `./output` directory with the same name as your Python file but with a `.html` extension.
4. Open the generated HTML file in a web browser to view the dependency graph.

## Example

Given a Python file `example.py`, running the script:

```bash
python drawDependence.py example.py
```

will generate `example.html` in the `./output` directory. Open `example.html` to see the dependency graph.

## Customization

You can customize the appearance of the graph by modifying the `template.html` file. The graph is rendered using the G6 library, so you can refer to the [G6 documentation](https://g6.antv.vision/en) for more advanced customization options.

## Acknowledgments

- [G6](https://g6.antv.vision/en) for the graph visualization library.
- Python's standard libraries for making this project possible.

