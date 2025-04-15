import os
import re
from collections import  deque, defaultdict
import argparse
import json

prefix = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>G6 Graph Example</title>
  <script src="https://unpkg.com/@antv/g6@5/dist/g6.min.js"></script>
  <style>
    #container {
      /* width: 500px; */
      /* height: 500px; */
      width: 100vw;
      height: 100vh;
      border: 1px solid #ccc; /* 可选：为容器添加边框 */
    }
  </style>
</head>
<body>
<div id="container"></div>
<script>
    const data = '''

suffix = '''

    const graph = new G6.Graph({
        container: 'container',
        width: window.innerWidth,
        height: window.innerHeight, 
        data,
        node: {
            style: {
                labelText: (d) => d.text,
            },
        },
        edge: {
            type: 'line',
            style: {
                endArrow: true
            }
        },
        combo: {
            type: 'rect',
            style: {
                labelText: (d) => d.id,
                padding: 20,
            },
        },
            behaviors: ['drag-element', 'collapse-expand', 'zoom-canvas'],
    });

    graph.render();
</script>
</body>
</html>'''

def parse_imports(py_file_path):
    
    with open(py_file_path, encoding='utf-8') as f:
        code = f.read()
    
    imports_list = []
    
    pattern = r'(?:from\s+([\w.]+)\s+import\s+([\w.]+(?:,\s*[\w.]+)*)|import\s+([\w.]+(?:,\s*[\w.]+)*))'

    matches = re.findall(pattern, code)

    imports_list = []
    for match in matches:
        if match[0]:
            module = match[0]
            for item in match[1].split(','):
                item = item.strip()
                imports_list.append(f'{module}.{item}')
        else:
            for item in match[2].split(','):
                item = item.strip()
                imports_list.append(f'{item}')

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
    
def analyze_dependencies(py_file_path, project_dir):

    queue = deque()
    visited = []
    external_packages = set()
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
            if not package_path:
                package_path = find_package_path(package_name, project_dir)

            if package_path:
                if package_path not in visited:
                    queue.append(package_path)
                py_packages_path[current_py_path].append(package_path)
            else:
                external_packages.add(package_name.split(".")[0])

    return external_packages, py_packages_path

def extract_dirs(path):
    dirs = []
    path = path.rstrip(os.sep)
    while True:
        path = os.path.dirname(path)
        if path == "":
            break
        dirs.append(path)
    return dirs

def standardize_dependencies(internal_dependence):
    file_set = set()
    for key in internal_dependence:
        file_set.add(key)
        for item in internal_dependence[key]:
            file_set.add(item)
    file_list = list(file_set)

    dir_set = set()
    for file in file_list:
        dir_set.update(extract_dirs(file))

    dir_list = sorted(dir_set, key=len)

    nodes = []
    combo_y = defaultdict(int)
    for file_path in file_list:
        item = {
            "id": file_path,
            "text": os.path.basename(file_path),
            "combo": os.path.dirname(file_path)
        }
        style = {
            "x": 400 + len(item['combo'].split(os.sep)) * 100,
            "y": 200 + combo_y[item['combo']] * 100
        }
        combo_y[item['combo']] += 1
        item['style'] = style
        nodes.append(item)
    position_set = set()
    for node in nodes:
        style = node['style']
        down = True
        while (style['x'], style['y']) in position_set:
            if down:
                style['y'] += 100
            else:
                style['x'] += 200
            down = not down
        position_set.add((style['x'], style['y']))

    edges = []
    index = 0
    for key in internal_dependence:
        for target in internal_dependence[key]:
            item = {
                "id": str(index),
                "source": key,
                "target": target
            }
            index += 1
            edges.append(item)

    combos = []
    for dir in dir_list:
        item = {
            "id": dir
        }
        parent_dir = os.path.dirname(dir)
        if parent_dir != "":
            item['combo'] = parent_dir
        combos.append(item)

    data = {
        "nodes": nodes,
        "edges": edges,
        "combos": combos
    }
    return data


def process_single_file(file_path, project_dir):
    if not os.path.exists(file_path):
        print(f"{file_path} doesn't exist")
        return

    if project_dir.endswith(os.sep):
        project_dir =project_dir[:-1]

    
    external_package, internal_dependence =  analyze_dependencies(file_path, project_dir)
    print(f"{file_path} external package", external_package)

    new_internal_dependence = defaultdict(list)

    for key in internal_dependence:
        source = key.replace(project_dir, ".")
        for target in internal_dependence[key]:
            target = target.replace(project_dir, ".")
            new_internal_dependence[source].append(target)

    data = standardize_dependencies(new_internal_dependence)

    template_html =prefix + json.dumps(data, indent=4) + suffix
    
    output_path = file_path.replace(".py", ".html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_html)

def process_directory(directory_path, project_dir):
    if not os.path.isdir(directory_path):
        print(f"{directory_path} is not a directory")
        return

    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path) and item_path.endswith('.py'):
            process_single_file(item_path, project_dir)

def main():
    parser = argparse.ArgumentParser(description="Generate dependency path")
    parser.add_argument("path", type=str, help="Python file or directory path")
    parser.add_argument("project_dir", type=str, nargs='?', default=None,
                       help="Optional project directory path (positional argument)")

    args = parser.parse_args()
    path = args.path
    project_dir = args.project_dir

    if os.path.isfile(path) and path.endswith('.py'):
        if not project_dir:
            project_dir = os.path.dirname(path)
        process_single_file(path, project_dir)
    elif os.path.isdir(path):
        if not project_dir:
            project_dir = path
        process_directory(path, project_dir)
    else:
        print(f"{path} is neither a valid Python file nor a directory")

if __name__ == "__main__":
    main()