# backbone_components.py
from typing import Dict, Any, List
import torch
import torch.nn as nn
from modeling.backbone import BackboneRegistry

class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, 
                 padding=1, batch_norm=True, activation="relu"):
        super().__init__()
        
        layers = []
        layers.append(nn.Conv2d(in_channels, out_channels, 
                               kernel_size, stride, padding))
        
        if batch_norm:
            layers.append(nn.BatchNorm2d(out_channels))
            
        if activation == "relu":
            layers.append(nn.ReLU(inplace=True))
        elif activation == "leaky_relu":
            layers.append(nn.LeakyReLU(0.2, inplace=True))
        
        self.block = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.block(x)

class ResidualBlock(nn.Module):
    def __init__(self, channels, bottleneck=False):
        super().__init__()
        self.channels = channels
        
        if bottleneck:
            self.residual = nn.Sequential(
                nn.Conv2d(channels, channels//4, 1, 1, 0),
                nn.BatchNorm2d(channels//4),
                nn.ReLU(inplace=True),
                nn.Conv2d(channels//4, channels//4, 3, 1, 1),
                nn.BatchNorm2d(channels//4),
                nn.ReLU(inplace=True),
                nn.Conv2d(channels//4, channels, 1, 1, 0),
                nn.BatchNorm2d(channels)
            )
        else:
            self.residual = nn.Sequential(
                nn.Conv2d(channels, channels, 3, 1, 1),
                nn.BatchNorm2d(channels),
                nn.ReLU(inplace=True),
                nn.Conv2d(channels, channels, 3, 1, 1),
                nn.BatchNorm2d(channels)
            )
        
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        identity = x
        out = self.residual(x)
        out += identity  # The crucial residual connection!
        out = self.relu(out)
        return out

class SequentialBackbone(nn.Module):
    def __init__(self, layers: List[Dict[str, Any]]):
        super().__init__()
        self.layers = nn.ModuleList()
        
        for layer_config in layers:
            module = BackboneRegistry.create_from_config(layer_config)
            self.layers.append(module)
    
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
    
class UNetBackbone(nn.Module):
    def __init__(self, encoder_config, decoder_config, skip_connections=True):
        super().__init__()
        self.encoder = BackboneRegistry.create_from_config(encoder_config)
        self.decoder = BackboneRegistry.create_from_config(decoder_config)
        self.skip_connections = skip_connections
        
        # Store intermediate activations for skip connections
        self.encoder_features = []
    
    def forward(self, x):
        # Clear stored features
        self.encoder_features = []
        
        # For UNet, we need to track intermediate outputs
        if isinstance(self.encoder, SequentialBackbone):
            # Pass through encoder layers, storing outputs
            for layer in self.encoder.layers:
                x = layer(x)
                self.encoder_features.append(x)
        else:
            # Handle single module encoder
            x = self.encoder(x)
            self.encoder_features.append(x)
        
        # For decoder with skip connections
        if self.skip_connections and isinstance(self.decoder, SequentialBackbone):
            # Start with encoder output
            x_dec = x
            
            # For each decoder layer (except the last one)
            for i, layer in enumerate(self.decoder.layers[:-1]):
                x_dec = layer(x_dec)
                
                # Add skip connection if appropriate
                if i < len(self.encoder_features):
                    skip_feature = self.encoder_features[-(i+2)]  # Matching encoder feature
                    if x_dec.shape[2:] != skip_feature.shape[2:]:
                        # Resize if shapes don't match
                        x_dec = nn.functional.interpolate(
                            x_dec, size=skip_feature.shape[2:], mode='bilinear', align_corners=False)
                    
                    # Concatenate or add features
                    x_dec = torch.cat([x_dec, skip_feature], dim=1)
            
            # Final decoder layer
            if self.decoder.layers:
                x_dec = self.decoder.layers[-1](x_dec)
            
            return x_dec
        else:
            # Simple sequential decoding without skip connections
            return self.decoder(x)

class FPNBackbone(nn.Module):
    def __init__(self, backbone_config, fpn_channels=256):
        super().__init__()
        self.backbone = BackboneRegistry.create_from_config(backbone_config)
        self.fpn_channels = fpn_channels
        self.lateral_convs = nn.ModuleDict()
        self.output_convs = nn.ModuleDict()
        
        # Add lateral and output convs dynamically based on backbone
        # (Would be configured via YAML in practice)
    
    def forward(self, x):
        # Extract features from backbone
        features = {}
        
        if isinstance(self.backbone, SequentialBackbone):
            # Track output at different stages
            current = x
            for i, layer in enumerate(self.backbone.layers):
                current = layer(current)
                features[f"p{i+1}"] = current
        else:
            # Single backbone output
            features["p1"] = self.backbone(x)
        
        # FPN processing
        # (Implementation would use lateral connections and top-down pathway)
        
        return features

class ValidationClassifier(nn.Module):
    def __init__(self, backbone):
        super().__init__()
        self.backbone = BackboneRegistry.create_from_config(backbone)
        self.classifier = nn.Linear(self.backbone.out_channels, )
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.classifier(x)
        return x

# Register more complex components
BackboneRegistry.register("unet", UNetBackbone)
BackboneRegistry.register("fpn", FPNBackbone)
# Register components with proper forward passes
BackboneRegistry.register("conv_block", ConvBlock)
BackboneRegistry.register("residual_block", ResidualBlock) 
BackboneRegistry.register("sequential", SequentialBackbone)