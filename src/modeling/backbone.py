# backbone_factory.py
from typing import Dict, Any, List, Type
import yaml
import torch.nn as nn

class BackboneRegistry:
    """Registry for backbone components"""
    _registry = {}
    
    @classmethod
    def register(cls, name: str, component_class: Type[nn.Module]):
        """Register a nn.Module class with a name"""
        cls._registry[name] = component_class
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> nn.Module:
        """Create a backbone component from a configuration dictionary"""
        config = config.copy()  # Avoid modifying the input
        component_type = config.pop("type")
        
        if component_type not in cls._registry:
            raise ValueError(f"Unknown component type: {component_type}")
            
        component_class = cls._registry[component_type]
        return component_class(**config)
    
    @classmethod
    def load_from_yaml(cls, yaml_path: str) -> nn.Module:
        """Load and create a backbone from a YAML file"""
        with open(yaml_path, 'r') as file:
            config = yaml.safe_load(file)
        return cls.create_from_config(config)