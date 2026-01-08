#!/usr/bin/env python3
"""
Test validation script that checks test files for syntax and structure
without requiring NetBox to be installed.
"""

import ast
import sys
from pathlib import Path


def validate_python_file(filepath):
    """Validate Python file syntax."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def count_test_methods(filepath):
    """Count test methods in a test file."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
        tree = ast.parse(content)

        test_count = 0
        class_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith("Test"):
                    class_count += 1
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_"):
                    test_count += 1

        return test_count, class_count
    except Exception as e:
        return 0, 0


def main():
    """Main validation function."""
    test_dir = Path("circuithelper/tests")

    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return 1

    print("🔍 Validating NetBox Circuit Manager Tests\n")
    print("=" * 60)

    # Find all test files
    test_files = list(test_dir.glob("test_*.py"))
    test_files.append(test_dir / "conftest.py")

    total_tests = 0
    total_classes = 0
    total_files = 0
    errors = []

    for test_file in sorted(test_files):
        if not test_file.exists():
            continue

        print(f"\n📄 {test_file.name}")

        # Validate syntax
        valid, error = validate_python_file(test_file)
        if not valid:
            print(f"   ❌ Syntax Error: {error}")
            errors.append((test_file.name, error))
            continue

        print(f"   ✓ Syntax: Valid")

        # Count tests
        test_count, class_count = count_test_methods(test_file)
        if test_count > 0:
            print(f"   ✓ Test Methods: {test_count}")
            print(f"   ✓ Test Classes: {class_count}")
            total_tests += test_count
            total_classes += class_count

        total_files += 1

    # Check factory file
    factory_file = test_dir / "fixtures" / "factories.py"
    if factory_file.exists():
        print(f"\n📄 {factory_file.relative_to(test_dir.parent)}")
        valid, error = validate_python_file(factory_file)
        if valid:
            print(f"   ✓ Syntax: Valid")
            total_files += 1
        else:
            print(f"   ❌ Syntax Error: {error}")
            errors.append((str(factory_file), error))

    # Summary
    print("\n" + "=" * 60)
    print("\n📊 Test Suite Summary:")
    print(f"   • Test Files: {total_files}")
    print(f"   • Test Classes: {total_classes}")
    print(f"   • Test Methods: {total_tests}")
    print(f"   • Syntax Errors: {len(errors)}")

    if errors:
        print("\n❌ Errors Found:")
        for filename, error in errors:
            print(f"   • {filename}: {error}")
        return 1

    print("\n✅ All tests validated successfully!")
    print(f"\n🎯 Test Coverage Target: 80%")
    print(f"   Estimated tests written: {total_tests}")
    print(f"   Expected minimum: 100")

    if total_tests >= 100:
        print(f"   ✓ Test count meets requirements")
    else:
        print(f"   ⚠ Test count below recommended minimum")

    # Check for required test files
    print("\n📋 Required Test Files:")
    required_files = [
        "test_models.py",
        "test_api.py",
        "test_forms.py",
        "test_utils.py",
        "test_providers.py",
        "test_management_commands.py",
        "conftest.py",
    ]

    for required in required_files:
        filepath = test_dir / required
        if filepath.exists():
            print(f"   ✓ {required}")
        else:
            print(f"   ❌ {required} (missing)")

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
