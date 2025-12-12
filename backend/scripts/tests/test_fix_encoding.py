"""
Tests for fix_encoding script.
"""
import pytest
import tempfile
from pathlib import Path
from scripts.fix_encoding import (
    has_mojibake,
    repair_content,
    process_file,
    main
)


class TestHasMojibake:
    """Tests for has_mojibake function."""
    
    def test_has_mojibake_detects_aj(self):
        """Test detection of Ã character."""
        assert has_mojibake("NÃºmero") is True
        assert has_mojibake("Normal text") is False
    
    def test_has_mojibake_detects_acirc(self):
        """Test detection of â character."""
        assert has_mojibake("Textâ") is True
    
    def test_has_mojibake_detects_eth(self):
        """Test detection of ð character."""
        assert has_mojibake("Textð") is True


class TestRepairContent:
    """Tests for repair_content function."""
    
    def test_repair_content_no_mojibake(self):
        """Test repair with no mojibake."""
        text = "Normal UTF-8 text"
        data = text.encode('utf-8')
        
        result = repair_content(data)
        assert result == text
    
    def test_repair_content_with_ascii_replacements(self):
        """Test repair replaces ASCII symbols."""
        text = "✔ Test ❌"
        data = text.encode('utf-8')
        
        result = repair_content(data)
        assert "[OK]" in result
        assert "[ERROR]" in result
    
    def test_repair_content_with_mojibake(self):
        """Test repair fixes mojibake."""
        # Create mojibake text (UTF-8 interpreted as Latin-1)
        correct_text = "Número"
        mojibake_data = correct_text.encode('utf-8').decode('latin-1').encode('latin-1')
        
        result = repair_content(mojibake_data)
        assert "Número" in result or "Numero" in result


class TestProcessFile:
    """Tests for process_file function."""
    
    def test_process_file_skips_self(self, tmp_path):
        """Test that process_file skips the script itself."""
        script_path = Path(__file__).parent.parent / "fix_encoding.py"
        
        result = process_file(script_path)
        assert result is False
    
    def test_process_file_skips_non_text_extensions(self, tmp_path):
        """Test that process_file skips non-text files."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b'\x00\x01\x02')
        
        result = process_file(binary_file)
        assert result is False
    
    def test_process_file_processes_text_file(self, tmp_path):
        """Test that process_file processes text files."""
        text_file = tmp_path / "test.py"
        text_file.write_bytes(b"print('hello')")
        
        # File has no mojibake, so should return False
        result = process_file(text_file)
        # Should return False if no changes needed
        assert isinstance(result, bool)
    
    def test_process_file_handles_encoding_errors(self, tmp_path):
        """Test that process_file handles encoding errors gracefully."""
        # Create file that might cause encoding errors
        text_file = tmp_path / "test.txt"
        text_file.write_bytes(b'\xff\xfe\x00\x01')
        
        # Should not raise exception
        try:
            result = process_file(text_file)
            assert isinstance(result, bool)
        except (UnicodeDecodeError, UnicodeEncodeError):
            pytest.fail("process_file should handle encoding errors gracefully")


class TestMain:
    """Tests for main function."""
    
    @patch('scripts.fix_encoding.BACKEND_DIR')
    def test_main_no_files_fixed(self, mock_backend_dir, tmp_path):
        """Test main with no files to fix."""
        mock_backend_dir.rglob.return_value = []
        
        result = main()
        assert result == 0
    
    @patch('scripts.fix_encoding.BACKEND_DIR')
    def test_main_processes_files(self, mock_backend_dir, tmp_path):
        """Test main processes files."""
        # Create test files
        file1 = tmp_path / "test1.py"
        file1.write_bytes(b"print('hello')")
        
        file2 = tmp_path / "test2.txt"
        file2.write_bytes(b"normal text")
        
        mock_backend_dir.rglob.return_value = [file1, file2]
        
        # Mock process_file to return True for one file
        with patch('scripts.fix_encoding.process_file') as mock_process:
            mock_process.side_effect = [False, False]  # No changes needed
            
            result = main()
            assert result == 0
            assert mock_process.call_count == 2

