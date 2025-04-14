// DependencyAnalyzer.cpp
#include "DependencyAnalyzer.h"
#include "FileParser.h"
#include "Utils.h"
#include <queue>
#include <unordered_set>
#include <unordered_map>

std::pair<std::unordered_set<std::string>, std::unordered_map<std::string, std::vector<std::string>>> DependencyAnalyzer::analyzeDependencies(const std::string& filePath, const std::string& project_dir) {
    std::queue<std::string> queue;
    std::unordered_set<std::string> visited;
    std::unordered_set<std::string> externalPackages;
    std::unordered_map<std::string, std::vector<std::string>> pyPackagesPath;

    queue.emplace(filePath);

    while (!queue.empty()) {
        std::string currentPyPath = queue.front();
        queue.pop();
        if (visited.find(currentPyPath) != visited.end()) {
            continue;
        }
        visited.insert(currentPyPath);

        std::vector<std::string> importsList = FileParser::parseImports(currentPyPath);

        if (pyPackagesPath.find(currentPyPath) == pyPackagesPath.end()) {
            pyPackagesPath[currentPyPath] = std::vector<std::string>();
        }

        for (const std::string& packageName : importsList) {
            std::string directory = Utils::getDirectory(currentPyPath);
            std::string packagePath = Utils::findPackagePath(packageName, directory);

            if(packagePath.empty()){
                packagePath = Utils::findPackagePath(packageName, project_dir);
            }

            if (!packagePath.empty()) {
                if (visited.find(packagePath) == visited.end()) {
                    queue.emplace(packagePath);
                }
                pyPackagesPath[currentPyPath].emplace_back(packagePath);
            } else {
                externalPackages.insert(packageName.substr(0, packageName.find('.')));
            }
        }
    }

    return {externalPackages, pyPackagesPath};
}