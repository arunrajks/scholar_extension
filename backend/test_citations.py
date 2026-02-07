from models import ScholarlyPaper, Author
from services.citation_service import format_all_citations

def test_citation_engine():
    print("Testing citation engine...")
    
    # Test case 1: Normal paper
    paper1 = ScholarlyPaper(
        title="Evolution of Quantum Computing",
        authors=[Author(name="John Doe"), Author(name="Jane Smith")],
        year=2023,
        journal="Quantum Journal",
        volume="12",
        issue="3",
        pages="200-210",
        source_api="TestAPI"
    )
    print("Running test case 1...")
    format_all_citations(paper1)
    print("Test case 1 passed.")

    # Test case 2: No authors (Potential crash candidate)
    paper2 = ScholarlyPaper(
        title="Untitled Secret Document",
        authors=[],
        year=2024,
        source_api="Ghost"
    )
    print("Running test case 2 (No authors)...")
    format_all_citations(paper2)
    print("Test case 2 passed.")

    # Test case 3: Single name author
    paper3 = ScholarlyPaper(
        title="Mononym Study",
        authors=[Author(name="Aristotle")],
        year=-300,
        source_api="History"
    )
    print("Running test case 3 (Mononym)...")
    format_all_citations(paper3)
    print("Test case 3 passed.")

    # Test case 4: Missing journal/vol/issue
    paper4 = ScholarlyPaper(
        title="Preprint Alpha",
        authors=[Author(name="Alice Bob")],
        year=2025,
        source_api="arXiv"
    )
    # Test case 5: Empty author name (Potential crash candidate)
    paper5 = ScholarlyPaper(
        title="Empty Author Test",
        authors=[Author(name="")],
        year=2026,
        source_api="EdgeCase"
    )
    print("Running test case 5 (Empty author name)...")
    format_all_citations(paper5)
    print("Test case 5 passed.")

    print("All tests completed successfully!")

if __name__ == "__main__":
    test_citation_engine()
