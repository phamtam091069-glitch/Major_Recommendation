"""
Response Validator Module
Validates chatbot responses using fallback API before returning to user
Ensures accuracy, relevance, and quality of responses
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validates chatbot responses before returning them
    Uses fallback API to check accuracy, relevance, and appropriateness
    """

    def __init__(self):
        self.high_confidence_sources = ["explicit_major", "pattern", "greeting"]
        self.low_confidence_threshold = 0.7

    def should_validate(self, response: Dict[str, Any]) -> bool:
        """
        Determine if response should be validated
        Skip validation for high-confidence responses
        Always validate fallback responses
        
        Args:
            response: Response dict from chatbot
            
        Returns:
            True if validation is needed, False otherwise
        """
        source = response.get("source", "")
        confidence = float(response.get("confidence", 0.0))

        # Never validate high-confidence sources
        if source in self.high_confidence_sources:
            logger.debug(f"✅ Skipping validation: {source} (high confidence)")
            return False

        # Always validate fallback API responses
        if source == "fallback":
            logger.debug(f"⚠️ Validating fallback response (source verification)")
            return True

        # Validate low-confidence responses
        if confidence < self.low_confidence_threshold:
            logger.debug(
                f"⚠️ Validating {source} response (low confidence: {confidence})"
            )
            return True

        return False

    def validate_response(
        self,
        user_message: str,
        response: Dict[str, Any],
        fallback_api=None,
        major_list=None,
    ) -> Dict[str, Any]:
        """
        Validate response using fallback API
        
        Args:
            user_message: Original user message
            response: Response dict from chatbot
            fallback_api: Fallback API instance for validation
            major_list: List of valid majors for constraint
            
        Returns:
            Modified response with validation results
        """
        # Check if validation is needed
        if not self.should_validate(response):
            return response

        # Validate response content
        validation_result = self._perform_validation(
            user_message=user_message,
            response=response,
            fallback_api=fallback_api,
            major_list=major_list,
        )

        # Apply validation results
        if validation_result.get("valid"):
            logger.info("✅ Response passed validation")
            return response
        else:
            logger.warning(f"❌ Response failed validation: {validation_result.get('issues')}")
            # Adjust confidence if issues found
            if validation_result.get("confidence_adjustment"):
                response["confidence"] = max(
                    0.0,
                    response.get("confidence", 0.0)
                    + validation_result.get("confidence_adjustment", 0),
                )
            # Add validation metadata
            response["validation_issues"] = validation_result.get("issues", [])
            response["validation_passed"] = False
            return response

    def _perform_validation(
        self,
        user_message: str,
        response: Dict[str, Any],
        fallback_api=None,
        major_list=None,
    ) -> Dict[str, Any]:
        """
        Perform actual validation using fallback API
        
        Args:
            user_message: Original user message
            response: Response from chatbot
            fallback_api: API for validation
            major_list: List of valid majors for constraint
            
        Returns:
            Validation result dict with valid/issues/adjustments
        """
        try:
            # Extract response components
            reply = response.get("reply", "")
            resolved_major = response.get("resolved_major", "")
            confidence = response.get("confidence", 0.0)

            # Build validation prompt
            validation_prompt = self._build_validation_prompt(
                user_message=user_message,
                response_text=reply,
                resolved_major=resolved_major,
                confidence=confidence,
            )

            # Call fallback API for validation
            if not fallback_api:
                logger.warning("No fallback API available for validation")
                return {
                    "valid": True,
                    "issues": [],
                    "confidence_adjustment": 0,
                }

            validation_response = fallback_api.analyze_free_text(
                validation_prompt,
                context="response_validation",
                major_list=major_list,
            )

            # Parse validation response
            if isinstance(validation_response, dict):
                success = validation_response.get("success", False)
                validation_text = str(
                    validation_response.get("response", "")
                ).lower()

                is_valid = success and ("valid" in validation_text or "appropriate" in validation_text)

                issues = self._extract_issues(validation_text)

                return {
                    "valid": is_valid,
                    "issues": issues,
                    "confidence_adjustment": -0.1 if not is_valid else 0,
                }

            return {"valid": True, "issues": [], "confidence_adjustment": 0}

        except Exception as exc:
            logger.exception(f"Error during response validation: {exc}")
            # On error, assume valid to avoid breaking chat flow
            return {"valid": True, "issues": [], "confidence_adjustment": 0}

    def _build_validation_prompt(
        self,
        user_message: str,
        response_text: str,
        resolved_major: str,
        confidence: float,
    ) -> str:
        """
        Build prompt for fallback API validation
        
        Args:
            user_message: Original user query
            response_text: Chatbot response text
            resolved_major: Recommended major
            confidence: Confidence score
            
        Returns:
            Validation prompt string
        """
        prompt = f"""Hãy kiểm tra xem câu trả lời của chatbot có phù hợp không.

Câu hỏi của user: "{user_message}"

Câu trả lời của chatbot: "{response_text}"

Ngành được gợi ý: {resolved_major if resolved_major else "Không có"}
Độ tin cậy: {confidence:.2f}

Vui lòng kiểm tra:
1. Câu trả lời có phù hợp với câu hỏi không?
2. Ngành được gợi ý có thích hợp không?
3. Có bất kỳ thông tin sai lệch không?
4. Câu trả lời có rõ ràng và chuyên nghiệp không?

Trả lời: VALID (hợp lệ) hoặc INVALID (không hợp lệ) + lý do nếu không hợp lệ"""

        return prompt

    def _extract_issues(self, validation_text: str) -> List[str]:
        """
        Extract issues from validation response
        
        Args:
            validation_text: Validation response text
            
        Returns:
            List of identified issues
        """
        issues = []

        # Check for common issues
        issue_keywords = {
            "sai lệch": "Thông tin sai lệch",
            "không phù hợp": "Không phù hợp với câu hỏi",
            "không rõ": "Không rõ ràng",
            "không chuyên nghiệp": "Không chuyên nghiệp",
            "sai": "Sai lệch",
            "lỗi": "Có lỗi",
            "vấn đề": "Có vấn đề",
        }

        for keyword, issue_text in issue_keywords.items():
            if keyword in validation_text:
                issues.append(issue_text)

        # If no specific issues found but marked invalid
        if not issues and "invalid" in validation_text:
            issues.append("Không thỏa mãn yêu cầu kiểm tra")

        return issues

    def validate_multiple_responses(
        self,
        user_message: str,
        responses: List[Dict[str, Any]],
        fallback_api=None,
        major_list=None,
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple alternative responses
        Useful for selecting best response from candidates
        
        Args:
            user_message: Original user message
            responses: List of response candidates
            fallback_api: API for validation
            major_list: List of valid majors for constraint
            
        Returns:
            Validated responses with scores
        """
        validated = []

        for response in responses:
            validated_response = self.validate_response(
                user_message=user_message,
                response=response,
                fallback_api=fallback_api,
                major_list=major_list,
            )
            validated.append(validated_response)

        # Sort by confidence
        validated.sort(key=lambda r: r.get("confidence", 0.0), reverse=True)

        return validated


def get_response_validator() -> ResponseValidator:
    """Factory function to get validator instance"""
    return ResponseValidator()
