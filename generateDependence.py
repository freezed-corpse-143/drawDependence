import os
import ast
from importlib import import_module
import re
from collections import  deque
import argparse
import json

def parse_imports(py_file_path):
    with open(py_file_path, encoding='utf-8') as f:
        code = f.read()
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(e)
        raise e
    imports_list = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in imports_list:
                    imports_list.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if node.module + "." + alias.name not in imports_list:
                    imports_list.append(node.module + "." + alias.name)
    return imports_list

def find_package_path(package_name, directory):
    parts = package_name.split(".")
    first_part = parts[0]
    base_path = os.path.join(directory, first_part)
    module_path = f"{base_path}.py"
    
    if os.path.isfile(module_path):
        return module_path

    init_file_path = os.path.join(directory, "__init__.py")
    if os.path.isfile(init_file_path):
        with open(init_file_path, "r", encoding='utf-8') as file:
            content = file.read()
        pattern = re.compile(r"from\s+\.(\w+)\s+import\s+(\w+)(\s+as\s+(\w+))?")
        matches = pattern.findall(content)
        
        for match in matches:
            xxx, yyy, _, zzz = match
            search_path = os.path.join(directory, xxx)
            
            if not zzz:
                if os.path.isfile(f"{search_path}.py"):
                    return f"{search_path}.py"
                elif os.path.isdir(search_path):
                    return find_package_path(package_name, search_path)
            
            elif zzz == first_part:
                new_package_name = ".".join([yyy] + parts[1:])
                if os.path.isfile(f"{search_path}.py"):
                    return f"{search_path}.py"
                elif os.path.isdir(search_path):
                    return find_package_path(new_package_name, search_path)
    
    if os.path.isdir(base_path):
        if len(parts) == 1:
            raise Exception("please replace 'import module' with a specific one.")
        else:
            new_package_name = ".".join(parts[1:])
            return find_package_path(new_package_name, base_path)
    
    return ""

def is_package_installed(package_name):
    try:
        import_module(package_name)
        return True
    except ImportError:
        return False
    
def analyze_dependencies(py_file_path):

    queue = deque()
    visited = []
    external_packages = []
    unfound_packages = []
    py_packages_path = {}


    queue.append(py_file_path)


    while queue:
        current_py_path = queue.popleft()
        if current_py_path in visited:
            continue
        visited.append(current_py_path)


        imports_list = parse_imports(current_py_path)


        if current_py_path not in py_packages_path:
            py_packages_path[current_py_path] = []


        for package_name in imports_list:
            directory = os.path.dirname(current_py_path)
            package_path = find_package_path(package_name, directory)

            if package_path:
                if package_path not in visited:
                    queue.append(package_path)
                py_packages_path[current_py_path].append(package_path)
            else:
                if is_package_installed(package_name):
                    if package_name not in external_packages:
                        external_packages.append(package_name)
                else:
                    if package_name not in unfound_packages:
                        unfound_packages.append(package_name)

    return external_packages, unfound_packages, py_packages_path

def main():
    parser = argparse.ArgumentParser(description="generate dependence path")
    parser.add_argument("py_path", type=str, required=True, help="python file path")
    args = parser.parse_args()

    if not os.path.exists(args.py_path):
        print(f"{args.py_path} doesn't exist")
        return
    
    internal_rependence =  analyze_dependencies(args.py_path)[2]

    edges = []
    for key in internal_rependence:
        if len(internal_rependence[key]) == 0:
            continue
        print(f"{key}\t-->\t{target}")
        for target in internal_rependence[key]:
            edges.append({
                "source": key,
                "target": target
            })
    
    with open(f"{args.py_path.replace(".py", ".json")}", 'w', encoding='utf-8') as f:
        json.dump(edges, f)


if __name__ == "__main__":
    main()