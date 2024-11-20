import os
import logging
from platformio.fs import expanduser

# Custom exceptions
class PackageException(Exception):
    pass

class VCSBaseException(Exception):
    pass

# Function to get default core directory
def get_default_core_dir():
    # Default to ~/.platformio
    path = os.path.join(expanduser("~"), ".platformio")
    
    # Handle Windows-specific directory fallback (commented for non-Windows)
    # Uncomment this block if you're on Windows
    # if IS_WINDOWS:
    #     win_core_dir = os.path.splitdrive(path)[0] + "\\.platformio"
    #     if os.path.isdir(win_core_dir) and os.access(win_core_dir, os.W_OK):
    #         path = win_core_dir

    # Ensure the directory exists, but handle invalid symlink creation
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            logging.info(f"Created directory: {path}")
        except OSError as e:
            logging.error(f"Library Manager: Installing symlink: {path}")
            raise PackageException(f"Can not create a symbolic link for `{path}`, not a directory") from e

    if not os.path.isdir(path):
        logging.error(f"Library Manager: Installing symlink: {path}")
        raise VCSBaseException(f"VCS: Unknown repository type symlink: {path}")

    return path

# Set up logging configuration to display on the console
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all logs

# Test 1: Path does not exist and needs to be created
def test_create_directory():
    print("Test: Directory Creation")
    # Temporarily set an invalid path for testing purposes
    test_path = os.path.join(expanduser("~"), ".platformio_invalid")
    if os.path.exists(test_path):
        os.rmdir(test_path)  # Remove if exists

    try:
        result = get_default_core_dir()  # This should try to create the directory
        print(f"Directory created successfully at: {result}")
    except Exception as e:
        print(f"Expected exception: {e}")

# Test 2: Path exists but is not a directory (e.g., it's a file)
def test_invalid_directory():
    print("Test: Invalid Directory")
    # Temporarily set a path to a file (not a directory)
    test_path = os.path.join(expanduser("~"), ".platformio_invalid_file")
    if os.path.exists(test_path):
        os.remove(test_path)  # Remove if exists
    # Create a file in place of directory
    with open(test_path, 'w') as f:
        f.write("This is a test file")

    try:
        # This should now raise a VCSBaseException as it's not a directory
        result = get_default_core_dir()  
        print(f"Result: {result}")
    except VCSBaseException as e:
        print(f"Expected exception: {e}")
    except Exception as e:
        print(f"Unexpected exception: {e}")
    
    # Clean up
    os.remove(test_path)

# Run the tests
test_create_directory()
test_invalid_directory()
