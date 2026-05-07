#include <iostream>
#include <filesystem>
#include <string>
#include <vector>

namespace fs = std::filesystem;

const std::vector<std::string> IGNORE_DIRS = {
    "node_modules", ".git", "venv", "__pycache__", "build"
};

bool is_ignore(const std::string& dirName) {
    for (const auto& ignored : IGNORE_DIRS) {
        if (dirName == ignored) return true;
    }
    return false;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: ./analyzer <repository_path>\n";
        return 1;
    }

    fs::path target_dir = argv[1];

    if (!fs::exists(target_dir) || !fs::is_directory(target_dir)) {
        std::cerr << "Error: Invalid directory path -> " << target_dir << "\n";
        return 1;
    }

    std::cout << "\n> Analyzing Structure for: " << target_dir.filename().string() << "\n";

    auto it = fs::recursive_directory_iterator(target_dir);
    for (; it != fs::recursive_directory_iterator(); ++it) {
        std::string fileName = it->path().filename().string();

        if (it->is_directory() && is_ignore(fileName)) {
            it.disable_recursion_pending();
            continue;
        }

        int depth = it.depth();
        std::string indent(depth * 4, ' '); 
        
        if (it->is_directory()) {
            std::cout << indent << "|-- [" << fileName << "]\n";
        } else {
            std::cout << indent << "|-- " << fileName << "\n";
        }
    }
    return 0;
}