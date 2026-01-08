#!/usr/bin/env python3
"""
Test quality checker - validates test structure and best practices.
"""

import ast
import re
from pathlib import Path
from collections import defaultdict


class TestQualityChecker(ast.NodeVisitor):
    """AST visitor to check test quality."""

    def __init__(self):
        self.test_methods = []
        self.has_docstrings = 0
        self.missing_docstrings = 0
        self.assertions = 0
        self.test_classes = []
        self.fixtures_used = set()
        self.imports = set()

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        if node.name.startswith('Test'):
            self.test_classes.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        if node.name.startswith('test_'):
            self.test_methods.append(node.name)

            # Check for docstring
            if ast.get_docstring(node):
                self.has_docstrings += 1
            else:
                self.missing_docstrings += 1

            # Check for assertions
            for child in ast.walk(node):
                if isinstance(child, ast.Assert):
                    self.assertions += 1

            # Check for fixtures in arguments
            for arg in node.args.args:
                if arg.arg not in ['self', 'cls']:
                    self.fixtures_used.add(arg.arg)

        self.generic_visit(node)

    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.add(alias.name)

    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        if node.module:
            self.imports.add(node.module)


def analyze_test_file(filepath):
    """Analyze a test file for quality metrics."""
    with open(filepath, 'r') as f:
        content = f.read()

    tree = ast.parse(content)
    checker = TestQualityChecker()
    checker.visit(tree)

    return {
        'test_methods': len(checker.test_methods),
        'test_classes': len(checker.test_classes),
        'has_docstrings': checker.has_docstrings,
        'missing_docstrings': checker.missing_docstrings,
        'assertions': checker.assertions,
        'fixtures_used': checker.fixtures_used,
        'imports': checker.imports,
        'method_names': checker.test_methods,
        'class_names': checker.test_classes
    }


def main():
    """Main function."""
    test_dir = Path('circuithelper/tests')

    print("🔬 Test Quality Analysis\n")
    print("=" * 70)

    test_files = sorted(test_dir.glob('test_*.py'))

    total_stats = {
        'files': 0,
        'methods': 0,
        'classes': 0,
        'with_docstrings': 0,
        'without_docstrings': 0,
        'assertions': 0,
        'fixtures': set()
    }

    all_imports = defaultdict(int)

    for test_file in test_files:
        print(f"\n📝 {test_file.name}")
        print("-" * 70)

        stats = analyze_test_file(test_file)

        print(f"  Test Classes: {stats['test_classes']}")
        print(f"  Test Methods: {stats['test_methods']}")
        print(f"  With Docstrings: {stats['has_docstrings']}")
        print(f"  Without Docstrings: {stats['missing_docstrings']}")
        print(f"  Total Assertions: {stats['assertions']}")

        if stats['test_methods'] > 0:
            docstring_pct = (stats['has_docstrings'] / stats['test_methods']) * 100
            assertions_per_test = stats['assertions'] / stats['test_methods']

            print(f"  Docstring Coverage: {docstring_pct:.1f}%")
            print(f"  Assertions/Test: {assertions_per_test:.1f}")

            # Quality checks
            issues = []
            if docstring_pct < 80:
                issues.append(f"Low docstring coverage ({docstring_pct:.1f}%)")
            if assertions_per_test < 1:
                issues.append(f"Few assertions per test ({assertions_per_test:.1f})")

            if issues:
                print(f"  ⚠️  Issues: {', '.join(issues)}")
            else:
                print(f"  ✅ Quality: Good")

        if stats['fixtures_used']:
            print(f"  Fixtures: {', '.join(sorted(stats['fixtures_used']))}")

        # Update totals
        total_stats['files'] += 1
        total_stats['methods'] += stats['test_methods']
        total_stats['classes'] += stats['test_classes']
        total_stats['with_docstrings'] += stats['has_docstrings']
        total_stats['without_docstrings'] += stats['missing_docstrings']
        total_stats['assertions'] += stats['assertions']
        total_stats['fixtures'].update(stats['fixtures_used'])

        for imp in stats['imports']:
            all_imports[imp] += 1

    # Summary
    print("\n" + "=" * 70)
    print("\n📊 Overall Test Suite Quality\n")

    print(f"Total Test Files: {total_stats['files']}")
    print(f"Total Test Classes: {total_stats['classes']}")
    print(f"Total Test Methods: {total_stats['methods']}")
    print(f"Total Assertions: {total_stats['assertions']}")

    if total_stats['methods'] > 0:
        overall_docstring_pct = (total_stats['with_docstrings'] / total_stats['methods']) * 100
        overall_assertions = total_stats['assertions'] / total_stats['methods']

        print(f"\nQuality Metrics:")
        print(f"  Docstring Coverage: {overall_docstring_pct:.1f}%")
        print(f"  Assertions per Test: {overall_assertions:.1f}")

        # Quality score
        quality_checks = []
        if overall_docstring_pct >= 80:
            quality_checks.append("✅ Good docstring coverage")
        else:
            quality_checks.append(f"⚠️  Low docstring coverage ({overall_docstring_pct:.1f}%)")

        if overall_assertions >= 2:
            quality_checks.append("✅ Good assertion coverage")
        elif overall_assertions >= 1:
            quality_checks.append("⚠️  Moderate assertion coverage")
        else:
            quality_checks.append("❌ Low assertion coverage")

        if total_stats['methods'] >= 100:
            quality_checks.append("✅ Comprehensive test count")
        else:
            quality_checks.append("⚠️  Could use more tests")

        print(f"\nQuality Checks:")
        for check in quality_checks:
            print(f"  {check}")

    # Fixtures
    if total_stats['fixtures']:
        print(f"\nFixtures Used ({len(total_stats['fixtures'])}):")
        for fixture in sorted(total_stats['fixtures']):
            print(f"  • {fixture}")

    # Most common imports
    print(f"\nTop Dependencies:")
    sorted_imports = sorted(all_imports.items(), key=lambda x: x[1], reverse=True)
    for imp, count in sorted_imports[:10]:
        if not imp.startswith('circuithelper'):
            print(f"  • {imp} (used in {count} files)")

    print("\n" + "=" * 70)
    print("\n✅ Test quality analysis complete!")


if __name__ == '__main__':
    main()
