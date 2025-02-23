// Utils.cpp
#include "Utils.h"
#include <filesystem>
#include <algorithm>
#include <fstream>
#include <regex>


std::string Utils::findPackagePath(const std::string& packageName, const std::string& directory) {
    namespace fs = std::filesystem;

    std::vector<std::string> parts;
    size_t start = 0;
    size_t end = packageName.find('.');
    while (end != std::string::npos) {
        parts.push_back(packageName.substr(start, end - start));
        start = end + 1;
        end = packageName.find('.', start);
    }
    parts.push_back(packageName.substr(start));

    std::string firstPart = parts[0];
    std::string basePath = (fs::path(directory) / firstPart).string();

    std::string modulePath = basePath + ".py";
    if (fs::is_regular_file(modulePath)) {
        return modulePath;
    }

    std::string initFilePath = (fs::path(directory) / "__init__.py").string();
    if (fs::is_regular_file(initFilePath)) {
        std::ifstream initFile(initFilePath);
        std::string content((std::istreambuf_iterator<char>(initFile)), std::istreambuf_iterator<char>());

        std::regex pattern(R"(from\s+\.(\w+)\s+import\s+(\w+)(\s+as\s+(\w+))?)");
        std::smatch matches;
        std::string::const_iterator searchStart(content.cbegin());

        while (std::regex_search(searchStart, content.cend(), matches, pattern)) {
            std::string xxx = matches[1];
            std::string yyy = matches[2];
            std::string zzz = matches[4];

            std::string searchPath = (fs::path(directory) / xxx).string();

            if (zzz.empty()) {
                if (fs::is_regular_file(searchPath + ".py")) {
                    return searchPath + ".py";
                } else if (fs::is_directory(searchPath)) {
                    return findPackagePath(packageName, searchPath);
                }
            } else if (zzz == firstPart) {
                std::string newPackageName = yyy;
                for (size_t i = 1; i < parts.size(); ++i) {
                    newPackageName += "." + parts[i];
                }

                if (fs::is_regular_file(searchPath + ".py")) {
                    return searchPath + ".py";
                } else if (fs::is_directory(searchPath)) {
                    return findPackagePath(newPackageName, searchPath);
                }
            }

            searchStart = matches.suffix().first;
        }
    }

    if (fs::is_directory(basePath)) {
        if (parts.size() == 1) {
            throw std::runtime_error("please replace 'import module' with a specific one.");
        } else {
            std::string newPackageName;
            for (size_t i = 1; i < parts.size(); ++i) {
                newPackageName += parts[i];
                if (i < parts.size() - 1) {
                    newPackageName += ".";
                }
            }
            return findPackagePath(newPackageName, basePath);
        }
    }

    return "";
}

std::string Utils::normalizePath(const std::string& path) {
    std::string normalizedPath = path;
    std::replace(normalizedPath.begin(), normalizedPath.end(), '\\', '/');
    return normalizedPath;
}

std::string Utils::replace(const std::string& str, const std::string& from, const std::string& to) {
    std::string result = str;
    size_t start_pos = 0;
    while ((start_pos = result.find(from, start_pos)) != std::string::npos) {
        result.replace(start_pos, from.length(), to);
        start_pos += to.length();
    }
    return result;
}

std::string Utils::getDirectory(const std::string& filePath) {
    return std::filesystem::path(filePath).parent_path().string();
}

std::string Utils::getBaseName(const std::string& path) {
    return std::filesystem::path(path).filename().string();
}

std::vector<std::string> Utils::extractDirs(const std::string& path) {
    std::vector<std::string> dirs;
    std::string normalizedPath = normalizePath(path);
    if(normalizedPath.back() == '/'){
        normalizedPath.pop_back();
    }
    std::string currentPath = normalizedPath;
    while (true) {
        currentPath = std::filesystem::path(currentPath).parent_path().string();
        if (currentPath.empty()) {
            break;
        }
        dirs.push_back(currentPath);
    }
    return dirs;
}

int Utils::countSubstrings(const std::string& str, const std::string& substr) {
    int count = 0;
    size_t pos = 0;
    while ((pos = str.find(substr, pos)) != std::string::npos) {
        count++;
        pos += substr.length();
    }
    return count;
}

bool Utils::ends_with(const std::string& str, const std::string& suffix) {
    return str.size() >= suffix.size() && 
           str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
}