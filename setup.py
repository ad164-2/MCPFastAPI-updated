"""
Project Setup Script
====================
This script creates the project file and folder structure from an embedded JSON definition.
Run this script to automatically generate all necessary directories and empty files.

Usage:
    python setup.py

The project structure is defined in the PROJECT_STRUCTURE dictionary below.
You can modify it to customize your project structure.
"""

import os
import json
from pathlib import Path
from typing import Dict

# ============================================================================
# PROJECT STRUCTURE DEFINITION
# ============================================================================
# Modify this structure to customize your project layout
# Format:
#   - "files": List of file names to create (empty files)
#   - "directories": Dict of subdirectories with their own files and directories
# ============================================================================

PROJECT_STRUCTURE = {
    "files": [
        "main.py",
        "requirements.txt",
        ".env",
        "pyproject.toml",
        ".gitignore"
    ],
    "directories": {
        "app": {
            "files": ["__init__.py", "app.py"],
            "directories": {
                "core": {
                    "files": ["__init__.py"],
                    "directories": {
                        "base": {
                            "files": ["__init__.py", "entity.py", "repository.py"],
                            "directories": {}
                        },
                        "config": {
                            "files": ["__init__.py", "settings.py", "observability_config.py"],
                            "directories": {}
                        },
                        "database": {
                            "files": ["__init__.py", "database.py"],
                            "directories": {}
                        },
                        "utils": {
                            "files": ["__init__.py", "exceptions.py", "logger.py", "observability.py"],
                            "directories": {}
                        }
                    }
                },
                "features": {
                    "files": ["__init__.py"],
                    "directories": {
                        "auth": {
                            "files": ["__init__.py", "auth_route.py", "auth_schemas.py", "auth_utils.py", "jwt.py"],
                            "directories": {}
                        },
                        "users": {
                            "files": ["__init__.py", "users_route.py", "user_entity.py", "user_repository.py", "test_user_repository.py", "test_user_route.py"],
                            "directories": {}
                        },
                        "chat": {
                            "files": ["__init__.py", "chat_entity.py", "chat_repository.py", "chat_route.py", "chat_schemas.py"],
                            "directories": {}
                        },
                        "documents": {
                            "files": ["__init__.py", "router.py", "schemas.py", "service.py"],
                            "directories": {}
                        }
                    }
                },
                "llm_functions": {
                    "files": ["AgentGraph.py", "AgentLLM.py", "AgentState.py", "LLMCall.py", "LLMDefination.py", "MCPHelper.py", "mcp_config.json", "RAGHelper.py", "ToolHelper.py"],
                    "directories": {
                        "tools": {
                            "files": ["current_date.py", "google_search.py", "sqlite_tool.py"],
                            "directories": {}
                        },
                        "tools2": {
                            "files": ["current_date.py", "google_search.py", "sqlite_tool.py", "toolsconfig.py"],
                            "directories": {}
                        }
                    }
                },
                "middleware": {
                    "files": ["__init__.py", "auth_middleware.py"],
                    "directories": {}
                }
            }
        }
    }
}


class ProjectSetup:
    """Project setup utility class."""
    
    def __init__(self, base_path: str = "."):
        """Initialize project setup."""
        self.base_path = Path(base_path)
        self.structure = PROJECT_STRUCTURE
        self.created_files = 0
        self.created_dirs = 0
        self.skipped_files = 0
        self.skipped_dirs = 0
    
    def create_file(self, file_path: Path):
        """Create an empty file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.touch()
                self.created_files += 1
                print(f"  ✓ Created file: {file_path.relative_to(self.base_path)}")
            else:
                self.skipped_files += 1
                print(f"  ⊙ File exists: {file_path.relative_to(self.base_path)}")
        except Exception as e:
            print(f"  ✗ Error creating file {file_path}: {e}")
    
    def create_directory(self, dir_path: Path):
        """Create a directory."""
        try:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.created_dirs += 1
                print(f"  ✓ Created directory: {dir_path.relative_to(self.base_path)}")
            else:
                self.skipped_dirs += 1
                print(f"  ⊙ Directory exists: {dir_path.relative_to(self.base_path)}")
        except Exception as e:
            print(f"  ✗ Error creating directory {dir_path}: {e}")
    
    def process_structure(self, structure: Dict, current_path: Path):
        """Recursively process the structure dictionary."""
        # Create files at current level
        if "files" in structure:
            for filename in structure["files"]:
                file_path = current_path / filename
                self.create_file(file_path)
        
        # Process subdirectories
        if "directories" in structure:
            for dirname, substructure in structure["directories"].items():
                dir_path = current_path / dirname
                self.create_directory(dir_path)
                self.process_structure(substructure, dir_path)
    
    def setup(self):
        """Run the complete setup."""
        print("=" * 70)
        print("🚀 MCPFastAPI Project Structure Setup")
        print("=" * 70)
        print()
        
        # Process root files
        print("📄 Creating root files...")
        if "files" in self.structure:
            for filename in self.structure["files"]:
                file_path = self.base_path / filename
                self.create_file(file_path)
        
        print()
        print("📁 Creating directories and files...")
        
        # Process directories
        if "directories" in self.structure:
            for dirname, substructure in self.structure["directories"].items():
                dir_path = self.base_path / dirname
                self.create_directory(dir_path)
                self.process_structure(substructure, dir_path)
        
        print()
        print("=" * 70)
        print(f"✅ Setup completed successfully!")
        print(f"   📊 Created: {self.created_dirs} directories, {self.created_files} files")
        print(f"   ⊙ Skipped: {self.skipped_dirs} directories, {self.skipped_files} files (already exist)")
        print("=" * 70)
        print()
        print("📝 Next steps:")
        print("   1. Create virtual environment: python -m venv .venv")
        print("   2. Activate it:")
        print("      - Windows: .venv\\Scripts\\activate")
        print("      - Unix/MacOS: source .venv/bin/activate")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Configure .env file")
        print("   5. Run: python main.py")
        print()
    
    def show_structure(self):
        """Display the project structure in a tree format."""
        print("=" * 70)
        print("📋 Project Structure Preview")
        print("=" * 70)
        print()
        print(json.dumps(self.structure, indent=2))
        print()
    
    def export_json(self, output_file: str = "project_structure.json"):
        """Export the structure to a JSON file."""
        output_path = self.base_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.structure, f, indent=2)
        print(f"✓ Exported structure to: {output_path}")
        print(f"  You can edit this file and modify the PROJECT_STRUCTURE in setup.py")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup FastAPI project structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py                      # Create structure in current directory
  python setup.py --path ./new_project # Create in specific directory
  python setup.py --show               # Show structure without creating
  python setup.py --export             # Export structure to JSON file
  
The project structure is defined in the PROJECT_STRUCTURE dictionary
at the top of this file. Edit it to customize your project layout.
        """
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Base path for project setup (default: current directory)"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the project structure without creating files"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export structure to project_structure.json"
    )
    
    args = parser.parse_args()
    
    setup = ProjectSetup(args.path)
    
    if args.show:
        setup.show_structure()
    elif args.export:
        setup.export_json()
    else:
        setup.setup()


if __name__ == "__main__":
    main()
