import unittest
from src.evaluator_agents import EvaluatorAgent

class TestEvaluatorAgent(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.evaluator = EvaluatorAgent()
        
    def test_evaluator_initialization(self):
        """Test that the evaluator is properly initialized with all categories"""
        expected_categories = [
            "protocol_parameters",
            "treasury_management",
            "tokenomics",
            "protocol_upgrades",
            "governance_process",
            "partnerships_integrations",
            "risk_management",
            "community_initiatives"
        ]
        
        for category in expected_categories:
            self.assertIn(category, self.evaluator.prompts)
            self.assertIn("system", self.evaluator.prompts[category])
            self.assertIn("key_points", self.evaluator.prompts[category])
            self.assertIn("output_instructions", self.evaluator.prompts[category])
            
    def test_evaluate_proposal(self):
        """Test proposal evaluation with a sample proposal"""
        # Sample proposal data
        proposal_details = {
            "title": "Test Proposal",
            "created_at": "2024-03-20",
            "content": "This is a test proposal for protocol parameter changes.",
            "comments": [
                {"content": "This looks good for parameter optimization."},
                {"content": "We should consider the impact on other parameters."}
            ]
        }
        
        # Test evaluation
        result = self.evaluator.evaluate_proposal("protocol_parameters", proposal_details)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("score", result)
        self.assertIn("analysis", result)
        self.assertIn("category", result)
        self.assertEqual(result["category"], "protocol_parameters")
        
    def test_invalid_category(self):
        """Test that invalid categories raise appropriate errors"""
        proposal_details = {
            "title": "Test Proposal",
            "content": "Test content"
        }
        
        with self.assertRaises(ValueError):
            self.evaluator.evaluate_proposal("invalid_category", proposal_details)
            
    def test_error_handling(self):
        """Test that the evaluator handles API errors gracefully"""
        # Create a proposal that would cause an error (empty content)
        proposal_details = {
            "title": "",
            "content": "",
            "created_at": ""
        }
        
        result = self.evaluator.evaluate_proposal("protocol_parameters", proposal_details)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["score"], 0.0)
        self.assertIn("Error", result["analysis"])

if __name__ == '__main__':
    unittest.main() 