"""AI service for question generation and answer evaluation."""
from openai import OpenAI
from config import settings
from models.session import Evaluation, Role
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)


class AIService:
    """Handle AI operations using OpenAI."""
    
    @staticmethod
    def _get_role_prompt(role: str) -> str:
        """Get system prompt for specific role."""
        prompts = {
            Role.FRONTEND: "You are an expert technical interviewer for Frontend Developer positions. Ask questions about React, JavaScript, CSS, HTML, web performance, and frontend architecture.",
            Role.BACKEND: "You are an expert technical interviewer for Backend Developer positions. Ask questions about APIs, databases, server architecture, security, and backend frameworks.",
            Role.FULLSTACK: "You are an expert technical interviewer for Full Stack Developer positions. Ask questions covering both frontend and backend technologies, system design, and full application architecture.",
            Role.AI_ML: "You are an expert technical interviewer for AI/ML Engineer positions. Ask questions about machine learning algorithms, neural networks, data processing, model deployment, and AI frameworks.",
            Role.DATA_ANALYST: "You are an expert technical interviewer for Data Analyst positions. Ask questions about SQL, data visualization, statistical analysis, business intelligence, and data interpretation."
        }
        return prompts.get(role, prompts[Role.FULLSTACK])
    
    @staticmethod
    async def generate_question(role: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Generate an interview question based on role and conversation history.
        
        Args:
            role: The interview role
            conversation_history: Previous Q&A pairs for context
            
        Returns:
            Generated question string
        """
        try:
            messages = [
                {"role": "system", "content": AIService._get_role_prompt(role)},
                {"role": "system", "content": "Ask one clear, specific technical interview question. Keep it concise and focused on practical knowledge."}
            ]
            
            # Add conversation history if available
            if conversation_history:
                for entry in conversation_history[-3:]:  # Last 3 Q&A pairs for context
                    messages.append({"role": "assistant", "content": entry.get("question", "")})
                    messages.append({"role": "user", "content": entry.get("answer", "")})
            
            messages.append({"role": "user", "content": "Ask me the next interview question."})
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.8,
                timeout=30
            )
            
            question = response.choices[0].message.content.strip()
            logger.info(f"Generated question for {role}")
            return question
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            # Fallback question
            return "Can you describe your experience with the technologies relevant to this role?"
    
    @staticmethod
    async def evaluate_answer(question: str, answer: str, role: str) -> Evaluation:
        """
        Evaluate a candidate's answer.
        
        Args:
            question: The interview question
            answer: The candidate's answer
            role: The interview role
            
        Returns:
            Evaluation object with score, strengths, improvements, and suggestion
        """
        try:
            system_prompt = f"""You are an expert technical interviewer evaluating answers for a {role} position.

Evaluate the candidate's answer and provide:
1. A score from 0-10 (0=completely wrong, 10=perfect answer)
2. 2-3 specific strengths in their answer
3. 2-3 specific areas for improvement
4. A suggested better answer

Return your evaluation in this exact JSON format:
{{
    "score": <number between 0-10>,
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "improvements": ["improvement 1", "improvement 2", "improvement 3"],
    "suggestion": "A concise suggested answer that demonstrates best practices"
}}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\n\nCandidate's Answer: {answer}\n\nProvide your evaluation in JSON format."}
            ]
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            eval_data = json.loads(content)
            
            # Validate and create Evaluation object
            evaluation = Evaluation(
                score=float(eval_data["score"]),
                strengths=eval_data["strengths"][:3],  # Max 3
                improvements=eval_data["improvements"][:3],  # Max 3
                suggestion=eval_data["suggestion"]
            )
            
            logger.info(f"Evaluated answer with score: {evaluation.score}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            # Fallback evaluation
            return Evaluation(
                score=5.0,
                strengths=["You provided a response", "You attempted to answer the question"],
                improvements=["Provide more specific details", "Include concrete examples", "Demonstrate deeper technical knowledge"],
                suggestion="A strong answer would include specific examples, demonstrate understanding of core concepts, and show practical experience with the technology."
            )


ai_service = AIService()
