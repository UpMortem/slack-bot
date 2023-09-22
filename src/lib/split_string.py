import unittest


def split_string_into_chunks(s, chunk_size):
    chunks = [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]
    return [
        "{} ({}/{})".format(chunk, i + 1, len(chunks)) for i, chunk in enumerate(chunks)
    ]


class TestSplitString(unittest.TestCase):
    def test_split_string_into_chunks(self):
        self.assertEqual(
            split_string_into_chunks("This is a test string.", 4),
            [
                "This (1/6)",
                " is (2/6)",
                " a t (3/6)",
                "est s (4/6)",
                "trin (5/6)",
                "g. (6/6)",
            ],
        )
        self.assertEqual(
            split_string_into_chunks("Another test.", 7),
            ["Another (1/2)", " test. (2/2)"],
        )
        self.assertEqual(
            split_string_into_chunks("Singleword", 5), ["Singl (1/2)", "eword (2/2)"]
        )
        self.assertEqual(
            split_string_into_chunks("", 5), [" (1/1)"]
        )  # Empty string test
        self.assertEqual(
            split_string_into_chunks("a b c d e f", 1),
            [
                "a (1/12)",
                " (2/12)",
                "b (3/12)",
                " (4/12)",
                "c (5/12)",
                " (6/12)",
                "d (7/12)",
                " (8/12)",
                "e (9/12)",
                " (10/12)",
                "f (11/12)",
                " (12/12)",
            ],
        )  # One-letter words


if __name__ == "__main__":
    unittest.main()
