# External libraries
import pytest

if __name__ == "__main__":
    print("\n", "   Running all tests in the project...   ".center(150, "*"), "\n")
    pytest.main(["--verbose", "--color=yes", "--capture=no", "-k", "test_"])
