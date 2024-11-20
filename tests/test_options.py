import os
import pytest
from unittest.mock import patch, MagicMock
from platformio.project.options import get_default_core_dir


@pytest.mark.parametrize("is_windows", [True, False])
@patch("platformio.project.options.os")
@patch("platformio.project.options.expanduser")
@patch("platformio.project.options.logging")
def test_get_default_core_dir(logging_mock, expanduser_mock, os_mock, is_windows):
    # Mock platform
    with patch("platformio.project.options.IS_WINDOWS", is_windows):
        # Set up mocks
        home_dir = "/mock/home" if not is_windows else "C:\\mock\\home"
        expanduser_mock.return_value = home_dir
        platformio_dir = os.path.join(home_dir, ".platformio")
        
        # Mock os behavior
        os_mock.path.join.side_effect = lambda a, b: os.path.join(a, b)
        os_mock.path.exists.return_value = False
        os_mock.makedirs.return_value = None
        os_mock.path.isdir.side_effect = lambda path: path == platformio_dir

        # Run the function
        result = get_default_core_dir()

        # Assertions
        os_mock.path.join.assert_called_with(home_dir, ".platformio")
        os_mock.makedirs.assert_called_with(platformio_dir, exist_ok=True)
        assert result == platformio_dir

        # Ensure no logging errors for non-Windows
        if not is_windows:
            logging_mock.error.assert_not_called()


