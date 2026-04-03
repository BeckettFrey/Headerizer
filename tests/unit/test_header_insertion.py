# File: tests/unit/test_header_insertion.py
from pathlib import Path
from unittest.mock import patch, mock_open
from headerizer.processor import add_header_to_file

class TestHeaderInsertion:
    """Test core header insertion functionality"""
    
    def test_add_new_header(self):
        """Test adding header to file without existing header"""
        content = "print('hello world')\n"
        expected = "# File: /path/to/test.py\nprint('hello world')\n"
        
        with patch('builtins.open', mock_open(read_data=content)) as mock_file:
            result = add_header_to_file(
                Path("test.py"), 
                {}, 
                "/path/to/test.py", 
                "# "
            )
            
            mock_file().write.assert_called_once_with(expected)
            assert result == "written"
    
    def test_update_existing_header(self):
        """Test updating existing header when path format changes"""
        content = "# File: test.py\nprint('hello world')\n"
        expected = "# File: /absolute/path/test.py\nprint('hello world')\n"
        
        with patch('builtins.open', mock_open(read_data=content)) as mock_file:
            result = add_header_to_file(
                Path("test.py"), 
                {}, 
                "/absolute/path/test.py", 
                "# "
            )
            
            mock_file().write.assert_called_once_with(expected)
            assert result == "written"
    
    def test_skip_identical_header(self):
        """Test skipping when header is already correct"""
        content = "# File: /path/to/test.py\nprint('hello world')\n"
        
        with patch('builtins.open', mock_open(read_data=content)) as mock_file:
            result = add_header_to_file(
                Path("test.py"), 
                {}, 
                "/path/to/test.py", 
                "# "
            )
            
            # Should not write since content is unchanged
            mock_file().write.assert_not_called()
            assert result == "skipped"
    
    def test_different_comment_styles(self):
        """Test different comment prefixes for different file types"""
        test_cases = [
            ("test.py", "# ", "# File: test.py\ncode\n"),
            ("test.js", "// ", "// File: test.js\ncode\n"),
            ("test.sql", "-- ", "-- File: test.sql\ncode\n"),
            ("test.html", "<!-- ", "<!-- File: test.html -->\ncode\n"),
        ]
        
        for filename, prefix, expected in test_cases:
            with patch('builtins.open', mock_open(read_data="code\n")):
                result = add_header_to_file(
                    Path(filename), 
                    {}, 
                    filename, 
                    prefix
                )
                assert result == "written"
    
    def test_preserve_file_ending_newlines(self):
        """Test preserving original file newline endings"""
        # File with newline at end
        content_with_newline = "print('hello')\n"
        expected_with_newline = "# File: test.py\nprint('hello')\n"
        
        with patch('builtins.open', mock_open(read_data=content_with_newline)) as mock_file:
            add_header_to_file(Path("test.py"), {}, "test.py", "# ")
            mock_file().write.assert_called_once_with(expected_with_newline)
        
        # File without newline at end
        content_no_newline = "print('hello')"
        expected_no_newline = "# File: test.py\nprint('hello')"
        
        with patch('builtins.open', mock_open(read_data=content_no_newline)) as mock_file:
            add_header_to_file(Path("test.py"), {}, "test.py", "# ")
            mock_file().write.assert_called_once_with(expected_no_newline)
    
    def test_header_detection_in_first_three_lines(self):
        """Test that existing headers are detected within first 3 lines only"""
        # Header in line 2 should be updated
        content_line2 = "#!/usr/bin/env python\n# File: old/path.py\nprint('hello')\n"
        expected_line2 = "#!/usr/bin/env python\n# File: new/path.py\nprint('hello')\n"
        
        with patch('builtins.open', mock_open(read_data=content_line2)) as mock_file:
            result = add_header_to_file(Path("test.py"), {}, "new/path.py", "# ")
            mock_file().write.assert_called_once_with(expected_line2)
            assert result == "written"
        
        # "File:" in line 4 should be ignored, new header added to top
        content_line4 = "line1\nline2\nline3\n# File: should/ignore.py\nprint('hello')\n"
        expected_line4 = "# File: new/path.py\nline1\nline2\nline3\n# File: should/ignore.py\nprint('hello')\n"
        
        with patch('builtins.open', mock_open(read_data=content_line4)) as mock_file:
            result = add_header_to_file(Path("test.py"), {}, "new/path.py", "# ")
            mock_file().write.assert_called_once_with(expected_line4)
            assert result == "written"
    
    def test_error_handling(self):
        """Test error handling during file processing"""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = add_header_to_file(Path("test.py"), {}, "test.py", "# ")
            assert result == "error"
    
    def test_shebang_handling(self):
        """Test that headers are inserted after shebang lines"""
        # Shell script with shebang - header should go after shebang
        shell_content = "#!/bin/bash\necho 'hello'\n"
        expected_shell = "#!/bin/bash\n# File: scripts/deploy.sh\necho 'hello'\n"
        
        with patch('builtins.open', mock_open(read_data=shell_content)) as mock_file:
            result = add_header_to_file(Path("scripts/deploy.sh"), {}, "scripts/deploy.sh", "# ")
            mock_file().write.assert_called_once_with(expected_shell)
            assert result == "written"
        
        # Python script with shebang - header should go after shebang
        py_content = "#!/usr/bin/env python3\nprint('hello')\n"
        expected_py = "#!/usr/bin/env python3\n# File: test.py\nprint('hello')\n"
        
        with patch('builtins.open', mock_open(read_data=py_content)) as mock_file:
            result = add_header_to_file(Path("test.py"), {}, "test.py", "# ")
            mock_file().write.assert_called_once_with(expected_py)
            assert result == "written"
        
        # Existing header after shebang should be updated
        existing_header_content = "#!/bin/bash\n# File: old/path.sh\necho 'hello'\n"
        expected_updated = "#!/bin/bash\n# File: new/path.sh\necho 'hello'\n"
        
        with patch('builtins.open', mock_open(read_data=existing_header_content)) as mock_file:
            result = add_header_to_file(Path("scripts/deploy.sh"), {}, "new/path.sh", "# ")
            mock_file().write.assert_called_once_with(expected_updated)
            assert result == "written"