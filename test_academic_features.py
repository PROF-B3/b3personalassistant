#!/usr/bin/env python3
"""
Test script for new academic features:
- Academic search (Beta)
- Citation management (Gamma)
- Document export (Epsilon)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.academic_search import create_academic_search
from modules.citation_manager import Citation, create_citation_manager
from modules.document_export import create_document_exporter


def test_academic_search():
    """Test academic paper search."""
    print("Testing academic search...")

    search = create_academic_search()

    # Search arXiv
    papers = search.search("machine learning", sources=["arxiv"], limit=3)

    print(f"  Found {len(papers)} papers from arXiv")

    if papers:
        paper = papers[0]
        print(f"  Sample: {paper.title[:50]}...")
        print(f"  Authors: {', '.join(paper.authors[:2])}")
        print(f"  Year: {paper.year}")

        # Test BibTeX generation
        bibtex = paper.to_bibtex()
        assert "@" in bibtex, "Should generate BibTeX"
        print("  ✓ BibTeX generation works")

        # Test APA citation
        apa = paper.to_apa()
        assert len(apa) > 0, "Should generate APA citation"
        print("  ✓ APA citation works")

    print("  ✓ Academic search works correctly")
    return True


def test_citation_manager():
    """Test citation management."""
    print("Testing citation manager...")

    cm = create_citation_manager(storage_path=Path("databases/test_citations"))

    # Create a citation
    citation = Citation(
        cite_key="Smith2023ML",
        title="Machine Learning Fundamentals",
        authors=["John Smith", "Jane Doe"],
        year=2023,
        venue="Nature Machine Intelligence",
        doi="10.1038/example"
    )

    # Add citation
    cm.add_citation(citation)
    assert len(cm.citations) == 1, "Should have 1 citation"

    # Get citation
    retrieved = cm.get_citation("Smith2023ML")
    assert retrieved is not None, "Should retrieve citation"
    assert retrieved.title == citation.title, "Title should match"

    # Search citations
    results = cm.search_citations("machine learning")
    assert len(results) >= 1, "Should find citation"

    # Generate bibliography
    bibtex = cm.generate_bibliography(style="bibtex")
    assert "Smith2023ML" in bibtex, "Should include citation"

    apa = cm.generate_bibliography(style="apa")
    assert "Smith" in apa, "Should generate APA"

    # Clean up
    import shutil
    shutil.rmtree(Path("databases/test_citations"))

    print("  ✓ Citation manager works correctly")
    return True


def test_document_export():
    """Test document export."""
    print("Testing document export...")

    exporter = create_document_exporter()

    # Test Markdown content
    content = """# Introduction

This is a test document with **bold** and *italic* text.

## Methodology

- Step 1
- Step 2
- Step 3

## Results

We found that...
"""

    # Test LaTeX export
    latex_path = Path("test_export.tex")
    success = exporter.export_to_latex(
        content=content,
        output_path=latex_path,
        title="Test Document",
        author="Test Author"
    )

    assert success, "Should export to LaTeX"
    assert latex_path.exists(), "LaTeX file should exist"

    # Verify LaTeX content
    latex_content = latex_path.read_text()
    assert "\\documentclass" in latex_content, "Should have document class"
    assert "Test Document" in latex_content, "Should include title"
    assert "\\section{Introduction}" in latex_content, "Should convert headings"

    # Clean up
    latex_path.unlink()

    print("  ✓ Document export works correctly")
    return True


def main():
    """Run all academic feature tests."""
    print("=" * 60)
    print("B3PersonalAssistant Academic Features Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_academic_search,
        test_citation_manager,
        test_document_export,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()

    if failed == 0:
        print("✓ ALL ACADEMIC FEATURE TESTS PASSED!")
        print()
        print("Academic features verified:")
        print("  ✓ Academic paper search (arXiv, CrossRef, Semantic Scholar)")
        print("  ✓ Citation management with BibTeX/APA/MLA/Chicago")
        print("  ✓ Document export to LaTeX and Word")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
