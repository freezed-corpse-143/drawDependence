// Utils.h
#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <vector>

class Utils {
public:
    static std::string findPackagePath(const std::string& packageName, const std::string& directory);
    static std::string replace(const std::string& str, const std::string& from, const std::string& to);
    static std::string getDirectory(const std::string& filePath);
    static std::string getBaseName(const std::string& path);
    static std::vector<std::string> extractDirs(const std::string& path);
    static int countSubstrings(const std::string& str, const std::string& substr);
    static bool ends_with(const std::string& str, const std::string& suffix);
};

#endif // UTILS_H