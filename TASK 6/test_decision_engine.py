"""
Test Suite — Decision Engine
Validates rule-based logic, thresholds, and stopping conditions.
"""

import unittest
from decision_engine import DecisionEngine, DecisionResult, Action, Adjustment, DifficultyLevel


class TestDecisionEngine(unittest.TestCase):
    """Comprehensive test suite for DecisionEngine."""
    
    def setUp(self):
        """Create fresh engine for each test."""
        self.engine = DecisionEngine("test-session-001")
    
    def test_initial_state(self):
        """Verify initial engine state."""
        self.assertEqual(self.engine.current_difficulty, DifficultyLevel.EASY)
        self.assertEqual(self.engine.question_count, 0)
        self.assertEqual(self.engine.low_score_streak, 0)
        self.assertEqual(len(self.engine.score_history), 0)
    
    def test_difficulty_increase_easy_to_medium(self):
        """Score > 0.70 from Easy should go to Medium."""
        result = self.engine.evaluate(0.80)
        
        self.assertEqual(result.difficulty, DifficultyLevel.MEDIUM)
        self.assertEqual(result.difficulty_adjustment, Adjustment.INCREASE)
        self.assertEqual(result.next_action, Action.CONTINUE)
        self.assertIn("increased", result.reason.lower())
    
    def test_difficulty_increase_medium_to_hard(self):
        """Score > 0.70 from Medium should go to Hard."""
        self.engine.current_difficulty = DifficultyLevel.MEDIUM
        result = self.engine.evaluate(0.75)
        
        self.assertEqual(result.difficulty, DifficultyLevel.HARD)
        self.assertEqual(result.difficulty_adjustment, Adjustment.INCREASE)
    
    def test_difficulty_maintain_at_hard_boundary(self):
        """Score > 0.70 at Hard should maintain (cannot increase beyond Hard)."""
        self.engine.current_difficulty = DifficultyLevel.HARD
        result = self.engine.evaluate(0.85)
        
        self.assertEqual(result.difficulty, DifficultyLevel.HARD)
        self.assertEqual(result.difficulty_adjustment, Adjustment.MAINTAIN)
    
    def test_difficulty_decrease_hard_to_medium(self):
        """Score < 0.40 from Hard should go to Medium."""
        self.engine.current_difficulty = DifficultyLevel.HARD
        result = self.engine.evaluate(0.30)
        
        self.assertEqual(result.difficulty, DifficultyLevel.MEDIUM)
        self.assertEqual(result.difficulty_adjustment, Adjustment.DECREASE)
        self.assertIn("decreased", result.reason.lower())
    
    def test_difficulty_decrease_medium_to_easy(self):
        """Score < 0.40 from Medium should go to Easy."""
        self.engine.current_difficulty = DifficultyLevel.MEDIUM
        result = self.engine.evaluate(0.35)
        
        self.assertEqual(result.difficulty, DifficultyLevel.EASY)
        self.assertEqual(result.difficulty_adjustment, Adjustment.DECREASE)
    
    def test_difficulty_maintain_at_easy_boundary(self):
        """Score < 0.40 at Easy should maintain (cannot decrease below Easy)."""
        self.engine.current_difficulty = DifficultyLevel.EASY
        result = self.engine.evaluate(0.30)
        
        self.assertEqual(result.difficulty, DifficultyLevel.EASY)
        self.assertEqual(result.difficulty_adjustment, Adjustment.MAINTAIN)
    
    def test_difficulty_maintain_middle_range(self):
        """Score between 0.40-0.70 should maintain difficulty."""
        test_scores = [0.40, 0.50, 0.60, 0.70]
        
        for score in test_scores:
            with self.subTest(score=score):
                engine = DecisionEngine(f"test-{score}")
                engine.current_difficulty = DifficultyLevel.MEDIUM
                result = engine.evaluate(score)
                
                self.assertEqual(result.difficulty, DifficultyLevel.MEDIUM)
                self.assertEqual(result.difficulty_adjustment, Adjustment.MAINTAIN)
                self.assertIn("maintained", result.reason.lower())
    
    def test_stopping_consecutive_low_scores(self):
        """2 consecutive scores < 0.40 should stop session."""
        # First low score
        result1 = self.engine.evaluate(0.30)
        self.assertEqual(result1.next_action, Action.CONTINUE)
        self.assertEqual(result1.low_score_streak, 1)
        
        # Second consecutive low score
        result2 = self.engine.evaluate(0.20)
        self.assertEqual(result2.next_action, Action.END)
        self.assertEqual(result2.low_score_streak, 2)
        self.assertIn("struggling", result2.reason.lower())
    
    def test_stopping_max_questions(self):
        """10 questions should trigger session end."""
        engine = DecisionEngine("test-max", max_questions=3)
        
        # Questions 1-3 (at limit)
        engine.evaluate(0.80)  # Q1
        engine.evaluate(0.75)  # Q2
        result = engine.evaluate(0.70)  # Q3 - should stop
        
        self.assertEqual(result.question_number, 3)
        self.assertEqual(result.next_action, Action.END)
        self.assertIn("Maximum question limit", result.reason)
    
    def test_low_score_streak_reset(self):
        """Good score should reset low score streak."""
        self.engine.evaluate(0.30)  # Low
        self.engine.evaluate(0.80)  # Good - resets streak
        
        self.assertEqual(self.engine.low_score_streak, 0)
        
        result = self.engine.evaluate(0.30)  # Low again
        self.assertEqual(result.low_score_streak, 1)
        self.assertEqual(result.next_action, Action.CONTINUE)
    
    def test_score_validation(self):
        """Invalid scores should raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.evaluate(1.5)
        
        with self.assertRaises(ValueError):
            self.engine.evaluate(-0.1)
    
    def test_question_count_increment(self):
        """Each evaluation should increment question count."""
        for i in range(1, 6):
            result = self.engine.evaluate(0.80)
            self.assertEqual(result.question_number, i)
    
    def test_score_history_tracking(self):
        """All scores should be recorded in history."""
        scores = [0.80, 0.75, 0.30, 0.90]
        
        for score in scores:
            self.engine.evaluate(score)
        
        self.assertEqual(self.engine.score_history, scores)
    
    def test_session_summary(self):
        """Session summary should reflect current state."""
        self.engine.evaluate(0.80)
        self.engine.evaluate(0.30)
        
        summary = self.engine.get_session_summary()
        
        self.assertEqual(summary["session_id"], "test-session-001")
        self.assertEqual(summary["question_count"], 2)
        self.assertEqual(summary["low_score_streak"], 1)
        self.assertEqual(len(summary["score_history"]), 2)
    
    def test_reason_clarity(self):
        """All decisions should include clear human-readable reasons."""
        # Increase
        result_inc = self.engine.evaluate(0.85)
        self.assertIn("Strong answer", result_inc.reason)
        
        # Decrease
        engine2 = DecisionEngine("test-dec")
        engine2.current_difficulty = DifficultyLevel.MEDIUM
        result_dec = engine2.evaluate(0.30)
        self.assertIn("Weak answer", result_dec.reason)
        
        # Maintain
        engine3 = DecisionEngine("test-maint")
        engine3.current_difficulty = DifficultyLevel.MEDIUM
        result_maint = engine3.evaluate(0.55)
        self.assertIn("Adequate answer", result_maint.reason)


class TestScenarioWorkflow(unittest.TestCase):
    """End-to-end scenario test matching project requirements."""
    
    def test_scenario_provided_in_requirements(self):
        """
        Test the exact scenario from project requirements:
        Scores: [0.8, 0.75, 0.3, 0.2, 0.9]
        
        Expected:
        Q1: 0.80 → continue → Easy → Medium
        Q2: 0.75 → continue → Medium → Hard
        Q3: 0.30 → continue → Hard → Medium
        Q4: 0.20 → end → Medium → Easy
        Q5: 0.90 → end (already stopped)
        """
        engine = DecisionEngine("scenario-test")
        scores = [0.8, 0.75, 0.3, 0.2, 0.9]
        
        # Q1: 0.80
        result1 = engine.evaluate(scores[0])
        self.assertEqual(result1.next_action, Action.CONTINUE)
        self.assertEqual(result1.difficulty, DifficultyLevel.MEDIUM)
        self.assertEqual(result1.difficulty_adjustment, Adjustment.INCREASE)
        self.assertEqual(result1.question_number, 1)
        print(f"Q1: score={scores[0]} → {result1.difficulty.value} ({result1.difficulty_adjustment.value})")
        
        # Q2: 0.75
        result2 = engine.evaluate(scores[1])
        self.assertEqual(result2.next_action, Action.CONTINUE)
        self.assertEqual(result2.difficulty, DifficultyLevel.HARD)
        self.assertEqual(result2.difficulty_adjustment, Adjustment.INCREASE)
        self.assertEqual(result2.question_number, 2)
        print(f"Q2: score={scores[1]} → {result2.difficulty.value} ({result2.difficulty_adjustment.value})")
        
        # Q3: 0.30
        result3 = engine.evaluate(scores[2])
        self.assertEqual(result3.next_action, Action.CONTINUE)
        self.assertEqual(result3.difficulty, DifficultyLevel.MEDIUM)
        self.assertEqual(result3.difficulty_adjustment, Adjustment.DECREASE)
        self.assertEqual(result3.question_number, 3)
        self.assertEqual(result3.low_score_streak, 1)
        print(f"Q3: score={scores[2]} → {result3.difficulty.value} ({result3.difficulty_adjustment.value})")
        
        # Q4: 0.20
        result4 = engine.evaluate(scores[3])
        self.assertEqual(result4.next_action, Action.END)
        self.assertEqual(result4.difficulty, DifficultyLevel.EASY)  # Decreased from Medium
        self.assertEqual(result4.difficulty_adjustment, Adjustment.DECREASE)
        self.assertEqual(result4.question_number, 4)
        self.assertEqual(result4.low_score_streak, 2)
        self.assertIn("struggling", result4.reason.lower())
        print(f"Q4: score={scores[3]} → {result4.next_action.value} ({result4.reason})")
        
        # Session stopped - Q5 would not be processed in real scenario
        print("\n✓ Scenario workflow validated successfully")


def run_demo():
    """Run interactive demo of the decision engine."""
    print("\n" + "="*60)
    print("DECISION ENGINE — INTERACTIVE DEMO")
    print("="*60)
    
    engine = DecisionEngine("demo-session")
    
    # Scenario from requirements
    scores = [0.8, 0.75, 0.3, 0.2, 0.9]
    
    print(f"\nInput Scores: {scores}")
    print(f"Thresholds: Increase > 0.70 | Decrease < 0.40 | Max Questions: 10")
    print(f"Stopping: 2 consecutive < 0.40")
    print("\n" + "-"*60)
    
    for i, score in enumerate(scores, 1):
        result = engine.evaluate(score)
        
        print(f"\nQ{i}: Score = {score:.2f}")
        print(f"   Action: {result.next_action.value.upper()}")
        print(f"   Difficulty: {result.difficulty.value} (adjustment: {result.difficulty_adjustment.value})")
        print(f"   Reason: {result.reason}")
        
        if result.next_action == Action.END:
            print(f"\n{'='*60}")
            print("SESSION STOPPED")
            print(f"{'='*60}")
            break
    
    print(f"\nFinal State:")
    summary = engine.get_session_summary()
    print(f"  Questions Asked: {summary['question_count']}")
    print(f"  Final Difficulty: {summary['current_difficulty']}")
    print(f"  Score History: {summary['score_history']}")
    print(f"  Low Score Streak: {summary['low_score_streak']}")


if __name__ == "__main__":
    # Run demo first
    run_demo()
    
    # Run unit tests
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60 + "\n")
    unittest.main(verbosity=2, exit=False)
