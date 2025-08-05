"""
Rubric-based scoring system for content evaluation.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx is not installed. Please install it with: pip install httpx")
    exit(1)


class RubricScorer:
    """
    Rubric-based scoring system that evaluates content against predefined rubric.
    """
    
    def __init__(self, model_name: str = "jiutian-lan", api_key: str = "", timeout: float = 30.0):
        self.model_name = model_name
        self.api_key = api_key
        self.timeout = timeout
        self.api_url = "https://ncoa-uat.cmitry.com/gateway/llm-subscribe/v1/chat/completions"
        self.rubric = self._generate_default_rubric()
    
    def _generate_default_rubric(self) -> Dict[str, Any]:
        """
        Generate a default rubric for general content evaluation.
        """
        return {
            "criteria": {
                "relevance_alignment": {
                    "weight": 0.3,
                    "description": "How well the content aligns with the specified requirements",
                    "scoring": {
                        "excellent": {"score": 90, "description": "Perfect alignment with all requirements"},
                        "good": {"score": 75, "description": "Strong alignment with most requirements"},
                        "fair": {"score": 60, "description": "Moderate alignment with some requirements"},
                        "poor": {"score": 40, "description": "Limited alignment with few requirements"},
                        "none": {"score": 20, "description": "No alignment with requirements"}
                    }
                },
                "quality_completeness": {
                    "weight": 0.25,
                    "description": "Overall quality and completeness of the content",
                    "scoring": {
                        "excellent": {"score": 90, "description": "Exceptional quality, comprehensive and complete"},
                        "good": {"score": 75, "description": "High quality, mostly complete"},
                        "fair": {"score": 60, "description": "Adequate quality, some gaps"},
                        "poor": {"score": 40, "description": "Poor quality, significant gaps"},
                        "none": {"score": 20, "description": "Very poor quality, incomplete"}
                    }
                },
                "technical_competency": {
                    "weight": 0.2,
                    "description": "Technical skills, knowledge, or specifications demonstrated",
                    "scoring": {
                        "excellent": {"score": 90, "description": "Expert level technical competency"},
                        "good": {"score": 75, "description": "Proficient technical competency"},
                        "fair": {"score": 60, "description": "Basic technical competency"},
                        "poor": {"score": 40, "description": "Limited technical competency"},
                        "none": {"score": 20, "description": "No relevant technical competency"}
                    }
                },
                "presentation_clarity": {
                    "weight": 0.15,
                    "description": "Clarity, organization, and professional presentation",
                    "scoring": {
                        "excellent": {"score": 90, "description": "Exceptional presentation, clear and professional"},
                        "good": {"score": 75, "description": "Well-organized, professional format"},
                        "fair": {"score": 60, "description": "Adequate presentation, some clarity issues"},
                        "poor": {"score": 40, "description": "Poor organization, unclear presentation"},
                        "none": {"score": 20, "description": "Very poor presentation quality"}
                    }
                },
                "innovation_uniqueness": {
                    "weight": 0.1,
                    "description": "Innovation, uniqueness, or added value beyond basic requirements",
                    "scoring": {
                        "excellent": {"score": 90, "description": "Highly innovative, unique value proposition"},
                        "good": {"score": 75, "description": "Some innovation, good added value"},
                        "fair": {"score": 60, "description": "Moderate innovation, some added value"},
                        "poor": {"score": 40, "description": "Limited innovation, minimal added value"},
                        "none": {"score": 20, "description": "No innovation or added value"}
                    }
                }
            },
            "total_score_ranges": {
                "excellent": {"min": 85, "max": 100, "description": "Outstanding content, highly recommended"},
                "good": {"min": 70, "max": 84, "description": "Strong content, recommended"},
                "fair": {"min": 55, "max": 69, "description": "Adequate content, consider with reservations"},
                "poor": {"min": 40, "max": 54, "description": "Weak content, not recommended"},
                "reject": {"min": 0, "max": 39, "description": "Unsuitable content, reject"}
            }
        }
    
    def generate_custom_rubric(self, requirements: str, score_range: tuple = (0, 100)) -> Dict[str, Any]:
        """
        Generate a custom rubric based on the requirements using AI.
        
        Args:
            requirements: The requirements text to base the rubric on
            score_range: Tuple of (min_score, max_score) for the scoring range (default: (0, 100))
        """
        min_score, max_score = score_range
        
        # Calculate score levels based on the range
        score_span = max_score - min_score
        excellent_score = min_score + int(score_span * 0.9)  # 90% of range
        good_score = min_score + int(score_span * 0.75)     # 75% of range
        fair_score = min_score + int(score_span * 0.6)      # 60% of range
        poor_score = min_score + int(score_span * 0.4)      # 40% of range
        none_score = min_score + int(score_span * 0.2)      # 20% of range
        
        prompt = f"""
Based on the following requirements, create a detailed scoring rubric for evaluating content. 
The rubric should include 5-7 criteria with weights that sum to 1.0, and each criterion should have 5 scoring levels (excellent, good, fair, poor, none) with specific score ranges and descriptions.

Score Range: {min_score} to {max_score}
Use these approximate score levels:
- Excellent: {excellent_score}
- Good: {good_score}
- Fair: {fair_score}
- Poor: {poor_score}
- None: {none_score}

Requirements:
{requirements}

Please return the rubric in JSON format with the following structure:
{{
    "criteria": {{
        "criterion_name": {{
            "weight": 0.x,
            "description": "description",
            "scoring": {{
                "excellent": {{"score": {excellent_score}, "description": "..."}},
                "good": {{"score": {good_score}, "description": "..."}},
                "fair": {{"score": {fair_score}, "description": "..."}},
                "poor": {{"score": {poor_score}, "description": "..."}},
                "none": {{"score": {none_score}, "description": "..."}}
            }}
        }}
    }}
}}
"""
        
        try:
            response = self._call_api(prompt)
            if response and 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    rubric_data = json.loads(json_match.group())
                    self.rubric = rubric_data
                    return rubric_data
        except Exception as e:
            print(f"Error generating custom rubric: {e}")
        
        # Fallback to default rubric
        return self.rubric
    
    def _call_api(self, prompt: str, system_message: str = "You are a professional content evaluator and scoring expert.") -> Optional[Dict[str, Any]]:
        """
        Call the API to get AI response.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "stream": False,
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"API call error: {e}")
            return None
    
    def score_content(self, content: str, requirements: str = "") -> Dict[str, Any]:
        """
        Score content against the rubric.
        """
        # Create evaluation prompt
        rubric_text = self._format_rubric_for_prompt()
        
        requirements_section = f"Requirements: {requirements}\n" if requirements else ""
        
        prompt = f"""
Evaluate the following content against the provided rubric. For each criterion, determine which scoring level (excellent, good, fair, poor, none) best fits the content and provide a brief justification.

Rubric:
{rubric_text}

{requirements_section}Content to Evaluate:
{content}

Please provide your evaluation in the following JSON format:
{{
    "scores": {{
        "criterion_name": {{
            "level": "excellent/good/fair/poor/none",
            "score": numeric_score,
            "justification": "brief explanation"
        }}
    }},
    "total_score": calculated_weighted_total,
    "overall_assessment": "brief overall evaluation",
    "recommendation": "accept/consider/reject"
}}
"""
        
        try:
            response = self._call_api(prompt)
            if response and 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            print(f"Error scoring content: {e}")
        
        # Fallback scoring
        return {
            "scores": {},
            "total_score": 0,
            "overall_assessment": "Error in evaluation",
            "recommendation": "manual_review"
        }
    
    def _format_rubric_for_prompt(self) -> str:
        """
        Format the rubric for use in AI prompts.
        """
        rubric_text = "Scoring Rubric:\n"
        for criterion, details in self.rubric.get('criteria', {}).items():
            rubric_text += f"\n{criterion.replace('_', ' ').title()} (Weight: {details['weight']}): \n"
            rubric_text += f"  Description: {details['description']}\n"
            for level, score_info in details['scoring'].items():
                rubric_text += f"  - {level.title()}: {score_info['score']} points - {score_info['description']}\n"
        return rubric_text
    
    def save_rubric(self, filepath: str) -> None:
        """
        Save the current rubric to a file.
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.rubric, f, indent=2, ensure_ascii=False)
    
    def load_rubric(self, filepath: str) -> None:
        """
        Load a rubric from a file.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.rubric = json.load(f)