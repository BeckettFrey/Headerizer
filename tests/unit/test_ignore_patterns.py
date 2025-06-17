# File: tests/unit/test_ignore_patterns.py
import tempfile
from pathlib import Path
from headerizer.utils import should_ignore, load_headerignore

class TestIgnorePatterns:
    """Test file/directory ignoring functionality"""
    
    def test_should_ignore_basic_patterns(self):
        """Test basic glob pattern matching"""
        root = Path("/project")
        patterns = ["*.min.js", "node_modules", "build"]
        
        # Should ignore
        assert should_ignore(Path("/project/app.min.js"), root, patterns)
        assert should_ignore(Path("/project/node_modules/lib.js"), root, patterns)
        assert should_ignore(Path("/project/build/output.js"), root, patterns)
        
        # Should not ignore
        assert not should_ignore(Path("/project/src/app.js"), root, patterns)
        assert not should_ignore(Path("/project/README.md"), root, patterns)
    
    def test_should_ignore_nested_directories(self):
        """Test ignoring files in nested directories"""
        root = Path("/project")
        patterns = ["node_modules", "*.log"]
        
        # Nested node_modules
        assert should_ignore(Path("/project/src/node_modules/lib.js"), root, patterns)
        assert should_ignore(Path("/project/deep/nested/node_modules/file.txt"), root, patterns)
        
        # Log files at various depths
        assert should_ignore(Path("/project/app.log"), root, patterns)
        assert should_ignore(Path("/project/logs/error.log"), root, patterns)
        assert should_ignore(Path("/project/src/debug/trace.log"), root, patterns)
    
    def test_should_ignore_wildcard_patterns(self):
        """Test various wildcard patterns"""
        root = Path("/project")
        patterns = ["*.min.*", "test_*", "*temp*"]
        
        # Multiple extension wildcards
        assert should_ignore(Path("/project/app.min.js"), root, patterns)
        assert should_ignore(Path("/project/style.min.css"), root, patterns)
        
        # Prefix patterns
        assert should_ignore(Path("/project/test_utils.py"), root, patterns)
        assert should_ignore(Path("/project/test_integration.py"), root, patterns)
        
        # Contains patterns
        assert should_ignore(Path("/project/tempfile.txt"), root, patterns)
        assert should_ignore(Path("/project/data_temp_backup.sql"), root, patterns)
    
    def test_should_ignore_directory_patterns(self):
        """Test directory-specific ignore patterns"""
        root = Path("/project")
        patterns = ["build", "dist", "__pycache__"]
        
        # Direct directory matches
        assert should_ignore(Path("/project/build/main.js"), root, patterns)
        assert should_ignore(Path("/project/dist/bundle.css"), root, patterns)
        assert should_ignore(Path("/project/__pycache__/module.pyc"), root, patterns)
        
        # Nested directory matches
        assert should_ignore(Path("/project/src/build/output.txt"), root, patterns)
        assert should_ignore(Path("/project/lib/dist/package.json"), root, patterns)
    
    def test_should_ignore_empty_patterns(self):
        """Test handling empty or None patterns"""
        root = Path("/project")
        
        # Empty list
        assert not should_ignore(Path("/project/any_file.py"), root, [])
        
        # None patterns
        assert not should_ignore(Path("/project/any_file.py"), root, None)
    
    def test_should_ignore_relative_path_error(self):
        """Test handling files outside project root"""
        root = Path("/project")
        patterns = ["*.log"]
        
        # File outside root should not be ignored (returns False on ValueError)
        outside_file = Path("/other_project/file.log")
        assert not should_ignore(outside_file, root, patterns)
    
    def test_load_headerignore_file(self):
        """Test loading patterns from .headerignore file"""
        ignore_content = """# Comment line
node_modules
*.min.js
build

# Another comment
dist
*.pyc"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ignore_file = tmpdir_path / ".headerignore"
            ignore_file.write_text(ignore_content)
            
            patterns = load_headerignore(tmpdir_path)
            expected = ["node_modules", "*.min.js", "build", "dist", "*.pyc"]
            assert patterns == expected
    
    def test_load_headerignore_with_extra_patterns(self):
        """Test combining .headerignore with extra patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ignore_file = tmpdir_path / ".headerignore"
            ignore_file.write_text("node_modules\n*.min.js")
            
            patterns = load_headerignore(tmpdir_path, extra_patterns=["*.log", "temp"])
            
            # Should contain both file patterns and extra patterns
            assert "node_modules" in patterns
            assert "*.min.js" in patterns
            assert "*.log" in patterns
            assert "temp" in patterns
    
    def test_load_headerignore_missing_file(self):
        """Test handling missing .headerignore file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            # No .headerignore file created
            
            patterns = load_headerignore(tmpdir_path)
            assert patterns == []
            
            # With extra patterns
            patterns = load_headerignore(tmpdir_path, extra_patterns=["*.log"])
            assert patterns == ["*.log"]
    
    def test_load_headerignore_empty_file(self):
        """Test handling empty .headerignore file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ignore_file = tmpdir_path / ".headerignore"
            ignore_file.write_text("")
            
            patterns = load_headerignore(tmpdir_path)
            assert patterns == []
    
    def test_load_headerignore_whitespace_handling(self):
        """Test proper whitespace handling in .headerignore"""
        ignore_content = """  node_modules  
*.min.js
  
build
	dist	"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ignore_file = tmpdir_path / ".headerignore"
            ignore_file.write_text(ignore_content)
            
            patterns = load_headerignore(tmpdir_path)
            # Should strip whitespace and skip empty lines
            expected = ["node_modules", "*.min.js", "build", "dist"]
            assert patterns == expected
    
    def test_load_headerignore_comments_only(self):
        """Test .headerignore file with only comments"""
        ignore_content = """# This is a comment
# Another comment
# Yet another comment"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ignore_file = tmpdir_path / ".headerignore"
            ignore_file.write_text(ignore_content)
            
            patterns = load_headerignore(tmpdir_path)
            assert patterns == []
    
    def test_load_headerignore_error_handling(self):
        """Test error handling when reading .headerignore fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            ignore_file = tmpdir_path / ".headerignore"
            ignore_file.write_text("node_modules")
            
            # Make file unreadable (simulate permission error)
            ignore_file.chmod(0o000)
            
            try:
                # Should not raise exception, should return empty list or extra patterns
                patterns = load_headerignore(tmpdir_path, extra_patterns=["*.log"])
                assert "*.log" in patterns  # Extra patterns should still work
            finally:
                # Restore permissions for cleanup
                ignore_file.chmod(0o644)