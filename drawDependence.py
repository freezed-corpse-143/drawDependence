import ast
import os
import json
import sys

def parse_python_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    result = {
        "import": [],
        "from_import": [],
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["import"].append((alias.name, alias.asname))
        
        elif isinstance(node, ast.ImportFrom):
            level = node.level
            module_parts = []
            
            if node.module:
                module_parts = node.module.split('.')
            
            full_module = []
            if level > 0:
                full_module.extend(['<parent>'] * (level - 1))
            full_module.extend(module_parts)
            
            base_module = '.'.join(full_module)
            
            for alias in node.names:
                if not node.module:
                    result['from_import'].append(( "", alias.name, alias.asname))
                else:
                    result['from_import'].append((base_module, alias.name, alias.asname))
    
    return result


def get_py_files(directory):
    py_files = []
    base_dir = os.path.abspath(directory)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.abspath(os.path.join(root, file))
                py_files.append(os.path.join('.', full_path))
    
    return py_files


def get_import_entrances(file_path):
    result = []
    parse_result = parse_python_imports(file_path)
    for item in parse_result['import']:
        result.append(item[0])
    for item in parse_result['from_import']:
        result.append(f"{item[0]}.{item[1]}")
    return list(set(result))

def extract_node(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        source = file.read()
    
    tree = ast.parse(source)
    
    result = []
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result.append( target.id)
        elif isinstance(node, ast.FunctionDef):
            result.append(node.name)
        elif isinstance(node, ast.ClassDef):
            result.append(node.name)
    return result

def find_reference_path(entrance, dir):
    if not entrance:
        return None
    if entrance.startswith("<parent>"):
        return find_reference_path(entrance[8:], os.path.dirname(dir))
    if entrance.startswith("."):
        entrance = entrance[1:]
    result = None
    parts = entrance.split(".")
    first_part = parts[0]

    py_path = os.path.join(dir, f"{first_part}.py")
    if os.path.exists(py_path):
        return py_path
    
    sub_dir = os.path.join(dir, first_part)
    if os.path.exists(sub_dir):
        result = find_reference_path(".".join(parts[1:]) , sub_dir) 
        if result:
            return result
    # __init__.py doesn't exist
    init_py_path = os.path.join(dir, "__init__.py")
    if not os.path.exists(init_py_path):
        return result
    
    node_name_list = extract_node(init_py_path)
    if len(parts) == 1 and first_part in node_name_list:
        return init_py_path
    
    init_import_result = parse_python_imports(init_py_path)
    for item in init_import_result['from_import']:
        # from A import B as C
        if item[2] and first_part == item[2]:
            new_first_part = f"{item[0]}.{item[1]}"
            new_entrance = ".".join([new_first_part] + parts[1:])
            result = find_reference_path(new_entrance, dir)
            if result:
                return result
            continue
        # from A import B
        if not item[2] and first_part == item[1]:
            new_entrance = ".".join([item[0]] + parts[1:])
            result = find_reference_path(new_entrance, dir)
            if result:
                return result
    return result

def analyze_single_file(file_path, project_dir):
    file_dir = os.path.dirname(file_path)
    external_packages = set()
    reference_py_path_list = []

    entrance_list = get_import_entrances(file_path)
    for entrance in entrance_list:
        reference_py_path = find_reference_path(entrance, file_dir)
        if not reference_py_path:
            reference_py_path = find_reference_path(entrance, project_dir)
        if reference_py_path:
            reference_py_path_list.append(reference_py_path.replace(project_dir, "."))
        else:
            external_packages.add(entrance)
    return external_packages, reference_py_path_list

def extract_dirs(path):
    dirs = []
    path = path.rstrip(os.sep)
    while True:
        path = os.path.dirname(path)
        if path == "":
            break
        dirs.append(path)
    return dirs


prefix = '''
<!DOCTYPE html>
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
</html>
'''

def visualize_dependence(internal_dependence):
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
    combo_y = dict()
    for file_path in file_list:
        
        item = {
            "id": file_path,
            "text": os.path.basename(file_path),
            "combo": os.path.dirname(file_path)
        }
        if item['combo'] not in combo_y:
            combo_y[item['combo']] = 0
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

    template_html = prefix + json.dumps(data, indent=4) + suffix
    return template_html

def analyze_project(project_dir):
    external_packages = set()
    internal_dependence = dict()
    
    py_files = get_py_files(project_dir)
    for file_path in py_files:
        py_external_packages, py_reference_py_path_list = analyze_single_file(file_path, project_dir)
        external_packages.update(py_external_packages)
        if py_reference_py_path_list:
            internal_dependence[file_path.replace(project_dir, ".")] = py_reference_py_path_list
    print("external packages: ", sorted(external_packages))
    # print(json.dumps(internal_dependence, indent=4))
    template_html = visualize_dependence(internal_dependence)
    with open(os.path.join(project_dir, "dependence.html"), 'w', encoding='utf-8') as f:
        f.write(template_html)

def traversal_from_sample_file(file_path, project_dir=None):
    if not project_dir:
        project_dir = os.path.dirname(file_path)
    external_packages = set()
    internal_dependence = dict()
    output_path = file_path.replace(".py", ".html")
    
    queue = [file_path]
    visited = set()
    while len(queue) > 0 :
        file = queue.pop(0)
        visited.add(file)
        py_external_packages, py_reference_py_path_list = analyze_single_file(file, project_dir)
        external_packages.update(py_external_packages)
        if py_reference_py_path_list:
            internal_dependence[file.replace(project_dir, ".")] = py_reference_py_path_list
            for ref_py_path in py_reference_py_path_list:
                ref_py_path = project_dir+ ref_py_path[1:]
                if ref_py_path not in visited:
                    # print(project_dir, ref_py_path)
                    queue.append(ref_py_path)
    print("external packages: ", sorted(external_packages))
    # print(json.dumps(internal_dependence, indent=4))
    template_html = visualize_dependence(internal_dependence)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_html)


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 3:
        print("one or two parameters")
        return 
    
    path1 = sys.argv[1]
    if len(sys.argv) == 2:
        # Single argument case
        if os.path.isdir(path1):
            analyze_project(path1)
        elif os.path.isfile(path1) and path1.endswith('.py'):
            traversal_from_sample_file(path1)
        else:
            print("Invalid path or file type. Please provide a directory or .py file.")
    elif len(sys.argv) == 3:
        path2 = sys.argv[2]
        if os.path.isfile(path1) and path1.endswith('.py') and os.path.isdir(path2):
            # File + directory case
            traversal_from_sample_file(path1, path2)
        elif os.path.isdir(path1) and os.path.isdir(path2):
            # Directory + directory case - process all .py files in first directory
            for file in os.listdir(path1):
                if file.endswith('.py'):
                    file_path = os.path.join(path1, file)
                    traversal_from_sample_file(file_path, path2)
        else:
            print("Invalid combination of arguments.")
            print("For two arguments, provide either:")
            print("1. A .py file followed by a project directory")
            print("2. Two directories (will process .py files in first directory)")
    else:
        print("Too many arguments. Maximum 2 arguments supported.")

if __name__ == "__main__":
    main()