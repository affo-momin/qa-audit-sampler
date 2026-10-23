import unittest

from audit_sampler import coverage, sample


def make_rows():
    rows = []
    for i in range(100):
        rows.append({"task_id": f"t{i:03}", "annotator": "ann_a" if i < 70 else "ann_b",
                     "label": "spam" if i % 10 == 0 else "ham"})
    return rows


class TestSampler(unittest.TestCase):
    def test_every_group_is_covered(self):
        rows = make_rows()
        picked = sample(rows, rate=0.05, min_per_group=2)
        for field in ("annotator", "label"):
            for chosen, total in coverage(rows, picked, field).values():
                self.assertGreater(chosen, 0)

    def test_same_seed_same_sample(self):
        rows = make_rows()
        self.assertEqual(sample(rows, seed=7), sample(rows, seed=7))
        self.assertNotEqual(sample(rows, seed=7), sample(rows, seed=8))

    def test_small_group_taken_whole(self):
        rows = [{"task_id": "1", "annotator": "x", "label": "rare"}]
        self.assertEqual(len(sample(rows, min_per_group=5)), 1)

    def test_rate_respected(self):
        rows = make_rows()
        # ann_a/ham has 63 rows -> ceil(0.2 * 63) = 13
        picked = sample(rows, rate=0.2, min_per_group=1)
        n = sum(1 for r in picked if r["annotator"] == "ann_a" and r["label"] == "ham")
        self.assertEqual(n, 13)

    def test_bad_rate(self):
        with self.assertRaises(ValueError):
            sample(make_rows(), rate=0)


if __name__ == "__main__":
    unittest.main()
