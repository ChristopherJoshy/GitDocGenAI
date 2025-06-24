from typing import List, Dict, Any
import re

class ReadmeGenerator:
    """Generates clean GitHub README documentation from analyzed files"""
    
    def __init__(self, color_scheme='default'):
        self.color_scheme = color_scheme
        self.color_schemes = self._define_color_schemes()
    
    def generate_readme(self, repo_url: str, analyzed_files: List[Dict[str, Any]]) -> str:
        """
        Generate a clean GitHub README from analyzed files
        
        Args:
            repo_url: GitHub repository URL
            analyzed_files: List of analyzed file data
            
        Returns:
            Clean README markdown string
        """
        
        # Extract repository information
        repo_name = self._extract_repo_name(repo_url)
        project_info = self._analyze_project_structure(analyzed_files)
        
        # Generate README sections
        readme_sections = [
            self._generate_header(repo_name, project_info),
            self._generate_description(project_info),
            self._generate_features(project_info),
            self._generate_tech_stack(project_info),
            self._generate_file_overview(analyzed_files),
            self._generate_setup_instructions(project_info),
            self._generate_footer()
        ]
        
        return "\n".join(readme_sections)
    
    def _generate_shields(self, repo_name: str, project_info: Dict[str, Any]) -> str:
        """Generate shields/badges for the repository"""
        
        # Get current color scheme
        colors = self.color_schemes.get(self.color_scheme, self.color_schemes['default'])
        
        shields = [
            "![GitHub stars](https://img.shields.io/github/stars/username/repo?style=social)",
            "![GitHub forks](https://img.shields.io/github/forks/username/repo?style=social)",
            "![GitHub issues](https://img.shields.io/github/issues/username/repo)",
            "![GitHub license](https://img.shields.io/github/license/username/repo)",
            f"![Language](https://img.shields.io/badge/Language-{project_info['main_language'].title()}-{colors['primary']}?style=for-the-badge)",
            f"![Files](https://img.shields.io/badge/Files-{project_info['total_files']}-{colors['success']}?style=for-the-badge)",
            f"![Theme](https://img.shields.io/badge/Theme-{colors['theme_name'].replace(' ', '%20')}-{colors['secondary']}?style=for-the-badge)"
        ]
        
        return "\n".join([f"<p align=\"center\">{shield}</p>" for shield in shields])
    
    def _get_theme_banner(self) -> str:
        """Get theme-specific banner image"""
        banners = {
            'default': '<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="700">',
            'sunset': '<img src="https://user-images.githubusercontent.com/74038190/212284158-e840e285-664b-44d7-b79b-e264b5e54825.gif" width="700">',
            'forest': '<img src="https://user-images.githubusercontent.com/74038190/212284087-bbe7e430-757e-4901-90bf-4cd2ce3e1852.gif" width="700">',
            'purple': '<img src="https://user-images.githubusercontent.com/74038190/212284115-f47cd8ff-2ffb-4b04-b5bf-4d1c14c0247f.gif" width="700">',
            'cyberpunk': '<img src="https://user-images.githubusercontent.com/74038190/212257454-16e3712e-945a-4ca2-b238-408ad0bf87e6.gif" width="700">',
            'minimal': '<img src="https://user-images.githubusercontent.com/74038190/212257467-871d32b7-e401-42e8-a166-fcfd7baa4c6b.gif" width="700">'
        }
        return f'<p align="center">{banners.get(self.color_scheme, banners["default"])}</p>'
    
    def _get_tech_animation(self) -> str:
        """Get theme-specific technology section animation"""
        animations = {
            'default': '<img src="https://user-images.githubusercontent.com/74038190/212257454-16e3712e-945a-4ca2-b238-408ad0bf87e6.gif" width="100">',
            'sunset': '<img src="https://user-images.githubusercontent.com/74038190/212257467-871d32b7-e401-42e8-a166-fcfd7baa4c6b.gif" width="100">',
            'forest': '<img src="https://user-images.githubusercontent.com/74038190/212257468-1e9a91f1-b626-4baa-b15d-5c385dfa7ed2.gif" width="100">',
            'purple': '<img src="https://user-images.githubusercontent.com/74038190/212284115-f47cd8ff-2ffb-4b04-b5bf-4d1c14c0247f.gif" width="100">',
            'cyberpunk': '<img src="https://user-images.githubusercontent.com/74038190/212257465-7ce8d493-cac5-494e-982a-5a9deb852c4b.gif" width="100">',
            'minimal': '<img src="https://user-images.githubusercontent.com/74038190/212257460-738b9b77-8aeb-4c23-9b80-f2d5d65078d1.gif" width="100">'
        }
        return animations.get(self.color_scheme, animations['default'])
    
    def _define_color_schemes(self) -> dict:
        """Define different color schemes for README styling"""
        return {
            'default': {
                'primary': '36BCF7',
                'secondary': '6C63FF',
                'accent': 'FF6B6B',
                'success': '4ECDC4',
                'warning': 'FFE66D',
                'gradient': 'linear-gradient(45deg, #36BCF7, #6C63FF)',
                'typing_color': '36BCF7',
                'theme_name': 'Ocean Blue'
            },
            'sunset': {
                'primary': 'FF6B6B',
                'secondary': 'FFD93D',
                'accent': 'FF8E53',
                'success': '6BCF7F',
                'warning': 'FFB74D',
                'gradient': 'linear-gradient(45deg, #FF6B6B, #FFD93D)',
                'typing_color': 'FF6B6B',
                'theme_name': 'Sunset Orange'
            },
            'forest': {
                'primary': '4ECDC4',
                'secondary': '44A08D',
                'accent': '096C47',
                'success': '6BCF7F',
                'warning': 'F39C12',
                'gradient': 'linear-gradient(45deg, #4ECDC4, #44A08D)',
                'typing_color': '4ECDC4',
                'theme_name': 'Forest Green'
            },
            'purple': {
                'primary': '6C63FF',
                'secondary': '9C88FF',
                'accent': 'FF6B9D',
                'success': '4ECDC4',
                'warning': 'FFD93D',
                'gradient': 'linear-gradient(45deg, #6C63FF, #9C88FF)',
                'typing_color': '6C63FF',
                'theme_name': 'Royal Purple'
            },
            'cyberpunk': {
                'primary': '00F5FF',
                'secondary': 'FF073A',
                'accent': '39FF14',
                'success': '00FF41',
                'warning': 'FFD700',
                'gradient': 'linear-gradient(45deg, #00F5FF, #FF073A)',
                'typing_color': '00F5FF',
                'theme_name': 'Cyberpunk Neon'
            },
            'minimal': {
                'primary': '2C3E50',
                'secondary': '34495E',
                'accent': '3498DB',
                'success': '27AE60',
                'warning': 'F39C12',
                'gradient': 'linear-gradient(45deg, #2C3E50, #34495E)',
                'typing_color': '2C3E50',
                'theme_name': 'Minimal Dark'
            }
        }
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        match = re.search(r'github\.com/[^/]+/([^/]+?)(?:\.git)?/?$', repo_url)
        if match:
            return match.group(1)
        return repo_url.split('/')[-1].replace('.git', '')
    
    def _analyze_project_structure(self, analyzed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze project structure to understand what it does"""
        
        # Detect project type and purpose
        file_types = {}
        has_frontend = False
        has_backend = False
        has_database = False
        has_mobile = False
        main_language = None
        
        for file_data in analyzed_files:
            language = file_data.get('language', 'unknown')
            file_path = file_data.get('relative_path', '')
            content = file_data.get('content', '')
            
            # Count languages
            if language not in file_types:
                file_types[language] = 0
            file_types[language] += 1
            
            # Detect frontend
            if language in ['html', 'css', 'javascript', 'typescript', 'jsx', 'tsx']:
                has_frontend = True
            
            # Detect backend patterns
            if language in ['python', 'java', 'php', 'ruby', 'go', 'rust', 'csharp']:
                has_backend = True
            
            # Detect database
            if 'firebase' in content.lower() or 'mongodb' in content.lower() or 'sql' in content.lower():
                has_database = True
            
            # Detect mobile
            if 'react native' in content.lower() or 'flutter' in content.lower() or language == 'swift':
                has_mobile = True
        
        # Determine main language
        if file_types:
            main_language = max(file_types.keys(), key=lambda x: file_types[x])
        
        # Determine project type
        project_type = self._determine_project_type(has_frontend, has_backend, has_mobile, main_language)
        
        return {
            'file_types': file_types,
            'main_language': main_language,
            'project_type': project_type,
            'has_frontend': has_frontend,
            'has_backend': has_backend,
            'has_database': has_database,
            'has_mobile': has_mobile,
            'total_files': len(analyzed_files)
        }
    
    def _determine_project_type(self, has_frontend: bool, has_backend: bool, has_mobile: bool, main_language: str) -> str:
        """Determine what type of project this is"""
        
        if has_mobile:
            return "Mobile Application"
        elif has_frontend and has_backend:
            return "Full-Stack Web Application"
        elif has_frontend:
            return "Frontend Web Application"
        elif has_backend:
            return "Backend API/Service"
        elif main_language == 'python':
            return "Python Application"
        elif main_language == 'javascript':
            return "JavaScript Application"
        else:
            return "Software Project"
    
    def _generate_header(self, repo_name: str, project_info: Dict[str, Any]) -> str:
        """Generate enhanced README header with animations and styling"""
        
        # Get current color scheme
        colors = self.color_schemes.get(self.color_scheme, self.color_schemes['default'])
        
        # Generate dynamic shields/badges
        shields = self._generate_shields(repo_name, project_info)
        
        # Create theme-specific header
        theme_banner = self._get_theme_banner()
        
        return f"""<div align="center">

{theme_banner}

# 🚀 {repo_name}

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&duration=3000&pause=1000&color={colors['typing_color']}&center=true&vCenter=true&width=435&lines={project_info['project_type'].replace(' ', '+')};Built+with+{project_info['main_language'].title()};{colors['theme_name'].replace(' ', '+')};Modern+%26+Professional" alt="Typing SVG" />
</p>

{shields}

{theme_banner}

</div>

"""
    
    def _generate_description(self, project_info: Dict[str, Any]) -> str:
        """Generate enhanced project description with visual elements"""
        
        description_templates = {
            "Frontend Web Application": "A modern, responsive web application crafted with cutting-edge technologies to deliver an exceptional user experience across all devices and platforms.",
            "Full-Stack Web Application": "A comprehensive web solution featuring robust frontend interfaces and powerful backend services, engineered for scalability and optimal performance.",
            "Backend API/Service": "A high-performance backend service providing secure, reliable API endpoints with advanced data management and processing capabilities.",
            "Mobile Application": "A feature-rich mobile application optimized for performance, user engagement, and seamless cross-platform compatibility.",
            "Python Application": "A sophisticated Python-based solution leveraging the language's versatility and powerful ecosystem for robust functionality.",
            "JavaScript Application": "A dynamic JavaScript application featuring modern ES6+ syntax, interactive user interfaces, and real-time capabilities."
        }
        
        default_description = "A professionally crafted software project featuring clean architecture, modern development practices, and enterprise-grade code quality."
        description = description_templates.get(project_info['project_type'], default_description)
        
        return f"""<div align="center">

## 📖 About This Project

<img src="https://user-images.githubusercontent.com/74038190/212284087-bbe7e430-757e-4901-90bf-4cd2ce3e1852.gif" width="50">

</div>

{description}

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284158-e840e285-664b-44d7-b79b-e264b5e54825.gif" width="400">
</div>

"""
    
    def _generate_features(self, project_info: Dict[str, Any]) -> str:
        """Generate enhanced features section with icons and styling"""
        
        features = []
        
        if project_info['has_frontend']:
            features.extend([
                "🎨 **Interactive User Interface** - Stunning, responsive design that works seamlessly across all devices",
                "📱 **Mobile-First Design** - Optimized for mobile devices with touch-friendly interactions",
                "⚡ **Lightning Fast Performance** - Optimized loading times and smooth animations",
                "🎯 **User-Centric Experience** - Intuitive navigation and accessibility features"
            ])
        
        if project_info['has_backend']:
            features.extend([
                "🔧 **Robust Backend Architecture** - Scalable server-side processing and logic",
                "🌐 **RESTful API Endpoints** - Well-documented and secure API interfaces",
                "💾 **Advanced Data Management** - Efficient data handling and storage solutions",
                "🔒 **Security First** - Implementation of best security practices and protocols"
            ])
        
        if project_info['has_database']:
            features.extend([
                "🗄️ **Database Integration** - Seamless data persistence and retrieval",
                "🔄 **Real-time Updates** - Live data synchronization and instant updates",
                "📊 **Data Analytics** - Built-in analytics and reporting capabilities"
            ])
        
        # Add generic features if none detected
        if not features:
            features = [
                "🏗️ **Clean Architecture** - Well-structured, maintainable codebase",
                "🔧 **Modular Design** - Reusable components and scalable structure",
                "📈 **Performance Optimized** - Fast, efficient, and reliable operation",
                "🛠️ **Developer Friendly** - Easy setup, clear documentation, and extensible design"
            ]
        
        features_text = "\n".join([f"{feature}" for feature in features])
        
        return f"""<div align="center">

## ✨ Key Features

<img src="https://user-images.githubusercontent.com/74038190/212284115-f47cd8ff-2ffb-4b04-b5bf-4d1c14c0247f.gif" width="100">

</div>

<div align="center">

| Feature Category | Description |
|:---:|:---:|
| 🎨 **Design** | Modern, responsive, and user-friendly interface |
| ⚡ **Performance** | Optimized for speed and efficiency |
| 🔒 **Security** | Built with security best practices |
| 🛠️ **Maintenance** | Easy to update and extend |

</div>

{features_text}

"""
    
    def _generate_tech_stack(self, project_info: Dict[str, Any]) -> str:
        """Generate enhanced technology stack with icons and details"""
        
        # Get current color scheme
        colors = self.color_schemes.get(self.color_scheme, self.color_schemes['default'])
        
        tech_icons = {
            'javascript': f'![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)',
            'typescript': f'![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)',
            'python': f'![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)',
            'html': f'![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)',
            'css': f'![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)',
            'java': f'![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white)',
            'php': f'![PHP](https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white)',
            'ruby': f'![Ruby](https://img.shields.io/badge/Ruby-CC342D?style=for-the-badge&logo=ruby&logoColor=white)',
            'go': f'![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)',
            'rust': f'![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)',
            'swift': f'![Swift](https://img.shields.io/badge/Swift-FA7343?style=for-the-badge&logo=swift&logoColor=white)'
        }
        
        tech_badges = []
        tech_details = []
        
        for lang, count in sorted(project_info['file_types'].items(), key=lambda x: x[1], reverse=True):
            if lang != 'unknown' and count > 0:
                badge = tech_icons.get(lang, f'![{lang.title()}](https://img.shields.io/badge/{lang.title()}-000000?style=for-the-badge)')
                tech_badges.append(badge)
                
                lang_display = {
                    'javascript': 'JavaScript',
                    'typescript': 'TypeScript', 
                    'python': 'Python',
                    'html': 'HTML5',
                    'css': 'CSS3',
                    'java': 'Java',
                    'php': 'PHP',
                    'ruby': 'Ruby',
                    'go': 'Go',
                    'rust': 'Rust',
                    'swift': 'Swift'
                }.get(lang, lang.title())
                
                tech_details.append(f"- **{lang_display}** - {count} files")
        
        if not tech_badges:
            tech_badges = [f'![Various](https://img.shields.io/badge/Various-Technologies-{colors["primary"]}?style=for-the-badge)']
            tech_details = ["- **Multiple Technologies** - Modern tech stack"]
        
        badges_text = "\n".join(tech_badges)
        details_text = "\n".join(tech_details)
        
        # Get theme-specific tech section styling
        tech_animation = self._get_tech_animation()
        
        return f"""<div align="center">

## 🛠️ Technology Stack

{tech_animation}

{badges_text}

</div>

<details>
<summary>📊 <strong>Technology Breakdown</strong></summary>

{details_text}

</details>

"""
    
    def _generate_file_overview(self, analyzed_files: List[Dict[str, Any]]) -> str:
        """Generate simple file overview"""
        
        file_descriptions = []
        
        for file_data in analyzed_files:
            file_name = file_data.get('relative_path', '').split('/')[-1]
            language = file_data.get('language', '')
            content = file_data.get('content', '')
            
            # Generate simple description based on file type and content
            description = self._describe_file_purpose(file_name, language, content)
            
            if description:
                file_descriptions.append(f"**{file_name}** - {description}")
        
        if not file_descriptions:
            return """<div align="center">

## 📁 Project Structure

<img src="https://user-images.githubusercontent.com/74038190/212257468-1e9a91f1-b626-4baa-b15d-5c385dfa7ed2.gif" width="100">

Well-organized codebase with modular architecture and clean structure.

</div>

"""
        
        # Limit to most important files (max 12)
        important_files = file_descriptions[:12]
        
        # Create a nice table format
        table_header = """| File | Description |
|------|-------------|"""
        
        table_rows = []
        for desc in important_files:
            parts = desc.split(' - ', 1)
            if len(parts) == 2:
                filename = parts[0].replace('**', '').replace('*', '')
                description = parts[1]
                table_rows.append(f"| `{filename}` | {description} |")
        
        table_content = table_header + "\n" + "\n".join(table_rows)
        
        return f"""<div align="center">

## 📁 Project Structure

<img src="https://user-images.githubusercontent.com/74038190/212257468-1e9a91f1-b626-4baa-b15d-5c385dfa7ed2.gif" width="100">

</div>

{table_content}

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212257465-7ce8d493-cac5-494e-982a-5a9deb852c4b.gif" width="50">
</div>

"""
    
    def _describe_file_purpose(self, file_name: str, language: str, content: str) -> str:
        """Generate simple description of what a file does"""
        
        file_name_lower = file_name.lower()
        content_lower = content.lower()
        
        # Special cases for common files
        if file_name_lower == 'readme.md':
            return "Project documentation and setup instructions"
        elif file_name_lower == 'package.json':
            return "Project dependencies and configuration"
        elif file_name_lower == 'index.html':
            return "Main webpage entry point"
        elif file_name_lower == 'style.css' or file_name_lower == 'main.css':
            return "Main styling and visual design"
        elif file_name_lower == 'main.js' or file_name_lower == 'app.js':
            return "Core application logic and functionality"
        elif 'admin' in file_name_lower:
            return "Administrative interface and controls"
        elif 'auth' in file_name_lower:
            return "User authentication and security"
        elif 'config' in file_name_lower:
            return "Application configuration settings"
        elif language == 'css':
            return "Styling and visual design"
        elif language == 'javascript':
            if 'function' in content_lower or 'const' in content_lower:
                return "JavaScript functionality and interactions"
            else:
                return "Application scripting"
        elif language == 'html':
            return "User interface and page structure"
        elif language == 'python':
            return "Python application logic"
        elif language == 'json':
            return "Configuration and data structure"
        else:
            return f"{language.title()} source code"
    
    def _generate_setup_instructions(self, project_info: Dict[str, Any]) -> str:
        """Generate comprehensive setup instructions with styling"""
        
        if project_info['has_frontend'] and 'javascript' in project_info['file_types']:
            setup_content = """<details>
<summary>📦 <strong>Prerequisites</strong></summary>

- ![Node.js](https://img.shields.io/badge/Node.js-v14+-green?style=flat-square&logo=node.js)
- ![npm](https://img.shields.io/badge/npm-v6+-red?style=flat-square&logo=npm)
- Modern web browser (Chrome, Firefox, Safari, Edge)

</details>

### 🚀 Quick Start

```bash
# 1️⃣ Clone the repository
git clone <repository-url>
cd <repository-name>

# 2️⃣ Install dependencies
npm install

# 3️⃣ Start development server
npm start

# 4️⃣ Open your browser
# Navigate to http://localhost:3000
```

### 🔧 Development Setup

```bash
# Install development dependencies
npm install --dev

# Run in development mode
npm run dev

# Build for production
npm run build

# Run tests
npm test
```"""
        elif project_info['main_language'] == 'python':
            setup_content = """<details>
<summary>📦 <strong>Prerequisites</strong></summary>

- ![Python](https://img.shields.io/badge/Python-v3.7+-blue?style=flat-square&logo=python)
- ![pip](https://img.shields.io/badge/pip-latest-green?style=flat-square)
- Virtual environment (recommended)

</details>

### 🚀 Quick Start

```bash
# 1️⃣ Clone the repository
git clone <repository-url>
cd <repository-name>

# 2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run the application
python main.py
```

### 🔧 Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .

# Lint code
pylint src/
```"""
        else:
            setup_content = """<details>
<summary>📦 <strong>Prerequisites</strong></summary>

- Compatible development environment
- Required runtime dependencies
- Modern code editor (VS Code recommended)

</details>

### 🚀 Quick Start

```bash
# 1️⃣ Clone the repository
git clone <repository-url>
cd <repository-name>

# 2️⃣ Follow platform-specific setup
# See documentation for detailed instructions

# 3️⃣ Run the application
# Use the appropriate command for your platform
```"""
        
        return f"""<div align="center">

## 🚀 Getting Started

<img src="https://user-images.githubusercontent.com/74038190/212257467-871d32b7-e401-42e8-a166-fcfd7baa4c6b.gif" width="100">

</div>

{setup_content}

<div align="center">

### 🎯 Ready to go! 

<img src="https://user-images.githubusercontent.com/74038190/212257465-7ce8d493-cac5-494e-982a-5a9deb852c4b.gif" width="100">

</div>

"""
    
    def _generate_footer(self) -> str:
        """Generate enhanced README footer with animations"""
        
        return """<div align="center">

## 🤝 Contributing

<img src="https://user-images.githubusercontent.com/74038190/212284145-bf2c01a8-c448-4f1a-b911-99bb33e58e76.gif" width="200">

We welcome contributions! Here's how you can help:

</div>

<details>
<summary>🛠️ <strong>How to Contribute</strong></summary>

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

</details>

<div align="center">

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

<img src="https://user-images.githubusercontent.com/74038190/212284126-046157dc-2d2c-4e47-bfdc-76be8d7d4790.gif" width="150">

If you found this project helpful, please give it a ⭐️!

---

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="500">

**Made with ❤️ and modern web technologies**

<img src="https://komarev.com/ghpvc/?username=repo-visits&color=blueviolet&style=flat-square&label=Repository+Views">

</div>"""