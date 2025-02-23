// DependencyAnalyzer.h
#ifndef DEPENDENCYANALYZER_H
#define DEPENDENCYANALYZER_H

#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <queue>

class DependencyAnalyzer {
public:
    static std::pair<std::unordered_set<std::string>, std::unordered_map<std::string, std::vector<std::string>>> analyzeDependencies(const std::string& filePath);
};

#endif // DEPENDENCYANALYZER_H