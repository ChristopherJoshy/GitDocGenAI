import os
import time
from typing import Dict, Any
from google import genai
from google.genai import types

class GeminiDocGenerator:
    """Generates documentation using Gemini AI"""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"  # Using free tier model
        self.context_cache = {}  # Cache for repository context
    
    def set_repository_context(self, repo_structure: Dict[str, Any]):
        """Set repository-wide context for better analysis"""
        self.context_cache = {
            'repo_structure': repo_structure,
            'file_count': repo_structure.get('file_count', 0),
            'languages': repo_structure.get('languages', []),
            'main_directories': repo_structure.get('directories', []),
            'dependencies': repo_structure.get('dependencies', [])
        }
    
    def generate_documentation(self, file_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive documentation for a code file using MCP-style context
        
        Args:
            file_data: Dictionary containing file analysis data
            
        Returns:
            Generated documentation as markdown string
        """
        try:
            print(f"Generating docs for: {file_data.get('relative_path', 'unknown')}")
            prompt = self._create_documentation_prompt(file_data)
            
            # Use MCP-style structured generation with timeout
            start_time = time.time()
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1024,  # Reduced for faster processing
                )
            )
            
            elapsed_time = time.time() - start_time
            print(f"API call took {elapsed_time:.2f} seconds")
            
            if response and response.text and len(response.text.strip()) > 10:
                print(f"Generated {len(response.text)} characters of documentation")
                return response.text
            else:
                print("Empty or invalid response from Gemini API, using fallback")
                return self._generate_fallback_documentation(file_data)
                
        except Exception as e:
            print(f"Error generating documentation for {file_data['file_path']}: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return self._generate_fallback_documentation(file_data)
    
    def _create_documentation_prompt(self, file_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for documentation generation"""
        
        file_path = file_data['relative_path']
        content = file_data['content']
        language = file_data['language']
        file_type = file_data['file_type']
        metadata = file_data.get('metadata', {})
        
        # Smart content truncation - keep important parts
        if len(content) > 8000:  # Increased limit for better context
            lines = content.split('\n')
            # Keep header comments, imports, and main structure
            header_lines = []
            body_lines = []
            
            for i, line in enumerate(lines):
                if i < 50:  # Keep first 50 lines (headers, imports)
                    header_lines.append(line)
                elif any(keyword in line.lower() for keyword in ['class ', 'def ', 'function ', 'export ', 'const ', 'let ', 'var ']):
                    body_lines.append(line)
                    if len(body_lines) > 100:  # Limit body lines
                        break
            
            content = '\n'.join(header_lines + ['... [imports and setup code] ...'] + body_lines)
            if len(content) > 8000:
                content = content[:8000] + "\n... [truncated for analysis]"
        
        # Add repository context if available
        context_info = ""
        if self.context_cache:
            context_info = f"""
**Repository Context:**
- **Total Files:** {self.context_cache.get('file_count', 'Unknown')}
- **Languages:** {', '.join(self.context_cache.get('languages', []))}
- **Main Directories:** {', '.join(self.context_cache.get('main_directories', []))}
- **Dependencies:** {', '.join(self.context_cache.get('dependencies', [])[:10])}
"""

        prompt = f"""
You are analyzing a {language} {file_type} file as part of a complete codebase analysis using Model Context Protocol (MCP) principles. Generate comprehensive, colorful, and detailed documentation.

{context_info}

📁 **File Path:** `{file_path}`
🔤 **Language:** {language}
📊 **File Type:** {file_type}
📏 **Size:** {file_data['size']} bytes
📄 **Lines:** {file_data['line_count']}

**File Content:**
```{language}
{content}
```

**Metadata:**
- **Imports/Dependencies:** {', '.join(metadata.get('imports', [])[:5]) if metadata.get('imports') else 'None detected'}
- **Functions/Classes:** {', '.join(metadata.get('definitions', [])[:5]) if metadata.get('definitions') else 'None detected'}
- **Comment Lines:** {metadata.get('comment_lines', 0)}

**Please provide detailed documentation including:**

🎯 **Purpose & Overview**
- What this file does and its role in the project
- Key functionality and features
- Architecture and design patterns used

🔧 **Technical Details**
- Main components (classes, functions, modules)
- Dependencies and imports
- Data structures and algorithms used
- Configuration and settings

💡 **Usage Examples**
- How to use/integrate this file
- Code examples where applicable
- Common use cases

🔗 **Integration Points**
- How this file connects to other parts of the system
- Input/output interfaces
- External dependencies

⚠️ **Important Notes**
- Any limitations or considerations
- Performance implications
- Security considerations if applicable

🚀 **Best Practices**
- Recommended usage patterns
- Maintenance tips
- Extension points

Use emojis, markdown formatting, syntax highlighting, and make it visually appealing and comprehensive!
"""
        
        return prompt
    
    def _generate_fallback_documentation(self, file_data: Dict[str, Any]) -> str:
        """Generate fallback documentation when AI generation fails"""
        
        file_path = file_data['relative_path']
        language = file_data['language']
        file_type = file_data['file_type']
        size = file_data['size']
        line_count = file_data['line_count']
        metadata = file_data.get('metadata', {})
        
        # Create basic documentation structure
        fallback_doc = f"""
## 📄 {file_path}

### 🎯 **File Overview**
- **Language:** {language}
- **Type:** {file_type}
- **Size:** {size} bytes
- **Lines:** {line_count}

### 📊 **File Statistics**
- **Comment Lines:** {metadata.get('comment_lines', 0)}
- **Blank Lines:** {metadata.get('blank_lines', 0)}

### 🔗 **Dependencies**
"""
        
        # Add imports if available
        imports = metadata.get('imports', [])
        if imports:
            fallback_doc += "**Import Statements:**\n"
            for imp in imports[:10]:
                fallback_doc += f"- `{imp}`\n"
        else:
            fallback_doc += "- No imports detected\n"
        
        fallback_doc += "\n### 🔧 **Code Structure**\n"
        
        # Add definitions if available
        definitions = metadata.get('definitions', [])
        if definitions:
            fallback_doc += "**Functions/Classes:**\n"
            for defn in definitions[:15]:
                fallback_doc += f"- `{defn}`\n"
        else:
            fallback_doc += "- No major definitions detected\n"
        
        # Add file content preview
        content = file_data.get('content', '')
        if content:
            preview_lines = content.split('\n')[:10]
            fallback_doc += f"""

### 👀 **Code Preview**
```{language}
{chr(10).join(preview_lines)}
```

### ⚠️ **Note**
This documentation was generated using fallback analysis due to AI service limitations. For more detailed documentation, please try regenerating when the AI service is available.
"""
        
        return fallback_doc
