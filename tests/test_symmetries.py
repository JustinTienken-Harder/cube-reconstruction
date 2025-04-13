import pytest
from src.validators.symmetries import Symmetries  # Adjust the import path as needed

class TestRubiksCubeState:
    def setup_method(self):
        """Set up a fresh cube instance for each test"""
        self.sym = Symmetries()


    
    
