
# gitingest.py (real repository ingestion)
import os
import git

def ingest(repo_url, local_dir="repos"):
    """
    Ingests a GitHub repository and returns summary, tree, and content.
    
    Args:
        repo_url (str): GitHub repository URL.
        local_dir (str): Local directory to clone repositories.

    Returns:
        tuple: (summary, tree, content)
    """
    repo_name = repo_url.strip().split("/")[-1]
    path = os.path.join(local_dir, repo_name)

    # Create local_dir if it doesn't exist
    os.makedirs(local_dir, exist_ok=True)

    # Clone repo if not already cloned
    if not os.path.exists(path):
        print(f"Cloning repository {repo_url}...")
        git.Repo.clone_from(repo_url, path)
    else:
        print(f"Repository already exists at {path}, using existing copy.")

    # Read README.md as summary if it exists
    summary = ""
    readme_files = ["README.md", "README.MD", "readme.md"]
    for rf in readme_files:
        readme_path = os.path.join(path, rf)
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                summary = f.read()
            break

    if not summary:
        summary = "No README found in this repository."

    # Build repository tree and concatenate content
    tree = ""
    content = ""
    for root, dirs, files in os.walk(path):
        level = root.replace(path, "").count(os.sep)
        indent = "    " * level
        folder_name = os.path.basename(root) if level > 0 else ""
        if folder_name:
            tree += f"{indent}{folder_name}/\n"
        for file in files:
            tree += f"{indent}    {file}\n"
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_content = f.read()
                content += f"\n# {file}\n{file_content}\n"
            except Exception as e:
                # Skip binary files or files that cannot be read
                content += f"\n# {file}\n[Could not read file: {e}]\n"

    return summary, tree, content
