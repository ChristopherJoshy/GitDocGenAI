import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import mimetypes

class CodeAnalyzer:
    """Analyzes and prepares code files for documentation generation"""
    
    def __init__(self):
        self.max_file_size = 500 * 1024  # 500KB limit per file (increased for better analysis)
        self.encoding_attempts = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
    
    def analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single file and prepare it for documentation
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary containing file analysis data or None if file cannot be processed
        """
        try:
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                return None
            
            # Read file content
            content = self._read_file_content(file_path)
            if content is None:
                return None
            
            # Determine file type and language
            file_type = self._determine_file_type(file_path)
            language = self._determine_language(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, content)
            
            # Create analysis result with full context
            relative_path = str(file_path).split('/')[-1] if '/' in str(file_path) else str(file_path)
            if hasattr(file_path, 'relative_to'):
                try:
                    # Try to get relative path from repo root
                    parts = file_path.parts
                    if len(parts) > 1:
                        relative_path = '/'.join(parts[-2:]) if len(parts) > 2 else parts[-1]
                except:
                    relative_path = file_path.name
            
            return {
                'file_path': str(file_path),
                'relative_path': relative_path,
                'content': content,
                'file_type': file_type,
                'language': language,
                'size': file_path.stat().st_size,
                'line_count': len(content.splitlines()),
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Error analyzing file {file_path}: {str(e)}")
            return None
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with multiple encoding attempts"""
        for encoding in self.encoding_attempts:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    # Skip empty files or files with only whitespace
                    if not content.strip():
                        return None
                    return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                return None
        
        return None
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the general type of file"""
        suffix = file_path.suffix.lower()
        
        type_mapping = {
            # Web files
            '.html': 'web',
            '.css': 'stylesheet',
            '.scss': 'stylesheet', 
            '.sass': 'stylesheet',
            '.less': 'stylesheet',
            '.js': 'script',
            '.jsx': 'script',
            '.ts': 'script',
            '.tsx': 'script',
            
            # Programming languages
            '.py': 'source',
            '.java': 'source',
            '.cpp': 'source',
            '.c': 'source',
            '.h': 'header',
            '.hpp': 'header',
            '.cs': 'source',
            '.php': 'source',
            '.rb': 'source',
            '.go': 'source',
            '.rs': 'source',
            '.swift': 'source',
            '.kt': 'source',
            '.scala': 'source',
            '.r': 'source',
            '.m': 'source',
            
            # Scripts
            '.sh': 'script',
            '.bash': 'script',
            '.ps1': 'script',
            
            # Data files
            '.json': 'data',
            '.xml': 'data',
            '.yaml': 'data',
            '.yml': 'data',
            '.sql': 'database',
            
            # Documentation
            '.md': 'documentation',
            '.rst': 'documentation',
            '.txt': 'text'
        }
        
        return type_mapping.get(suffix, 'unknown')
    
    def _determine_language(self, file_path: Path) -> str:
        """Determine the programming language"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        
        # Extension-based detection
        language_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.bash': 'bash',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.r': 'r',
            '.m': 'matlab'
        }
        
        if suffix in language_mapping:
            return language_mapping[suffix]
        
        # Name-based detection for files without extensions
        if name in ['dockerfile']:
            return 'dockerfile'
        elif name in ['makefile']:
            return 'makefile'
        
        return 'text'
    
    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from file content"""
        metadata = {}
        
        try:
            lines = content.splitlines()
            if not lines:
                return metadata
            
            # Extract first few lines for context
            metadata['first_lines'] = lines[:5]
            
            # Count basic statistics
            metadata['blank_lines'] = sum(1 for line in lines if not line.strip())
            metadata['comment_lines'] = self._count_comment_lines(lines, file_path.suffix)
            
            # Extract imports/includes (first 50 lines)
            metadata['imports'] = self._extract_imports(lines[:50], file_path.suffix)
            
            # Extract functions/classes (basic detection)
            metadata['definitions'] = self._extract_definitions(lines, file_path.suffix)
            
        except Exception as e:
            print(f"Error extracting metadata for {file_path}: {str(e)}")
        
        return metadata
    
    def _count_comment_lines(self, lines: List[str], suffix: str) -> int:
        """Count comment lines based on file type"""
        comment_prefixes = {
            '.py': ['#'],
            '.js': ['//', '/*'],
            '.jsx': ['//', '/*'],
            '.ts': ['//', '/*'],
            '.tsx': ['//', '/*'],
            '.java': ['//', '/*'],
            '.cpp': ['//', '/*'],
            '.c': ['//', '/*'],
            '.cs': ['//', '/*'],
            '.php': ['//', '/*', '#'],
            '.rb': ['#'],
            '.go': ['//'],
            '.rs': ['//'],
            '.sh': ['#'],
            '.bash': ['#'],
            '.sql': ['--'],
            '.html': ['<!--'],
            '.css': ['/*']
        }
        
        prefixes = comment_prefixes.get(suffix.lower(), [])
        if not prefixes:
            return 0
        
        count = 0
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(prefix) for prefix in prefixes):
                count += 1
        
        return count
    
    def _extract_imports(self, lines: List[str], suffix: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        import_keywords = {
            '.py': ['import ', 'from '],
            '.js': ['import ', 'require('],
            '.jsx': ['import ', 'require('],
            '.ts': ['import ', 'require('],
            '.tsx': ['import ', 'require('],
            '.java': ['import '],
            '.cpp': ['#include'],
            '.c': ['#include'],
            '.cs': ['using '],
            '.go': ['import '],
            '.rs': ['use ']
        }
        
        keywords = import_keywords.get(suffix.lower(), [])
        
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(keyword) for keyword in keywords):
                imports.append(stripped)
        
        return imports[:10]  # Limit to first 10 imports
    
    def _extract_definitions(self, lines: List[str], suffix: str) -> List[str]:
        """Extract function and class definitions"""
        definitions = []
        
        definition_keywords = {
            '.py': ['def ', 'class ', 'async def '],
            '.js': ['function ', 'class ', 'const ', 'let ', 'var '],
            '.jsx': ['function ', 'class ', 'const ', 'let ', 'var '],
            '.ts': ['function ', 'class ', 'interface ', 'type '],
            '.tsx': ['function ', 'class ', 'interface ', 'type '],
            '.java': ['public class', 'private class', 'public interface', 'public void', 'private void'],
            '.cpp': ['class ', 'struct ', 'void ', 'int ', 'double '],
            '.c': ['void ', 'int ', 'double ', 'struct '],
            '.cs': ['public class', 'private class', 'public void', 'private void'],
            '.php': ['function ', 'class '],
            '.rb': ['def ', 'class '],
            '.go': ['func ', 'type '],
            '.rs': ['fn ', 'struct ', 'impl ']
        }
        
        keywords = definition_keywords.get(suffix.lower(), [])
        
        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped for keyword in keywords):
                # Clean up the line for better readability
                clean_line = stripped.split('{')[0].split('(')[0]
                if len(clean_line) < 100:  # Avoid very long lines
                    definitions.append(clean_line)
        
        return definitions[:20]  # Limit to first 20 definitions
