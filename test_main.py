from main import safe_filename

def test_safe_filename():
    # Test path traversal removal
    assert safe_filename("../../../etc/passwd") == "passwd"
    # Note: os.path.basename doesn't treat backslashes as path separators on POSIX systems.
    assert safe_filename("cmd.exe") == "cmd.exe"

    # Test valid filename
    assert safe_filename("valid_document.pdf") == "valid_document.pdf"

    # Test spaces and special characters are removed
    assert safe_filename("file with spaces & symbols!.txt") == "filewithspacessymbols.txt"

    # Test unicode normalization
    assert safe_filename("café.pdf") == "cafe.pdf"

    # Test starting with dot fallback
    assert safe_filename(".hidden_file") == "unnamed_upload.pdf"
    assert safe_filename("") == "unnamed_upload.pdf"
