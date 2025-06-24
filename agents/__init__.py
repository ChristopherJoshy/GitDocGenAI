"""
Modular agent-based architecture for GitHub repository documentation generation.
"""

from .repo_manager import RepoManager
from .code_analyzer import CodeAnalyzer
from .gemini_doc_generator import GeminiDocGenerator
from .doc_aggregator import DocAggregator

__all__ = [
    'RepoManager',
    'CodeAnalyzer', 
    'GeminiDocGenerator',
    'DocAggregator'
]
