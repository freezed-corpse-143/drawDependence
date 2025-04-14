// GraphGenerator.cpp
#include "GraphGenerator.h"
#include "Utils.h"
#include <nlohmann/json.hpp>
#include <algorithm>
#include <set>
#include <unordered_set>
#include <filesystem>

nlohmann::json GraphGenerator::standardizeDependencies(const std::unordered_map<std::string, std::vector<std::string>>& internalDependence) {
    std::set<std::string> fileSet;
    for (const auto& [key, values] : internalDependence) {
        fileSet.insert(key);
        for (const std::string& value : values) {
            fileSet.insert(value);
        }
    }

    std::vector<std::string> fileList(fileSet.begin(), fileSet.end());

    std::set<std::string> dirSet;
    for (const std::string& file : fileList) {
        std::vector<std::string> dirs = Utils::extractDirs(file);
        dirSet.insert(dirs.begin(), dirs.end());
    }

    std::vector<std::string> dirList(dirSet.begin(), dirSet.end());
    std::sort(dirList.begin(), dirList.end(), [](const std::string& a, const std::string& b) {
        return a.length() < b.length();
    });

    nlohmann::json nodes = nlohmann::json::array();
    std::unordered_map<std::string, int> comboY;
    for (const std::string& filePath : fileList) {
        nlohmann::json item;
        item["id"] = filePath;
        item["text"] = Utils::getBaseName(filePath);
        item["combo"] = Utils::getDirectory(filePath);
        item["style"]["x"] = 400 + Utils::countSubstrings(item["combo"], std::string(1, std::filesystem::path::preferred_separator)) * 100;
        item["style"]["y"] = 200 + comboY[item["combo"]] * 100;
        comboY[item["combo"]]++;
        nodes.push_back(item);
    }

    std::set<std::pair<int, int>> positionSet;
    for (auto& node : nodes) {
        int x = node["style"]["x"];
        int y = node["style"]["y"];
        bool down = true;
        while (positionSet.find({x, y}) != positionSet.end()) {
            if (down) {
                y += 100;
            } else {
                x += 200;
            }
            down = !down;
        }
        positionSet.insert({x, y});
        node["style"]["x"] = x;
        node["style"]["y"] = y;
    }

    nlohmann::json edges = nlohmann::json::array();
    int index = 0;
    for (const auto& [key, values] : internalDependence) {
        for (const std::string& target : values) {
            nlohmann::json item;
            item["id"] = std::to_string(index++);
            item["source"] = key;
            item["target"] = target;
            edges.push_back(item);
        }
    }

    nlohmann::json combos = nlohmann::json::array();
    for (const std::string& dir : dirList) {
        nlohmann::json item;
        item["id"] = dir;
        std::string parentDir = Utils::getDirectory(dir);
        if (!parentDir.empty()) {
            item["combo"] = parentDir;
        }
        combos.push_back(item);
    }

    nlohmann::json data;
    data["nodes"] = nodes;
    data["edges"] = edges;
    data["combos"] = combos;

    return data;
}