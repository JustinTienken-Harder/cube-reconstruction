import pytest
import re
from src.rubik.string_tools import StringManipulate

class TestStringManipulate:
    @pytest.fixture
    def string_manipulator(self):
        """Fixture providing a StringManipulate instance"""
        return StringManipulate()
    
    @pytest.fixture
    def commutator_examples(self):
        """Fixture providing test cases for commutator parsing"""
        return {
            "simple_alg": {
                "input": "R U R' U'",
                "expected": "R U R' U'"
            },
            "nested_commutator": {
                "input": "[R U R': [R U R' U2, R2 U' R]]",
                "expected": "R U R' R U R' U2 R2 U' R U2 R U' R' R' U R2 R U' R'"
            },
            "basic_commutator": {
                "input": "[R, U]",
                "expected": "R U R' U'"
            },
            "conjugate": {
                "input": "[R: [U R', U]]",
                "expected": "R U R' U R U' U' R'"
            },
            "mixed_format": {
                "input": " F [R U: R' [x, y] F]",
                "expected": "F R U R' x y x' y' F U' R'"
            },
            "complex_nested": {
                "input": "[ F R: [M', U2]] [[r: U], D2]",
                "expected": "F R M' U2 M U2 R' F' r U r' D2 r U' r' D2"
            },
            "deeply_nested": {
                "input": "[ F R: [[M', U2]: [[r: U], D2]]]",
                "expected": "F R M' U2 M U2 r U r' D2 r U' r' D2 U2 M' U2 M R' F'"
            }
        }

    @pytest.fixture
    def move_splitting_examples(self):
        """Fixture providing test cases for move splitting"""
        return {
            "with_spaces": {
                "input": "R U R' U R U2 R' RwUr' U' r x y R' U2 \\ This is a comment\nR2 U2 R' U2 R rwU'r",
                "expected": ["R", "U", "R'", "U", "R", "U2", "R'", "Rw", "U", "r'", "U'", "r", "x", "y", "R'", "U2", "R2", "U2", "R'", "U2", "R", "rw", "U'", "r"]
            },
            "without_spaces": {
                "input": "RUR'URU2R'RwUr'U'rxyR'U2R2U2R'U2RrwU'r",
                "expected": ["R", "U", "R'", "U", "R", "U2", "R'", "Rw", "U", "r'", "U'", "r", "x", "y", "R'", "U2", "R2", "U2", "R'", "U2", "R", "rw", "U'", "r"]
            }
        }

    @pytest.fixture
    def inverse_examples(self):
        """Fixture providing test cases for move inversion"""
        return {
            "simple": {
                "input": "R U R'",
                "expected": "R U' R'"
            },
            "with_doubles": {
                "input": "R U2 R'",
                "expected": "R U2 R'"
            },
            "complex": {
                "input": "R U R' F' R U R' U' R' F R2 U' R'",
                "expected": "R U R2 F' R U R U' R' F R U' R'"
            },
            "with_wide_moves": {
                "input": "r U r'",
                "expected": "r U' r'"
            }
        }

    def test_parse_comm(self, string_manipulator, commutator_examples):
        """Test commutator parsing functionality"""
        for name, case in commutator_examples.items():
            result = StringManipulate.parse_comm(case["input"])
            result = re.sub(r'\s+', ' ', result).strip()  # Remove whitespace for comparison
            assert result == case["expected"], f"Failed on {name}: expected {case['expected']}, got {result}"

    def test_split_moves(self, string_manipulator, move_splitting_examples):
        """Test move splitting functionality"""
        for name, case in move_splitting_examples.items():
            result = StringManipulate.split_moves(case["input"])
            assert result == case["expected"], f"Failed on {name}: expected {case['expected']}, got {result}"

    def test_inverse(self, string_manipulator, inverse_examples):
        """Test sequence inversion functionality"""
        for name, case in inverse_examples.items():
            result = StringManipulate.inverse(case["input"])
            assert result == case["expected"], f"Failed on {name}: expected {case['expected']}, got {result}"

    def test_notation_synonyms(self, string_manipulator):
        """Test notation synonym replacement"""
        synonyms = string_manipulator.notation_synonyms()
        
        # Test basic equivalences
        assert synonyms["RW"] == "r"
        assert synonyms["Rw"] == "r"
        assert synonyms["rW"] == "r"
        assert synonyms["rw"] == "r"
        
        # Test with modifiers
        assert synonyms["R'"] == "R'"
        assert synonyms["Rw'"] == "r'"
        assert synonyms["RW'"] == "r'"
        
        # Test rotations
        assert synonyms["x"] == "x"
        assert synonyms["X"] == "x"
        assert synonyms["y'"] == "y'"
        assert synonyms["Y'"] == "y'"

    def test_call_method(self, string_manipulator):
        """Test the __call__ method which combines multiple functionalities"""
        # Test with simple alg
        assert string_manipulator("R U R' U'") == "R U R' U'"
        
        # Test with synonyms
        assert string_manipulator("Rw U R' U'") == "r U R' U'"
        
        # Test with commutator
        assert string_manipulator("[R, U]") == "R U R' U'"
        
        # Test with spaces and commutators
        assert string_manipulator("RW [r: U]") == "r r U r'"
        
        # Test with complex notation
        assert string_manipulator("[R: [U, R']]") == "R U R' U' R R'"

    def test_edge_cases(self, string_manipulator):
        """Test edge cases and potential error conditions"""
        # Empty string
        assert string_manipulator("") == ""
        
        # Only whitespace
        assert string_manipulator("  \t  \n  ") == ""
        
        # Unbalanced brackets
        # WE SHOULD NOT NEED THIS BUT ALAS
        assert StringManipulate.parse_comm("[R, U") == " R U R' U'"
        assert StringManipulate.parse_comm("R, U]") == "R U] R' U"
        
        # Comments
        assert StringManipulate.split_moves("R U // This is a comment") == ["R", "U"]

    def test_integration(self, string_manipulator):
        """Test the entire workflow with a complex example"""
        input_str = "[Rw: [U, R']] // This is a test"
        expected = "r U R' U' R r'"
        
        result = string_manipulator(input_str)
        assert result == expected, f"Expected {expected}, got {result}"