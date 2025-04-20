import torch 
from modeling.backbone import BackboneRegistry
from modeling.components import * 


def create_classifier(yaml_path, num_classes):
    backbone = BackboneRegistry.load_from_yaml(yaml_path)
    classifier = nn.Sequential(
        backbone,
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(backbone.out_channels, num_classes)
    )
    return classifier

def create_auxillary_classifier_cube(yaml_path):
    backbone = BackboneRegistry.load_from_yaml(yaml_path)
    classifier = nn.Sequential(
        backbone,
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(backbone.out_channels)
    )
    return classifier