import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
import requests
import zipfile
import re

class RepoManager:
    """Handles GitHub repository cloning and file management"""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.supported_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', 
            '.sass', '.less', '.java', '.cpp', '.c', '.h', '.hpp', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.sh',
            '.bash', '.ps1', '.sql', '.xml', '.json', '.yaml', '.yml',
            '.md', '.rst', '.txt', '.dockerfile', '.makefile', '.r', '.m'
        }
    
    def clone_repository(self, repo_url: str) -> Path:
        """
        Clone or download a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Path to the cloned repository
            
        Raises:
            Exception: If cloning fails
        """
        try:
            # Try git clone first
            return self._git_clone(repo_url)
        except Exception:
            # Fallback to ZIP download
            return self._download_zip(repo_url)
    
    def _git_clone(self, repo_url: str) -> Path:
        """Clone repository using git"""
        repo_name = self._extract_repo_name(repo_url)
        clone_path = self.temp_dir / repo_name
        
        # Execute git clone
        result = subprocess.run([
            'git', 'clone', '--depth', '1', repo_url, str(clone_path)
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Git clone failed: {result.stderr}")
        
        return clone_path
    
    def _download_zip(self, repo_url: str) -> Path:
        """Download repository as ZIP file"""
        # Convert GitHub URL to ZIP download URL
        zip_url = self._get_zip_url(repo_url)
        repo_name = self._extract_repo_name(repo_url)
        
        # Download ZIP file
        response = requests.get(zip_url, timeout=300)
        response.raise_for_status()
        
        # Save and extract ZIP
        zip_path = self.temp_dir / f"{repo_name}.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        extract_path = self.temp_dir / repo_name
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        # Find the extracted directory (GitHub adds branch name to folder)
        extracted_dirs = [d for d in self.temp_dir.iterdir() if d.is_dir() and d.name != repo_name]
        if extracted_dirs:
            # Rename the extracted directory
            shutil.move(str(extracted_dirs[0]), str(extract_path))
        elif not extract_path.exists():
            # Fallback: look for any directory that might be the repo
            all_dirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
            if all_dirs:
                shutil.move(str(all_dirs[0]), str(extract_path))
        
        # Clean up ZIP file
        zip_path.unlink()
        
        return extract_path
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        # Handle various GitHub URL formats
        patterns = [
            r'github\.com/[^/]+/([^/]+?)(?:\.git)?/?$',
            r'github\.com/([^/]+/[^/]+?)(?:\.git)?/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                repo_path = match.group(1)
                if '/' in repo_path:
                    return repo_path.split('/')[-1]
                return repo_path
        
        # Fallback: use last part of URL
        return repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    
    def _get_zip_url(self, repo_url: str) -> str:
        """Convert GitHub repo URL to ZIP download URL"""
        # Remove .git suffix and trailing slash
        clean_url = repo_url.rstrip('/').replace('.git', '')
        
        # Convert to ZIP download URL - try multiple branch names
        if 'github.com' in clean_url:
            # Try common branch names in order
            for branch in ['main', 'master', 'dev', 'develop']:
                try:
                    test_url = f"{clean_url}/archive/refs/heads/{branch}.zip"
                    response = requests.head(test_url, timeout=10)
                    if response.status_code == 200:
                        return test_url
                except:
                    continue
            
            # Default to main if all fail
            return f"{clean_url}/archive/refs/heads/main.zip"
        
        raise Exception(f"Unsupported repository URL format: {repo_url}")
    
    def scan_files(self, repo_path: Path) -> List[Path]:
        """
        Recursively scan repository for supported files
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of file paths to analyze
        """
        files = []
        
        # Skip common non-code directories
        skip_dirs = {
            '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
            'node_modules', '.next', '.nuxt', 'build', 'dist',
            '.vscode', '.idea', '.DS_Store', 'venv', '.env',
            '.venv', 'env', 'virtualenv', '.tox'
        }
        
        for file_path in repo_path.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip files in excluded directories
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue
            
            # Skip very large files (> 5MB) but allow larger code files
            try:
                if file_path.stat().st_size > 5 * 1024 * 1024:
                    continue
            except OSError:
                continue
            
            # Check file extension
            if file_path.suffix.lower() in self.supported_extensions:
                files.append(file_path)
            
            # Include files without extensions that might be important
            elif not file_path.suffix and file_path.name.lower() in {
                'dockerfile', 'makefile', 'readme', 'license', 'changelog',
                'contributing', 'authors', 'install', 'news'
            }:
                files.append(file_path)
        
        # Sort files for consistent processing
        return sorted(files)
    
    def get_relative_path(self, file_path: Path, repo_path: Path) -> str:
        """Get relative path from repository root"""
        try:
            return str(file_path.relative_to(repo_path))
        except ValueError:
            return str(file_path)
