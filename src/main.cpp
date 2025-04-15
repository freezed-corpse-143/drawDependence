// main.cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include "DependencyAnalyzer.h"
#include "GraphGenerator.h"
#include "Utils.h"

void processSingleFile(const std::string& filePath, const std::string& project_dir) {

    const std::string prefix = R"html(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>G6 Graph Example</title>
  <script src="https://unpkg.com/@antv/g6@5/dist/g6.min.js"></script>
  <style>
    #container {
      width: 100vw;
      height: 100vh;
      border: 1px solid #ccc; /* 可选：为容器添加边框 */
    }
  </style>
</head>
<body>
<div id="container"></div>
<script>
    const data = 
)html";

    const std::string suffix = R"html(

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
</html>)html";

    if (!std::filesystem::exists(filePath)) {
        std::cerr << filePath << " doesn't exist" << std::endl;
        return;
    }
    std::string temp_dir = project_dir;
    if (!temp_dir.empty() && temp_dir.back() == std::filesystem::path::preferred_separator) {
        temp_dir.pop_back();
    }

    auto [externalPackages, internalDependence] = DependencyAnalyzer::analyzeDependencies(filePath, temp_dir);
    std::cout << filePath << " external package: ";
    for (const std::string& package : externalPackages) {
        std::cout << package << " ";
    }
    std::cout << std::endl;

    std::unordered_map<std::string, std::vector<std::string>> newInternalDependence;
    for (const auto& [key, values] : internalDependence) {
        std::string source;
        source = Utils::replace(key, temp_dir, ".");
        for (const std::string& target : values) {
            std::string normalizedTarget = Utils::replace(target, temp_dir, ".");
            newInternalDependence[source].push_back(normalizedTarget);
        }
    }

    nlohmann::json data = GraphGenerator::standardizeDependencies(newInternalDependence);

    std::string templateHtml = prefix + data.dump(4) + suffix;

    std::string outputPath = Utils::replace(filePath, ".py", ".html");
    std::ofstream outputFile(outputPath);
    outputFile << templateHtml;
    outputFile.close();
}

void processDirectory(const std::string& directoryPath) {
    if (!std::filesystem::is_directory(directoryPath)) {
        std::cerr << directoryPath << " is not a directory" << std::endl;
        return;
    }

    for (const auto& entry : std::filesystem::directory_iterator(directoryPath)) {
        if (entry.is_regular_file() && entry.path().extension() == ".py") {
            processSingleFile(entry.path().string(), directoryPath);
        }
    }
}

int main(int argc, char* argv[]) {

    if (argc < 2 || argc > 3) {
        std::cerr << "Usage: " << argv[0] << " <path> [project_dir]" << std::endl;
        std::cerr << "Generate dependency path" << std::endl;
        std::cerr << "Arguments:" << std::endl;
        std::cerr << "  path         Python file or directory path" << std::endl;
        std::cerr << "  project_dir  Optional project directory path" << std::endl;
        return 1;
    }

    std::string path = argv[1];


    if (std::filesystem::is_regular_file(path) && Utils::ends_with(path, ".py")) {
        std::string project_dir;
        if (argc == 3) {
            project_dir = argv[2];
        } else {
            project_dir = std::filesystem::path(path).parent_path().string();
        }
        processSingleFile(path, project_dir);
    } else if (std::filesystem::is_directory(path)) {
        processDirectory(path);
    } else {
        std::cerr << path << " is neither a valid Python file nor a directory" << std::endl;
    }

    return 0;
}