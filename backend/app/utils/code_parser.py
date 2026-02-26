# backend/app/utils/code_parser.py
import ast
import json
from typing import Dict, Any, List

class CodeParser:
    """
    Utility for parsing and analyzing code snippets.
    """

    @staticmethod
    def parse_python(code: str) -> Dict[str, Any]:
        """Parse Python code into AST and extract key elements."""
        try:
            tree = ast.parse(code)
            return {
                "functions": [
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    }
                    for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                ],
                "classes": [
                    {
                        "name": node.name,
                        "lineno": node.lineno,
                        "bases": [b.id for b in node.bases if isinstance(b, ast.Name)]
                    }
                    for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                ],
                "imports": [
                    {
                        "module": node.module,
                        "names": [n.name for n in node.names]
                    }
                    for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                ]
            }
        except SyntaxError:
            return {"error": "Invalid Python syntax"}

    @staticmethod
    def generate_diff(original: str, modified: str) -> str:
        """Generate unified diff between two code versions."""
        from difflib import unified_diff
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        return ''.join(unified_diff(orig_lines, mod_lines, fromfile="original", tofile="modified"))

    @staticmethod
    def extract_comments(code: str) -> List[str]:
        """Extract all comments from code."""
        import tokenize
        from io import StringIO
        comments = []
        for token in tokenize.generate_tokens(StringIO(code).readline):
            if token.type == tokenize.COMMENT:
                comments.append(token.string.strip("# "))
        return comments