#!/usr/bin/env python
"""Comprehensive error checking script for Flask app."""
import os
import sys
import ast
import importlib.util
from pathlib import Path

class ErrorChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def check_syntax(self, filepath):
        """Check Python file for syntax errors."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source)
            return True
        except SyntaxError as e:
            self.errors.append(f"❌ SYNTAX ERROR in {filepath}:{e.lineno}: {e.msg}")
            return False
        except Exception as e:
            self.errors.append(f"❌ ERROR reading {filepath}: {e}")
            return False

    def check_imports(self, filepath):
        """Check if imports are valid."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check common typos
                        if 'flask' in alias.name.lower() and alias.name != alias.name.lower():
                            self.warnings.append(f"⚠️  Possible import case issue in {filepath}: {alias.name}")

                elif isinstance(node, ast.ImportFrom):
                    # Check for circular imports (common issue)
                    if node.module and 'app' in node.module:
                        self.info.append(f"ℹ️  Internal import in {filepath}: from {node.module} import ...")
        except Exception as e:
            pass  # Already caught in syntax check

    def check_model_relationships(self, filepath):
        """Check for common model relationship errors."""
        if 'models' not in str(filepath):
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for duplicate backref
            if 'backref=' in content and content.count('backref=') > 1:
                # Find specific backref names
                import re
                backrefs = re.findall(r"backref=['\"](\w+)['\"]", content)
                duplicates = [b for b in backrefs if backrefs.count(b) > 1]
                if duplicates:
                    self.warnings.append(f"⚠️  Possible duplicate backref in {filepath}: {set(duplicates)}")

            # Check for relationship without backref or back_populates
            if 'db.relationship' in content:
                relationships = re.findall(r"db\.relationship\(['\"](\w+)['\"]([^\)]*)\)", content)
                for rel_name, rel_args in relationships:
                    if 'backref' not in rel_args and 'back_populates' not in rel_args:
                        self.info.append(f"ℹ️  Relationship without backref in {filepath}: {rel_name}")

        except Exception as e:
            pass

    def check_required_files(self):
        """Check if required files exist."""
        required_files = [
            'run.py',
            'app/__init__.py',
            'app/models/__init__.py',
            'app/extensions.py',
            'requirements.txt',
            '.env.example'
        ]

        for file in required_files:
            filepath = os.path.join('/home/user/Ecommerce_php/flask-app', file)
            if not os.path.exists(filepath):
                self.errors.append(f"❌ Missing required file: {file}")
            else:
                self.info.append(f"✅ Found: {file}")

    def check_env_file(self):
        """Check .env file configuration."""
        env_file = '/home/user/Ecommerce_php/flask-app/.env'
        env_example = '/home/user/Ecommerce_php/flask-app/.env.example'

        if not os.path.exists(env_file):
            if os.path.exists(env_example):
                self.warnings.append(f"⚠️  .env file not found. Copy from .env.example")
            else:
                self.errors.append(f"❌ Neither .env nor .env.example found")
        else:
            self.info.append(f"✅ .env file exists")

            # Check if .env has required variables
            with open(env_file, 'r') as f:
                env_content = f.read()

            required_vars = ['DB_HOST', 'DB_USER', 'DB_NAME', 'SECRET_KEY']
            for var in required_vars:
                if var not in env_content:
                    self.warnings.append(f"⚠️  Missing environment variable: {var}")

    def run_checks(self):
        """Run all checks."""
        print("="*70)
        print("🔍 INICIANDO DIAGNÓSTICO COMPLETO DEL SISTEMA")
        print("="*70 + "\n")

        # Check required files
        print("📁 Verificando archivos requeridos...")
        self.check_required_files()
        print()

        # Check .env
        print("⚙️  Verificando configuración de entorno...")
        self.check_env_file()
        print()

        # Check all Python files
        print("🐍 Analizando archivos Python...")
        app_dir = Path('/home/user/Ecommerce_php/flask-app')
        python_files = list(app_dir.rglob('*.py'))

        # Exclude venv and migrations
        python_files = [f for f in python_files if 'venv' not in str(f) and '__pycache__' not in str(f)]

        syntax_ok = 0
        syntax_fail = 0

        for filepath in python_files:
            relative_path = filepath.relative_to(app_dir)
            if self.check_syntax(filepath):
                syntax_ok += 1
                self.check_imports(filepath)
                self.check_model_relationships(filepath)
            else:
                syntax_fail += 1

        print(f"   ✅ Archivos sin errores de sintaxis: {syntax_ok}")
        print(f"   ❌ Archivos con errores: {syntax_fail}")
        print()

        # Print results
        self.print_results()

    def print_results(self):
        """Print all findings."""
        print("="*70)
        print("📊 RESUMEN DE DIAGNÓSTICO")
        print("="*70 + "\n")

        if self.errors:
            print(f"❌ ERRORES CRÍTICOS ({len(self.errors)}):")
            print("-" * 70)
            for error in self.errors:
                print(f"  {error}")
            print()
        else:
            print("✅ No se encontraron errores críticos\n")

        if self.warnings:
            print(f"⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            print("-" * 70)
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        else:
            print("✅ No se encontraron advertencias\n")

        if self.info:
            print(f"ℹ️  INFORMACIÓN ({len(self.info)}):")
            print("-" * 70)
            # Only show first 10 info messages
            for info in self.info[:10]:
                print(f"  {info}")
            if len(self.info) > 10:
                print(f"  ... y {len(self.info) - 10} más")
            print()

        # Final summary
        print("="*70)
        if not self.errors:
            print("✅ DIAGNÓSTICO COMPLETADO - Sistema saludable")
        else:
            print("❌ DIAGNÓSTICO COMPLETADO - Se encontraron errores que requieren atención")
        print("="*70)

if __name__ == '__main__':
    checker = ErrorChecker()
    checker.run_checks()
