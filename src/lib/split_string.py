import unittest

def split_string_into_chunks(s, chunk_size):
    words = s.split()
    chunks, chunk, chunk_length = [], "", 0
    for idx, word in enumerate(words):
        if chunk_length + len(word) + len(chunk.split()) > chunk_size and chunk:
            chunks.append(chunk)
            chunk, chunk_length = "", 0
        chunk += (" " + word if chunk else word)
        chunk_length += len(word)
    chunks.append(chunk)  # add last chunk
    return ["{} ({}/{})".format(chunk, i + 1, len(chunks)) for i, chunk in enumerate(chunks)]



class TestSplitString(unittest.TestCase):
    def test_split_string_into_chunks(self):
        self.assertEqual(split_string_into_chunks("This is a test string.", 4), ["This (1/4)", "is a (2/4)", "test (3/4)", "string. (4/4)"])
        self.assertEqual(split_string_into_chunks("Another test.", 7), ["Another (1/2)", "test. (2/2)"])
        self.assertEqual(split_string_into_chunks("Singleword", 5), ["Singleword (1/1)"])
        self.assertEqual(split_string_into_chunks("", 5), [" (1/1)"])  # Empty string test
        self.assertEqual(split_string_into_chunks("a b c d e f", 1), ["a (1/6)", "b (2/6)", "c (3/6)", "d (4/6)", "e (5/6)", "f (6/6)"])  # One-letter words

if __name__ == "__main__":
    unittest.main()
