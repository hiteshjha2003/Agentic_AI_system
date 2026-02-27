# backend/app/services/ingestion/code_ingester.py
import os
import ast
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from typing import List, Dict, Any, Generator
from pathlib import Path
import hashlib
from app.config import get_settings   # ← ADD THIS IMPORT

class CodeIngester:
    """
    Ingest entire codebases with AST parsing for intelligent chunking.
    Optimized for retrieval-augmented generation.
    """

    def __init__(self):
        self.settings = get_settings()  # ← ADD THIS LINE
        self.parser = Parser(Language(tspython.language()))
        self.supported_langs = {
            '.py': tspython.language(),
            # Add more tree-sitter grammars as needed
        }

    async def ingest_repository(
        self,
        repo_path: str,
        ignore_patterns: List[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream-process repository for vector store ingestion.
        Yields structured code chunks with metadata.
        """
        ignore_patterns = ignore_patterns or [
            'node_modules', '.git', '__pycache__', '.venv',
            'dist', 'build', '*.min.js', '*.pyc'
        ]

        repo = Path(repo_path)

        for file_path in repo.rglob("*"):
            # Skip ignored patterns
            if any(p in str(file_path) for p in ignore_patterns):
                continue

            if not file_path.is_file():
                continue

            ext = file_path.suffix
            if ext not in self.settings.SUPPORTED_EXTENSIONS:  # ← Now safe
                continue

            # Process file
            try:
                chunks = self._process_file(file_path, repo_path)
                for chunk in chunks:
                    yield chunk
            except Exception as e:
                yield {
                    "type": "error",
                    "file_path": str(file_path),
                    "error": str(e)
                }
    
    def _process_file(
        self, 
        file_path: Path,
        repo_root: str
    ) -> List[Dict[str, Any]]:
        """Parse single file into semantic chunks."""
        
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        rel_path = str(file_path.relative_to(repo_root))
        
        # Language-specific parsing
        if file_path.suffix == '.py':
            return self._parse_python(content, rel_path)
        else:
            # Generic chunking for other languages
            return self._generic_chunking(content, rel_path)
    
    def _parse_python(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """AST-based parsing for Python files."""
        
        try:
            tree = self.parser.parse(bytes(content, "utf8"))
            root_node = tree.root_node
            
            chunks = []
            
            # Extract top-level constructs
            for child in root_node.children:
                if child.type in ('function_definition', 'class_definition'):
                    chunk_text = content[child.start_byte:child.end_byte]
                    
                    # Secondary chunking for very large constructs
                    if len(chunk_text) > 10000:
                        sub_chunks = self._generic_chunking(chunk_text, file_path, chunk_size=100)
                        chunks.extend(sub_chunks)
                        continue

                    # Get function/class name
                    name_node = child.child_by_field_name('name')
                    name = content[name_node.start_byte:name_node.end_byte] if name_node else "unknown"
                    
                    # Get docstring if exists
                    docstring = self._extract_docstring(child, content)
                    
                    chunks.append({
                        "type": "code",
                        "file_path": file_path,
                        "content": chunk_text,
                        "language": "python",
                        "construct_type": child.type,
                        "name": name,
                        "docstring": docstring,
                        "line_start": child.start_point[0] + 1,
                        "line_end": child.end_point[0] + 1,
                        "embedding_text": f"""
                        File: {file_path}
                        {child.type.replace('_', ' ').title()}: {name}
                        Docstring: {docstring}
                        Code:
                        {chunk_text}
                        """.strip(),
                        "content_hash": hashlib.md5(chunk_text.encode()).hexdigest()
                    })
            
            return chunks
            
        except Exception as e:
            # Fallback to generic chunking
            return self._generic_chunking(content, file_path)
    
    def _extract_docstring(self, node, content: str) -> str:
        """Extract docstring from function/class node."""
        # Look for expression_statement containing string
        for child in node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'expression_statement':
                        string_node = stmt.children[0] if stmt.children else None
                        if string_node and string_node.type in ('string', 'comment'):
                            return content[string_node.start_byte:string_node.end_byte]
        return ""
    
    def _generic_chunking(
        self, 
        content: str, 
        file_path: str,
        chunk_size: int = 50,
        overlap: int = 5
    ) -> List[Dict[str, Any]]:
        """Line-based chunking for non-Python files."""
        
        lines = content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), chunk_size - overlap):
            chunk_lines = lines[i:i + chunk_size]
            chunk_text = '\n'.join(chunk_lines)
            
            chunks.append({
                "type": "code",
                "file_path": file_path,
                "content": chunk_text,
                "language": Path(file_path).suffix[1:],
                "construct_type": "chunk",
                "line_start": i + 1,
                "line_end": min(i + chunk_size, len(lines)),
                "embedding_text": f"File: {file_path}\nLines {i+1}-{min(i+chunk_size, len(lines))}:\n{chunk_text}",
                "content_hash": hashlib.md5(chunk_text.encode()).hexdigest()
            })
        
        return chunks