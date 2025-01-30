from const.py import UINT16, INT16, UINT32, INT32, STRING


class PopBuffer:
    """A buffer wrapper class that allows for positional awareness in buffer for decoding register data."""

    def __init__(self, size):
        self.buffer = [None] * size
        self.size = size
        self.position = 0

    def getItemInBuffer(self, dataType):
        """Get the item in the buffer."""
        match dataType:
            case UINT16:
            # Handle UINT16
            pass
            case UINT32:
            # Handle UINT32
            pass
            case INT16:
            # Handle INT16
            pass
            case INT32:
            # Handle INT32
            pass
            case _:
            raise ValueError(f"Unsupported data type: {dataType}")
        item = self.buffer[self.position]
        self.position += 1
        return item
