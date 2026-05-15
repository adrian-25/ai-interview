"""
Decision Engine — Build System Thinking Logic
Core rule-based decision layer for AI Voice Interview System.

Determines difficulty adjustment, session continuation, and stopping conditions
based on evaluated candidate scores.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Adjustment(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


class Action(str, Enum):
    CONTINUE = "continue"
    END = "end"


@dataclass
class DecisionResult:
    """Result of a decision evaluation."""
    next_action: Action
    difficulty: DifficultyLevel
    difficulty_adjustment: Adjustment
    question_number: int
    reason: str
    low_score_streak: int
    session_id: str


class DecisionEngine:
    """
    Rule-based decision engine for interview flow control.
    
    Maintains session state including:
    - Question count
    - Score history
    - Consecutive low-score streak
    - Current difficulty level
    
    Thresholds:
    - score > 0.70 → increase difficulty
    - 0.40 <= score <= 0.70 → maintain difficulty
    - score < 0.40 → decrease difficulty
    
    Stopping Conditions:
    - 2 consecutive scores < 0.40 (struggle detection)
    - Maximum question limit reached (default: 10)
    """
    
    # Thresholds
    INCREASE_THRESHOLD = 0.70
    DECREASE_THRESHOLD = 0.40
    LOW_SCORE_THRESHOLD = 0.40
    MAX_QUESTIONS_DEFAULT = 10
    CONSECUTIVE_LOW_LIMIT = 2
    
    def __init__(self, session_id: str, max_questions: int = MAX_QUESTIONS_DEFAULT):
        self.session_id = session_id
        self.max_questions = max_questions
        self.current_difficulty = DifficultyLevel.EASY
        self.question_count = 0
        self.score_history: list[float] = []
        self.low_score_streak = 0
    
    def evaluate(self, score: float) -> DecisionResult:
        """
        Evaluate a candidate score and return the next decision.
        
        Args:
            score: Float between 0.0 and 1.0 representing answer quality
            
        Returns:
            DecisionResult containing next action, difficulty, and reasoning
        """
        # Validate score
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {score}")
        
        # Update tracking
        self.question_count += 1
        self.score_history.append(score)
        self._update_low_score_streak(score)
        
        # Check stopping conditions first
        should_stop, stop_reason = self._check_stopping_conditions()
        
        if should_stop:
            return DecisionResult(
                next_action=Action.END,
                difficulty=self.current_difficulty,
                difficulty_adjustment=Adjustment.MAINTAIN,
                question_number=self.question_count,
                reason=stop_reason,
                low_score_streak=self.low_score_streak,
                session_id=self.session_id
            )
        
        # Adjust difficulty based on score
        adjustment = self._adjust_difficulty(score)
        reason = self._get_reason(score, adjustment)
        
        return DecisionResult(
            next_action=Action.CONTINUE,
            difficulty=self.current_difficulty,
            difficulty_adjustment=adjustment,
            question_number=self.question_count,
            reason=reason,
            low_score_streak=self.low_score_streak,
            session_id=self.session_id
        )
    
    def _adjust_difficulty(self, score: float) -> Adjustment:
        """
        Determine difficulty adjustment based on score.
        
        Rules:
        - score > 0.70: increase difficulty
        - 0.40 <= score <= 0.70: maintain difficulty
        - score < 0.40: decrease difficulty
        
        Boundaries enforced: Easy (min) → Medium → Hard (max)
        """
        if score > self.INCREASE_THRESHOLD:
            return self._increase()
        elif score < self.DECREASE_THRESHOLD:
            return self._decrease()
        else:
            return Adjustment.MAINTAIN
    
    def _increase(self) -> Adjustment:
        """Increase difficulty if not already at maximum."""
        if self.current_difficulty == DifficultyLevel.EASY:
            self.current_difficulty = DifficultyLevel.MEDIUM
            return Adjustment.INCREASE
        elif self.current_difficulty == DifficultyLevel.MEDIUM:
            self.current_difficulty = DifficultyLevel.HARD
            return Adjustment.INCREASE
        else:
            # Already at HARD, cannot increase further
            return Adjustment.MAINTAIN
    
    def _decrease(self) -> Adjustment:
        """Decrease difficulty if not already at minimum."""
        if self.current_difficulty == DifficultyLevel.HARD:
            self.current_difficulty = DifficultyLevel.MEDIUM
            return Adjustment.DECREASE
        elif self.current_difficulty == DifficultyLevel.MEDIUM:
            self.current_difficulty = DifficultyLevel.EASY
            return Adjustment.DECREASE
        else:
            # Already at EASY, cannot decrease further
            return Adjustment.MAINTAIN
    
    def _update_low_score_streak(self, score: float) -> None:
        """
        Track consecutive low scores for struggle detection.
        
        Low score threshold: < 0.40
        Stopping trigger: 2 consecutive low scores
        """
        if score < self.LOW_SCORE_THRESHOLD:
            self.low_score_streak += 1
        else:
            self.low_score_streak = 0
    
    def _check_stopping_conditions(self) -> tuple[bool, str]:
        """
        Check if interview should stop.
        
        Priority 1: Consecutive low scores (candidate struggling)
        Priority 2: Maximum question limit reached
        
        Returns:
            (should_stop: bool, reason: str)
        """
        # Priority 1: Struggle detection
        if self.low_score_streak >= self.CONSECUTIVE_LOW_LIMIT:
            return True, f"2 consecutive low scores ({self.LOW_SCORE_THRESHOLD}) — candidate appears to be struggling, session stopped to avoid further stress"
        
        # Priority 2: Maximum questions reached
        if self.question_count >= self.max_questions:
            return True, f"Maximum question limit reached ({self.max_questions}) — session completed"
        
        return False, ""
    
    def _get_reason(self, score: float, adjustment: Adjustment) -> str:
        """
        Generate human-readable explanation for the decision.
        
        Explains:
        - Why difficulty changed (or stayed same)
        - Why session continues
        - Context based on score thresholds
        """
        if adjustment == Adjustment.INCREASE:
            return f"Strong answer (score {score:.2f} > {self.INCREASE_THRESHOLD}) — difficulty increased to challenge candidate"
        elif adjustment == Adjustment.DECREASE:
            return f"Weak answer (score {score:.2f} < {self.DECREASE_THRESHOLD}) — difficulty decreased to match candidate level"
        else:
            if score >= self.DECREASE_THRESHOLD and score <= self.INCREASE_THRESHOLD:
                return f"Adequate answer (score {score:.2f} within {self.DECREASE_THRESHOLD}-{self.INCREASE_THRESHOLD} range) — difficulty maintained"
            else:
                return f"Difficulty maintained at boundary — current level: {self.current_difficulty.value}"
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Return current session state for debugging/monitoring."""
        return {
            "session_id": self.session_id,
            "question_count": self.question_count,
            "current_difficulty": self.current_difficulty.value,
            "score_history": self.score_history,
            "low_score_streak": self.low_score_streak,
            "max_questions": self.max_questions
        }
