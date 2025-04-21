import pytest
from rubik.cube import RubiksCube
from rubik.utils.corner import CornerValidate

class TestCornerValidation:
    def setup_method(self):
        self.solved_orientation = {'URF': 0, 'UFL': 0, 'ULB': 0, 'UBR': 0, 'DFR': 0, 'DLF': 0, 'DBL': 0, 'DRB': 0}
        self.solved_permutation = {'URF': 'URF', 'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'UBR', 'DFR': 'DFR', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'}

    @pytest.fixture
    def validator(self):
        """Fixture that provides a CornerValidate instance"""
        return CornerValidate()
    
    @pytest.fixture
    def cube(self):
        """Fixture that provides a RubiksCube instance"""
        return RubiksCube()
    
    @pytest.fixture
    def invalid_twisted_corner_state(self, cube):
        """Fixture that provides a cube state with a manually twisted corner"""
        cube.reset()
        invalid_state = list(cube.get_state_string())
        
        # Twist a corner (swap URF stickers)
        urf_indices = [0, 0+9*4, 2+9*5]  # URF corner indices
        invalid_state[urf_indices[0]], invalid_state[urf_indices[1]], invalid_state[urf_indices[2]] = invalid_state[urf_indices[2]], invalid_state[urf_indices[0]], invalid_state[urf_indices[1]]
        return "".join(invalid_state)
    
    @pytest.fixture
    def invalid_swapped_stickers_state(self, cube):
        """Fixture that provides a cube state with swapped stickers"""
        cube.reset()
        invalid_state = list(cube.get_state_string())
        
        # Swap two stickers
        urf_indices = [1+9, 2+18]
        invalid_state[urf_indices[0]], invalid_state[urf_indices[1]] = invalid_state[urf_indices[1]], invalid_state[urf_indices[0]]
        return "".join(invalid_state)
    
    @pytest.fixture
    def t_perm_state(self, cube):
        """Fixture that provides a cube state after applying a T-perm"""
        cube.reset()
        cube.apply_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
        return cube.get_state_string()

    @pytest.mark.parametrize("case", [
        {
            "name": "Solved cube", 
            "moves": "", 
            "expected_parity": 0, 
            "expected_orientation_valid": True,
            "expected_permutation": {'URF': 'URF', 'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'UBR', 'DFR': 'DFR', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'},
            "expected_orientations": {'URF': 0, 'UFL': 0, 'ULB': 0, 'UBR': 0, 'DFR': 0, 'DLF': 0, 'DBL': 0, 'DRB': 0}
        },
        {
            "name": "Single move", 
            "moves": "R", 
            "expected_parity": 1, 
            "expected_orientation_valid": True,
            "expected_permutation": {'URF': 'DFR', 'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'URF', 'DFR': 'DRB', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'UBR'},
            "expected_orientations":{'URF': 2, 'UFL': 0, 'ULB': 0, 'UBR': 1, 'DFR': 1, 'DLF': 0, 'DBL': 0, 'DRB': 2}
        },
        {
            "name": "Single move with rotation", 
            "moves": "x y R", 
            "expected_parity": 1, 
            "expected_orientation_valid": True,
            "expected_permutation": {'URF': 'DFR', 'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'URF', 'DFR': 'DRB', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'UBR'},
            "expected_orientations":{'URF': 2, 'UFL': 0, 'ULB': 0, 'UBR': 1, 'DFR': 1, 'DLF': 0, 'DBL': 0, 'DRB': 2}
        },
        {
            "name": "Simple algorithm", 
            "moves": "R U R' U'", 
            "expected_parity": 0, 
            "expected_orientation_valid": True,
            "expected_permutation": {'URF': 'DFR', 'UFL': 'UFL', 'ULB': 'UBR', 'UBR': 'ULB', 'DFR': 'URF', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'}, 
            "expected_orientations": {'URF': 2, 'UFL': 0, 'ULB': 0, 'UBR': 2, 'DFR': 2, 'DLF': 0, 'DBL': 0, 'DRB': 0}  # Fill in with actual orientations from console
        },
        {
            "name": "Sune algorithm", 
            "moves": "R U R' U R U2 R'", 
            "expected_parity": 0, 
            "expected_orientation_valid": True,
            "expected_permutation": {'URF': 'ULB', 'UFL': 'UBR', 'ULB': 'URF', 'UBR': 'UFL', 'DFR': 'DFR', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'},  # Fill in with actual permutation from console
            "expected_orientations": {'URF': 1, 'UFL': 1, 'ULB': 1, 'UBR': 0, 'DFR': 0, 'DLF': 0, 'DBL': 0, 'DRB': 0}
        }
    ])
    def test_valid_cube_states(self, validator, cube, case):
        """Test corner validation with valid cube states"""
        # Setup cube state
        cube.reset()
        if case["moves"]:
            cube.apply_moves(case["moves"])
        
        state_string = cube.get_state_string()
        corners = validator.get(state_string)
        
        # Test permutation
        permutation = validator.permutation(corners, state_string)
        parity = validator.parity(permutation)
        
        # Test orientation
        orientations = validator.orientation(corners, state_string)
        total_orientation = validator.get_total_orientation(corners, state_string)
        
        # Assertions
        assert parity == case["expected_parity"], f"Expected parity {case['expected_parity']} for {case['name']}, got {parity}"
        assert (total_orientation == 0) == case["expected_orientation_valid"], \
            f"Expected orientation validity {case['expected_orientation_valid']} for {case['name']}"
        
        # Check permutation dictionary matches expected
        if "expected_permutation" in case and case["expected_permutation"]:
            assert permutation == case["expected_permutation"], \
                f"Expected permutation {case['expected_permutation']} for {case['name']}, got {permutation}"
            
        # Check orientations dictionary matches expected
        if "expected_orientations" in case and case["expected_orientations"]:
            assert orientations == case["expected_orientations"], \
                f"Expected orientations {case['expected_orientations']} for {case['name']}, got {orientations}"

    def test_invalid_twisted_corner(self, validator, invalid_twisted_corner_state):
        """Test corner validation with a manually twisted corner"""
        corners = validator.get(invalid_twisted_corner_state)
        
        # Check permutation
        permutation = validator.permutation(corners, invalid_twisted_corner_state)
        parity = validator.parity(permutation)
        
        # Check orientation
        orientations = validator.orientation(corners, invalid_twisted_corner_state)
        total_orientation = validator.get_total_orientation(corners, invalid_twisted_corner_state)
        
        # Expected values from console output
        expected_parity = 0  # Fill in
        expected_orientation_valid = False  # Fill in
        expected_orientations = {'URF': 0, 'UFL': 0, 'ULB': 1, 'UBR': 0, 'DFR': 0, 'DLF': 0, 'DBL': 0, 'DRB': 0}  # Fill in from console output
        expected_permutation = {'URF': 'URF', 'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'UBR', 'DFR': 'DFR', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'}  # Fill in from console output
        
        # Assertions
        assert parity == expected_parity, f"Expected parity {expected_parity}, got {parity}"
        assert (total_orientation == 0) == expected_orientation_valid, \
            f"Expected orientation validity {expected_orientation_valid}, got {total_orientation == 0}"
        assert permutation == expected_permutation, \
            f"Expected permutation {expected_permutation}, got {permutation}"
        assert orientations == expected_orientations, \
            f"Expected orientations {expected_orientations}, got {orientations}"

    def test_invalid_swapped_stickers(self, validator, invalid_swapped_stickers_state):
        """Test corner validation with swapped stickers"""
        corners = validator.get(invalid_swapped_stickers_state)
        
        # Check permutation
        permutation = validator.permutation(corners, invalid_swapped_stickers_state)
        parity = validator.parity(permutation)
        
        # Check orientation
        orientations = validator.orientation(corners, invalid_swapped_stickers_state)
        total_orientation = validator.get_total_orientation(corners, invalid_swapped_stickers_state)
        
        # Expected values from console output
        expected_parity = 0 
        expected_orientation_valid = True
        expected_orientations = {'URF': 0, 'UFL': 0, 'ULB': 0, 'UBR': 0, 'DFR': 0, 'DLF': 0, 'DBL': 0, 'DRB': 0}  # Fill in from console output
        expected_permutation = {'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'UBR', 'DFR': 'DFR', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'}  # Fill in from console output
        
        # Assertions
        assert parity == expected_parity, f"Expected parity {expected_parity}, got {parity}"
        assert (total_orientation == 0) == expected_orientation_valid, \
            f"Expected orientation validity {expected_orientation_valid}, got {total_orientation == 0}"
        assert permutation == expected_permutation, \
            f"Expected permutation {expected_permutation}, got {permutation}"
        assert orientations == expected_orientations, \
            f"Expected orientations {expected_orientations}, got {orientations}"

    def test_t_perm_parity(self, validator, t_perm_state):
        """Test corner parity for T-perm algorithm"""
        corners = validator.get(t_perm_state)
        permutation = validator.permutation(corners, t_perm_state)
        corner_parity = validator.parity(permutation)
        orientations = validator.orientation(corners, t_perm_state)
        
        # Expected values from console output
        expected_parity = 1
        expected_permutation = {'URF': 'UBR', 'UFL': 'UFL', 'ULB': 'ULB', 'UBR': 'URF', 'DFR': 'DFR', 'DLF': 'DLF', 'DBL': 'DBL', 'DRB': 'DRB'}
        expected_orientations = self.solved_orientation
        
        # Assertions
        assert corner_parity == expected_parity, f"Expected T-perm corner parity {expected_parity}, got {corner_parity}"
        assert permutation == expected_permutation, \
            f"Expected permutation {expected_permutation}, got {permutation}"
        assert orientations == expected_orientations, \
            f"Expected orientations {expected_orientations}, got {orientations}"