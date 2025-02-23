// FileParser.cpp
#include "FileParser.h"
#include <fstream>
#include <regex>
#include <iostream>
#include <string>

void trim(std::string &str) {
    str.erase(0, str.find_first_not_of(' '));
    
    str.erase(str.find_last_not_of(' ') + 1);
}

std::vector<std::string> FileParser::parseImports(const std::string& filePath) {
    std::vector<std::string> importsList;
    std::ifstream file(filePath);
    std::string line;
    std::regex importPattern(R"((?:from\s+([\w.]+)\s+import\s+([\w.]+(?:,\s*[\w.]+)*)|import\s+([\w.]+(?:,\s*[\w.]+)*)))");

    while (std::getline(file, line)) {
        std::smatch matches;
        if (std::regex_search(line, matches, importPattern)) {
            if (matches[1].matched) {
                std::string module = matches[1];
                std::string items = matches[2];
                size_t pos = 0;
                while ((pos = items.find(',')) != std::string::npos) {
                    std::string item = items.substr(0, pos);
                    trim(item);
                    importsList.push_back(module + "." + item);
                    items.erase(0, pos + 1);
                }
                importsList.push_back(module + "." + items);
            } else {
                std::string items = matches[3];
                size_t pos = 0;
                while ((pos = items.find(',')) != std::string::npos) {
                    std::string item = items.substr(0, pos);
                    trim(item);
                    importsList.push_back(item);
                    items.erase(0, pos + 1);
                }
                importsList.push_back(items);
            }
        }
    }

    return importsList;
}