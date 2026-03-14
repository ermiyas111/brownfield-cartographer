import os
from tree_sitter_languages import get_language
from tree_sitter import Parser
from typing import List, Dict, Any

class LanguageRouter:
    def __init__(self):
        self.languages = {
            '.py': get_language('python'),
            '.sql': get_language('sql'),
            '.yaml': get_language('yaml'),
            '.yml': get_language('yaml'),
            '.ts': get_language('typescript'),
        }
        self.parsers = {ext: self._make_parser(lang) for ext, lang in self.languages.items()}

    def _make_parser(self, language):
        parser = Parser()
        parser.set_language(language)
        return parser

    def get_parser_for_file(self, filename: str):
        ext = os.path.splitext(filename)[1]
        return self.parsers.get(ext)

    def analyze_python(self, code: str) -> Dict[str, Any]:
        parser = self.parsers['.py']
        tree = parser.parse(bytes(code, 'utf8'))
        root = tree.root_node
        imports, classes, functions = [], [], []
        for node in root.children:
            if node.type == 'import_statement' or node.type == 'import_from_statement':
                imports.append(code[node.start_byte:node.end_byte].strip())
            elif node.type == 'class_definition':
                class_name = None
                bases = []
                for child in node.children:
                    if child.type == 'identifier':
                        class_name = code[child.start_byte:child.end_byte]
                    if child.type == 'argument_list':
                        bases = [code[c.start_byte:c.end_byte] for c in child.children if c.type == 'identifier']
                if class_name:
                    classes.append({'name': class_name, 'bases': bases})
            elif node.type == 'function_definition':
                func_name = None
                for child in node.children:
                    if child.type == 'identifier':
                        func_name = code[child.start_byte:child.end_byte]
                if func_name and not func_name.startswith('_'):
                    functions.append(func_name)
        return {'imports': imports, 'classes': classes, 'functions': functions}

    def analyze(self, filename: str, code: str) -> Dict[str, Any]:
        ext = os.path.splitext(filename)[1]
        if ext == '.py':
            return self.analyze_python(code)
        # Add more handlers for .sql, .yaml, .ts as needed
        return {}
