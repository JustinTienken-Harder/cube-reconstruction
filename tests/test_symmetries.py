import pytest
from src.rubiksymmetries import Symmetries  # Adjust the import path as needed


class TestSymmetries:
    def setup_method(self):
        """Set up a fresh cube instance for each test"""
        self.sym = Symmetries()


    
    
