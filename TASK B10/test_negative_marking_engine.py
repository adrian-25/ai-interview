"""
Test Suite — Negative Marking Engine
Validates the scoring formula, edge cases, and determinism.
"""
import unittest

from negative_marking_engine import (
    NegativeMarkingEngine,
    InvalidScoreInputError,
    calculate_score,
    DEFAULT_PENALTY_PER_WRONG,
)


class TestNegativeMarkingEngine(unittest.TestCase):
    """Core behaviour of NegativeMarkingEngine."""

    def setUp(self):
        self.engine = NegativeMarkingEngine()

    def test_spec_example(self):
        """The exact example from the task spec: correct=8, wrong=2 -> 7.5"""
        result = self.engine.calculate(correct=8, wrong=2)
        self.assertEqual(result.final_score, 7.5)

    def test_zero_wrong_returns_full_score(self):
        result = self.engine.calculate(correct=10, wrong=0)
        self.assertEqual(result.final_score, 10)

    def test_zero_correct_with_wrong_answers(self):
        result = self.engine.calculate(correct=0, wrong=4)
        self.assertEqual(result.final_score, -1.0)

    def test_both_zero(self):
        result = self.engine.calculate(correct=0, wrong=0)
        self.assertEqual(result.final_score, 0)

    # --- Missing values ------------------------------------------------

    def test_missing_correct_defaults_to_zero(self):
        result = self.engine.calculate(correct=None, wrong=3)
        self.assertEqual(result.correct, 0)
        self.assertEqual(result.final_score, -0.75)

    def test_missing_wrong_defaults_to_zero(self):
        result = self.engine.calculate(correct=5, wrong=None)
        self.assertEqual(result.wrong, 0)
        self.assertEqual(result.final_score, 5)

    def test_both_missing_defaults_to_zero(self):
        result = self.engine.calculate()
        self.assertEqual(result.final_score, 0)

    # --- Negative final score (expected, not an error) -----------------

    def test_negative_final_score_is_allowed(self):
        result = self.engine.calculate(correct=1, wrong=20)
        self.assertLess(result.final_score, 0)
        self.assertEqual(result.final_score, round(1 - 20 * DEFAULT_PENALTY_PER_WRONG, 4))

    # --- Invalid inputs are rejected ------------------------------------

    def test_negative_correct_input_rejected(self):
        with self.assertRaises(InvalidScoreInputError):
            self.engine.calculate(correct=-1, wrong=2)

    def test_negative_wrong_input_rejected(self):
        with self.assertRaises(InvalidScoreInputError):
            self.engine.calculate(correct=2, wrong=-1)

    def test_non_numeric_input_rejected(self):
        with self.assertRaises(InvalidScoreInputError):
            self.engine.calculate(correct="eight", wrong=2)

    def test_boolean_input_rejected(self):
        # bool is technically an int subclass in Python — explicitly reject it
        with self.assertRaises(InvalidScoreInputError):
            self.engine.calculate(correct=True, wrong=2)

    # --- Configurable penalty -------------------------------------------

    def test_custom_penalty_per_wrong(self):
        engine = NegativeMarkingEngine(penalty_per_wrong=0.5)
        result = engine.calculate(correct=8, wrong=2)
        self.assertEqual(result.final_score, 7.0)

    def test_zero_penalty_means_no_negative_marking(self):
        engine = NegativeMarkingEngine(penalty_per_wrong=0)
        result = engine.calculate(correct=5, wrong=10)
        self.assertEqual(result.final_score, 5)

    def test_negative_penalty_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            NegativeMarkingEngine(penalty_per_wrong=-0.25)

    # --- Determinism ------------------------------------------------------

    def test_same_input_always_same_output(self):
        r1 = self.engine.calculate(correct=8, wrong=2)
        r2 = self.engine.calculate(correct=8, wrong=2)
        self.assertEqual(r1.final_score, r2.final_score)

    # --- Result shape -----------------------------------------------------

    def test_to_dict_matches_api_contract(self):
        result = self.engine.calculate(correct=8, wrong=2)
        self.assertEqual(result.to_dict(), {"final_score": 7.5})


class TestCalculateScoreConvenienceFunction(unittest.TestCase):
    """Functional-style helper used by simple callers/scripts."""

    def test_basic_usage(self):
        self.assertEqual(calculate_score(correct=8, wrong=2), {"final_score": 7.5})

    def test_defaults_with_no_args(self):
        self.assertEqual(calculate_score(), {"final_score": 0})

    def test_custom_penalty_override(self):
        self.assertEqual(calculate_score(correct=8, wrong=2, penalty_per_wrong=1.0), {"final_score": 6.0})


if __name__ == "__main__":
    unittest.main(verbosity=2)
