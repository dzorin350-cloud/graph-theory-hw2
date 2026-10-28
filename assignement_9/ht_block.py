"""Blocks of segments for the Hopcroft-Tarjan planarity test.

While a spine path is walked upwards, the segments leaving it are stored
in blocks.  A block keeps two lists of attachments (DFS numbers of the
vertices where its segments come back): the left one and the right one.
All the segments of the left list are drawn on one side of the spine, the
right ones on the other side, and flipping the block swaps both sides.
Each list is sorted in decreasing order: the head [0] is the highest
attachment and the tail [-1] the lowest one.
"""

from collections import deque


class Block:
    """A group of segments whose sides depend on each other."""

    def __init__(self, attachments):
        """Create a block from the attachments of one new segment."""
        self.left = attachments
        self.right = deque()

    def flip(self):
        """Move every segment of the block to the other side."""
        self.left, self.right = self.right, self.left

    def left_interlace(self, stack):
        """Return True if the block interlaces the left side of the top."""
        return (bool(stack) and bool(stack[-1].left)
                and self.left[-1] < stack[-1].left[0])

    def right_interlace(self, stack):
        """Return True if the block interlaces the right side of the top."""
        return (bool(stack) and bool(stack[-1].right)
                and self.left[-1] < stack[-1].right[0])

    def combine(self, other):
        """Merge a lower block into this one (they are now tied)."""
        self.left.extend(other.left)
        self.right.extend(other.right)

    def clean(self, height):
        """Drop attachments equal to height; True if the block is empty."""
        while self.left and self.left[0] == height:
            self.left.popleft()
        while self.right and self.right[0] == height:
            self.right.popleft()
        return not self.left and not self.right

    def add_to(self, attachments, low):
        """Append the block to the attachments of the enclosing segment.

        Only one side may keep attachments above low (the base of the
        spine), so the block is flipped to put that side on the left.
        """
        if self.right and self.right[0] > low:
            self.flip()
        attachments.extend(self.left)
        attachments.extend(self.right)
