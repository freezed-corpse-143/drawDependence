// GraphGenerator.h
#ifndef GRAPHGENERATOR_H
#define GRAPHGENERATOR_H

#include <string>
#include <vector>
#include <unordered_map>
#include <nlohmann/json.hpp>

class GraphGenerator {
public:
    static nlohmann::json standardizeDependencies(const std::unordered_map<std::string, std::vector<std::string>>& internalDependence);
};

#endif // GRAPHGENERATOR_H