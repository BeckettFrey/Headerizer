#!/bin/bash


# Run from project root (one level higher than script directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 Running tests..."


# Ensure PYTHONPATH includes the current directory
export PYTHONPATH="$PROJECT_ROOT"

# Run pytest with any additional args passed to this script
pytest tests "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All tests passed."
else
  echo "❌ Some tests failed."
fi

exit $EXIT_CODE
