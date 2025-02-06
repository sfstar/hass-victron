"""popBuffer."""

from typing import Any


class PopBuffer:
    """A buffer wrapper class that allows for positional awareness in buffer for decoding register data."""

    def __init__(self, size: int) -> None:
        """Buffer wrapper class that allows for positional awareness in buffer for decoding register data.

        :param size: Size of the buffer
        """
        self.buffer = [None] * size
        self.size: int = size
        self.position = 0

    def get_item_in_buffer(self, data_type: Any) -> None:
        """Get the item in the buffer.

        :param data_type: buffer item
        :return:
        """
        # TODO: decomment
        # match data_type:
        #     case UINT16:
        #     # Handle UINT16
        #         pass
        #     case UINT32:
        #     # Handle UINT32
        #         pass
        #     case INT16:
        #     # Handle INT16
        #         pass
        #     case INT32:
        #     # Handle INT32
        #         pass
        #     case _:
        #         raise ValueError(f"Unsupported data type: {data_type}")
        item = self.buffer[self.position]
        self.position += 1
        return item
