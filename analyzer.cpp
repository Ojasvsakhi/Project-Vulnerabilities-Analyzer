#include <iostream>
#include <filesystem>
#include <string>
#include <vector>
#include <sstream>

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

    std::vector<std::string> files_to_analyze;
    
    std::stringstream tree_builder;
    tree_builder << "\n> Analyzing Structure for: " << target_dir.filename().string() << "\n";

    auto it = fs::recursive_directory_iterator(target_dir);
    for (; it != fs::recursive_directory_iterator(); ++it) {
        std::string fileName = it->path().filename().string();

        if (it->is_directory() && is_ignore(fileName)) {
            it.disable_recursion_pending();
            continue;
        }

        if (it->is_regular_file()) {
            files_to_analyze.push_back(it->path().string());
        }

        int depth = it.depth();
        std::string indent(depth * 4, ' '); 
        
        if (it->is_directory()) {
            tree_builder << indent << "|-- [" << fileName << "]\n";
        } else {
            tree_builder << indent << "|-- " << fileName << "\n";
        }
    }
    
    std::cout << tree_builder.str();
    std::cout << "\n> [SYSTEM MESSAGE] Successfully queued " 
              << files_to_analyze.size() << " files for deep LLVM analysis.\n";
    return 0;
}