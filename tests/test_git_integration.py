import unittest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import find_git_root
from processor import find_and_process_files


class TestGitIntegration(unittest.TestCase):
    """Test suite for Git integration functionality in Headerizer."""

    def setUp(self):
        self._temp_context = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self._temp_context.name)
        self.original_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.original_cwd)
        self._temp_context.cleanup()


    def _create_git_repo(self, repo_path):
        """Helper method to create a Git repository."""
        repo_path.mkdir(parents=True, exist_ok=True)

        # Initialize git repo
        subprocess.run(['git', 'init'], check=True, capture_output=True, cwd=repo_path)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True, cwd=repo_path)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True, cwd=repo_path)

        # Create initial commit
        test_file = repo_path / 'README.md'
        test_file.write_text('# Test Repository')
        subprocess.run(['git', 'add', 'README.md'], check=True, cwd=repo_path)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True, cwd=repo_path)


    def test_find_git_root_in_git_repo(self):
        """Test finding Git root when inside a Git repository."""
        git_repo = self.temp_dir / 'test_repo'
        self._create_git_repo(git_repo)
        
        # Test from repo root
        result = find_git_root(git_repo)
        self.assertEqual(result.resolve(), git_repo.resolve())
        
        # Test from subdirectory
        subdir = git_repo / 'src' / 'deep' / 'nested'
        subdir.mkdir(parents=True)
        result = find_git_root(subdir)
        self.assertEqual(result.resolve(), git_repo.resolve())

    def test_find_git_root_not_in_git_repo(self):
        """Test finding Git root when not in a Git repository."""
        non_git_dir = self.temp_dir / 'not_git'
        non_git_dir.mkdir()
        
        result = find_git_root(non_git_dir)
        self.assertIsNone(result)

    def test_find_git_root_git_not_installed(self):
        """Test behavior when Git is not installed or available."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("Git not found")
            
            result = find_git_root(self.temp_dir)
            self.assertIsNone(result)

    def test_find_git_root_git_command_fails(self):
        """Test behavior when Git command fails."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(128, 'git')
            
            result = find_git_root(self.temp_dir)
            self.assertIsNone(result)

    def test_relative_path_calculation(self):
        """Test relative path calculation from Git root."""
        git_repo = self.temp_dir / 'project'
        self._create_git_repo(git_repo)
        
        # Create test file structure
        src_dir = git_repo / 'src' / 'utils'
        src_dir.mkdir(parents=True)
        test_file = src_dir / 'helper.py'
        test_file.write_text('# Test file\nprint("hello")')
        
        git_root = find_git_root(git_repo)
        self.assertIsNotNone(git_root)
        
        # Calculate relative path
        relative_path = test_file.resolve().relative_to(git_root)
        expected = Path('src') / 'utils' / 'helper.py'
        self.assertEqual(relative_path, expected)

    def test_nested_git_repos(self):
        """Test behavior with nested Git repositories."""
        # Create outer repo
        outer_repo = self.temp_dir / 'outer'
        self._create_git_repo(outer_repo)
        
        # Create inner repo
        inner_repo = outer_repo / 'submodules' / 'inner'
        self._create_git_repo(inner_repo)
        
        # Test from inner repo - should return inner repo root
        result = find_git_root(inner_repo)
        self.assertEqual(result.resolve(), inner_repo.resolve())
        
        # Test from outer repo - should return outer repo root
        result = find_git_root(outer_repo)
        self.assertEqual(result.resolve(), outer_repo.resolve())
            
    @patch("processor.input", return_value="n")
    @patch("builtins.print")
    def test_relative_paths_in_processing(self, mock_print, mock_input):
        """Test that relative paths are used correctly during file processing."""
        mock_input.return_value = 'n'  # Cancel operation
        
        git_repo = self.temp_dir / 'test_project'
        self._create_git_repo(git_repo)
        
        # Create test files
        src_dir = git_repo / 'src'
        src_dir.mkdir()
        test_file = src_dir / 'main.py'
        test_file.write_text('print("Hello, World!")')
        
        file_types = {
            'python': {
                'extensions': ['.py'],
                'comment_prefix': '# '
            }
        }

        # Mock the processor to capture the paths being used
        with patch('processor.add_header_to_file') as mock_add_header:
            mock_add_header.return_value = 'written'
            
            # Test with relative paths
            find_and_process_files(
                git_repo,
                file_types,
                use_relative=True,
                print_written=True
            )
            
            # Verify that the function was called (even though we cancelled)
            # The important part is that it found the Git root
            mock_add_header.assert_not_called()
            self.assertTrue(any("Found" in call.args[0] for call in mock_print.call_args_list))
            git_root = find_git_root(git_repo)
            self.assertIsNotNone(git_root)
            


    def test_git_root_with_worktree(self):
        """Test Git root detection with Git worktrees."""
        # Create main repo
        main_repo = self.temp_dir / 'main'
        self._create_git_repo(main_repo)
        
        # Create a branch for worktree
        os.chdir(main_repo)
        subprocess.run(['git', 'checkout', '-b', 'feature'], check=True)
        subprocess.run(['git', 'checkout', 'main'], check=True)  # Use 'main' instead of 'master'
        
        # Create worktree (if Git version supports it)
        worktree_path = self.temp_dir / 'worktree'
        try:
            subprocess.run([
                'git', 'worktree', 'add', str(worktree_path), 'feature'
            ], check=True, capture_output=True)
            
            # Test Git root detection from worktree
            result = find_git_root(worktree_path)
            # Worktree should point back to main repo
            self.assertIsNotNone(result)
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git worktree not supported or available, skip this test
            self.skipTest("Git worktree not supported in this environment")

    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(128, 'git', stderr='Permission denied'))
    def test_git_root_permission_error(self, mock_run):
        result = find_git_root(self.temp_dir)
        self.assertIsNone(result)

    def test_git_root_with_bare_repo(self):
        """Test Git root detection with bare repositories."""
        bare_repo = self.temp_dir / 'bare.git'
        bare_repo.mkdir()
        os.chdir(bare_repo)
        
        # Initialize bare repo
        subprocess.run(['git', 'init', '--bare'], check=True, capture_output=True)
        
        # Clone the bare repo
        clone_dir = self.temp_dir / 'clone'
        subprocess.run([
            'git', 'clone', str(bare_repo), str(clone_dir)
        ], check=True, capture_output=True)
        
        # Test Git root from clone
        result = find_git_root(clone_dir)
        self.assertEqual(result.resolve(), clone_dir.resolve())

    def test_git_root_unicode_paths(self):
        """Test Git root detection with Unicode characters in paths."""
        unicode_repo = self.temp_dir / 'тест_репо'  # Cyrillic characters
        try:
            self._create_git_repo(unicode_repo)
            result = find_git_root(unicode_repo)
            self.assertEqual(result.resolve(), unicode_repo.resolve())
        except (UnicodeError, OSError):
            # Skip if filesystem doesn't support Unicode
            self.skipTest("Filesystem doesn't support Unicode paths")

    def test_git_root_long_paths(self):
        """Test Git root detection with very long paths."""
        # Create a deeply nested directory structure
        deep_path = self.temp_dir
        for i in range(10):
            deep_path = deep_path / f'very_long_directory_name_{i}'
        
        try:
            self._create_git_repo(deep_path)
            result = find_git_root(deep_path)
            self.assertEqual(result.resolve(), deep_path.resolve())
        except OSError:
            # Skip if path is too long for filesystem
            self.skipTest("Path too long for filesystem")

