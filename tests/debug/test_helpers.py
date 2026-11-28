import pytest

from platformio.debug.helpers import escape_gdbmi_stream


@pytest.mark.parametrize(
    "stream, expected",
    [
        ("GDB server started", '@"GDB server started"\n'),
        ("GDB server started\n", '@"GDB server started\\n"\n'),
    ],
)
def test_escape_gdbmi_stream_terminates_each_record(stream, expected):
    assert escape_gdbmi_stream("@", stream) == expected
