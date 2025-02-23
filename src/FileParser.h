// FileParser.h
#ifndef FILEPARSER_H
#define FILEPARSER_H

#include <vector>
#include <string>

class FileParser {
public:
    static std::vector<std::string> parseImports(const std::string& filePath);
};

#endif // FILEPARSER_H