import os

def create_directory_structure():
    # Define directories to create
    directories = [
        "database",
        "datasets",
        "reports",
        "backend",
        "ml_models",
        "agents",
        "utils",
        "frontend",
        "frontend/views",
        "documentation",
        "documentation/mca_report",
        "documentation/research_paper",
        "documentation/presentation",
        "documentation/screenshots"
    ]
    
    print("Initializing BusinessPilotAI Project Directory Structure...")
    
    # Create directories
    for directory in directories:
        path = os.path.join(".", directory)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")
        else:
            print(f"Directory already exists: {path}")
            
    # Create empty __init__.py files in python folders to make them packages
    python_packages = [
        "backend",
        "ml_models",
        "agents",
        "utils"
    ]
    
    for package in python_packages:
        init_file = os.path.join(".", package, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write(f"# {package} package initialization\n")
            print(f"Created file: {init_file}")
            
    print("\nInitialization Complete!")

if __name__ == "__main__":
    create_directory_structure()
