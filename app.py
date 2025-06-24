import streamlit as st
import tempfile
import os
import shutil
import time
from pathlib import Path
import traceback

from agents.repo_manager import RepoManager
from agents.code_analyzer import CodeAnalyzer
from agents.gemini_doc_generator import GeminiDocGenerator
from agents.doc_aggregator import DocAggregator
from agents.readme_generator import ReadmeGenerator
from utils.validators import validate_github_url, validate_api_key

def main():
    st.set_page_config(
        page_title="📚 GitHub Repo Documentation Generator",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 GitHub Repository Documentation Generator")
    st.markdown("Generate clean GitHub README documentation for any repository using AI-powered analysis")
    
    # Initialize session state
    if 'documentation' not in st.session_state:
        st.session_state.documentation = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Input Section
    st.header("🔧 Configuration")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository",
            help="Enter the full GitHub repository URL"
        )
    
    with col2:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="Enter your Gemini API key",
            help="Get your API key from Google AI Studio"
        )
    
    with col3:
        color_scheme = st.selectbox(
            "🎨 Color Theme",
            options=["default", "sunset", "forest", "purple", "cyberpunk", "minimal"],
            format_func=lambda x: {
                "default": "🌊 Ocean Blue",
                "sunset": "🌅 Sunset Orange", 
                "forest": "🌲 Forest Green",
                "purple": "💜 Royal Purple",
                "cyberpunk": "🔮 Cyberpunk Neon",
                "minimal": "⚫ Minimal Dark"
            }[x],
            help="Choose a color theme for your README"
        )
    
    # Validation
    url_valid = validate_github_url(repo_url) if repo_url else False
    key_valid = validate_api_key(api_key) if api_key else False
    
    if repo_url and not url_valid:
        st.error("❌ Please enter a valid GitHub repository URL")
    
    if api_key and not key_valid:
        st.error("❌ Please enter a valid Gemini API key")
    
    # Generate Documentation Button
    if st.button(
        "🚀 Generate Documentation", 
        disabled=not (url_valid and key_valid) or st.session_state.processing,
        type="primary"
    ):
        generate_documentation(repo_url, api_key)
    
    # Display Results
    if st.session_state.documentation:
        display_results()

def generate_documentation(repo_url: str, api_key: str):
    """Generate documentation for the given repository"""
    st.session_state.processing = True
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize agents
            repo_manager = RepoManager(temp_dir)
            code_analyzer = CodeAnalyzer()
            doc_generator = GeminiDocGenerator(api_key)
            doc_aggregator = DocAggregator()
            readme_generator = ReadmeGenerator(color_scheme)
            
            # Step 1: Clone repository
            status_text.text("📥 Cloning repository...")
            progress_bar.progress(10)
            
            repo_path = repo_manager.clone_repository(repo_url)
            
            # Step 2: Scan files
            status_text.text("🔍 Scanning repository files...")
            progress_bar.progress(25)
            
            file_list = repo_manager.scan_files(repo_path)
            
            if not file_list:
                st.error("❌ No supported files found in the repository")
                return
            
            st.info(f"📁 Found {len(file_list)} files to analyze")
            
            # Step 3: Build repository context
            status_text.text("🔍 Building repository context...")
            progress_bar.progress(30)
            
            # Create comprehensive repository structure context
            languages = list(set([f.suffix.lower().replace('.', '') for f in file_list if f.suffix]))
            directories = []
            dependencies = []
            
            # Extract directory structure
            for f in file_list:
                try:
                    rel_path = f.relative_to(repo_path)
                    if len(rel_path.parts) > 1:
                        directories.append(str(rel_path.parent))
                except:
                    pass
            
            directories = list(set(directories))[:20]  # Limit to top 20 directories
            
            # Quick scan for common dependency files
            for f in file_list:
                if f.name.lower() in ['package.json', 'requirements.txt', 'composer.json', 'pom.xml', 'cargo.toml', 'go.mod']:
                    try:
                        with open(f, 'r', encoding='utf-8', errors='ignore') as dep_file:
                            content = dep_file.read()[:2000]  # First 2KB for quick scan
                            dependencies.append(f"{f.name}: {content[:100]}...")
                    except:
                        dependencies.append(f.name)
            
            repo_structure = {
                'file_count': len(file_list),
                'languages': languages,
                'directories': directories,
                'dependencies': dependencies
            }
            
            # Set context for AI generator
            doc_generator.set_repository_context(repo_structure)
            
            # Step 4: Analyze files
            status_text.text("📊 Analyzing code files...")
            progress_bar.progress(40)
            
            analyzed_files = []
            for i, file_path in enumerate(file_list):
                try:
                    file_content = code_analyzer.analyze_file(file_path)
                    if file_content:
                        analyzed_files.append(file_content)
                    
                    # Update progress
                    current_progress = 40 + (30 * (i + 1) / len(file_list))
                    progress_bar.progress(int(current_progress))
                    
                except Exception as e:
                    st.warning(f"⚠️ Could not analyze {file_path}: {str(e)}")
            
            # Step 5: Generate documentation with full context
            status_text.text("🤖 Generating comprehensive AI documentation...")
            progress_bar.progress(70)
            
            documented_files = []
            for i, file_data in enumerate(analyzed_files):
                try:
                    st.info(f"Processing file {i+1}/{len(analyzed_files)}: {file_data.get('relative_path', 'unknown')}")
                    
                    # Add timeout protection
                    start_time = time.time()
                    documentation = doc_generator.generate_documentation(file_data)
                    end_time = time.time()
                    
                    st.success(f"✅ Completed in {end_time - start_time:.1f}s")
                    
                    documented_files.append({
                        'file_path': file_data['file_path'],
                        'documentation': documentation
                    })
                    
                    # Update progress
                    current_progress = 70 + (20 * (i + 1) / len(analyzed_files))
                    progress_bar.progress(int(current_progress))
                    
                    # Small delay to prevent API rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    st.error(f"❌ Error with {file_data.get('relative_path', 'unknown')}: {str(e)}")
                    # Continue with fallback documentation
                    try:
                        fallback_doc = doc_generator._generate_fallback_documentation(file_data)
                        documented_files.append({
                            'file_path': file_data['file_path'],
                            'documentation': fallback_doc
                        })
                    except:
                        pass
            
            # Step 6: Generate clean README
            status_text.text("📝 Creating clean GitHub README...")
            progress_bar.progress(90)
            
            final_documentation = readme_generator.generate_readme(
                repo_url, analyzed_files
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Clean GitHub README generated successfully!")
            
            # Store results
            st.session_state.documentation = final_documentation
            
            # Cleanup notification
            st.success("🧹 Repository files cleaned up automatically")
            
    except Exception as e:
        st.error(f"❌ Error generating documentation: {str(e)}")
        st.error("📋 Full error details:")
        st.code(traceback.format_exc())
    
    finally:
        st.session_state.processing = False

def display_results():
    """Display the generated documentation"""
    st.header("📄 Generated README")
    
    # Preview section
    with st.expander("👀 Preview README", expanded=True):
        st.markdown(st.session_state.documentation)
    
    # Download section
    st.header("💾 Download README")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.download_button(
            label="📥 Download README.md",
            data=st.session_state.documentation,
            file_name="README.md",
            mime="text/markdown",
            type="primary"
        )
    
    with col2:
        if st.button("🔄 Generate New README"):
            st.session_state.documentation = None
            st.rerun()
    
    # Statistics
    word_count = len(st.session_state.documentation.split())
    line_count = len(st.session_state.documentation.split('\n'))
    
    st.info(f"📊 README Statistics: {word_count} words, {line_count} lines")

if __name__ == "__main__":
    main()
