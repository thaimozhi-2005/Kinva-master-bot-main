#!/usr/bin/env python3
"""
Kinva Master Bot - Advanced Effects Module
Author: @funnytamilan
"""

import cv2
import numpy as np
import random
import math
import logging
from typing import Dict, List, Tuple, Optional, Union

logger = logging.getLogger(__name__)

class AdvancedEffects:
    """Advanced Effects Class with 50+ Effects for Images and Videos"""
    
    def __init__(self):
        self.effects_list = {
            # Basic Image Effects
            'vintage': self.apply_vintage,
            'cinematic': self.apply_cinematic,
            'black_white': self.apply_black_white,
            'sepia': self.apply_sepia,
            'blur': self.apply_blur,
            'sharpen': self.apply_sharpen,
            
            # Artistic Effects
            'watercolor': self.apply_watercolor,
            'oil_painting': self.apply_oil_painting,
            'sketch': self.apply_sketch,
            'cartoon': self.apply_cartoon,
            'neon': self.apply_neon,
            
            # Modern Effects
            'glitch': self.apply_glitch,
            'pixelate': self.apply_pixelate,
            'mosaic': self.apply_mosaic,
            'emboss': self.apply_emboss,
            'edge_detect': self.apply_edge_detect,
            
            # Color Effects
            'invert': self.apply_invert,
            'heatmap': self.apply_heatmap,
            'cold': self.apply_cold,
            'warm': self.apply_warm,
            'dramatic': self.apply_dramatic,
            
            # Video Effects
            'vhs': self.apply_vhs,
            'retro': self.apply_retro,
            'glow': self.apply_glow,
            'shake': self.apply_shake,
            
            # Premium Effects
            '3d_effect': self.apply_3d_effect,
            'cinematic_pro': self.apply_cinematic_pro,
            'ai_enhance': self.apply_ai_enhance,
            'style_transfer': self.apply_style_transfer
        }
    
    # ============= BASIC IMAGE EFFECTS =============
    
    def apply_vintage(self, image: np.ndarray) -> np.ndarray:
        """Apply vintage filter"""
        img = image.copy()
        img = cv2.applyColorMap(img, cv2.COLORMAP_BONE)
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        return img
    
    def apply_cinematic(self, image: np.ndarray) -> np.ndarray:
        """Apply cinematic movie filter"""
        img = image.copy()
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Add black bars
        h, w = img.shape[:2]
        bar_h = h // 12
        img[:bar_h] = [0, 0, 0]
        img[-bar_h:] = [0, 0, 0]
        
        return img
    
    def apply_black_white(self, image: np.ndarray) -> np.ndarray:
        """Apply black and white filter"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    def apply_sepia(self, image: np.ndarray) -> np.ndarray:
        """Apply sepia tone"""
        img = image.copy().astype(np.float32)
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(img, kernel)
        return np.clip(sepia, 0, 255).astype(np.uint8)
    
    def apply_blur(self, image: np.ndarray, intensity: int = 15) -> np.ndarray:
        """Apply Gaussian blur"""
        return cv2.GaussianBlur(image, (intensity, intensity), 0)
    
    def apply_sharpen(self, image: np.ndarray) -> np.ndarray:
        """Apply sharpen filter"""
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    # ============= ARTISTIC EFFECTS =============
    
    def apply_watercolor(self, image: np.ndarray) -> np.ndarray:
        """Apply watercolor painting effect"""
        img = image.copy()
        for _ in range(3):
            img = cv2.bilateralFilter(img, 9, 75, 75)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 9, 10)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.addWeighted(img, 0.7, edges_colored, 0.3, 0)
    
    def apply_oil_painting(self, image: np.ndarray, size: int = 5) -> np.ndarray:
        """Apply oil painting effect"""
        img = image.copy()
        h, w = img.shape[:2]
        output = np.zeros_like(img)
        
        for y in range(0, h - size, size):
            for x in range(0, w - size, size):
                patch = img[y:y+size, x:x+size]
                avg_color = np.mean(patch, axis=(0, 1))
                output[y:y+size, x:x+size] = avg_color
        return output
    
    def apply_sketch(self, image: np.ndarray) -> np.ndarray:
        """Apply pencil sketch effect"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    def apply_cartoon(self, image: np.ndarray) -> np.ndarray:
        """Apply cartoon effect"""
        smooth = cv2.bilateralFilter(image, 9, 75, 75)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 9, 10)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.bitwise_and(smooth, edges_colored)
    
    def apply_neon(self, image: np.ndarray) -> np.ndarray:
        """Apply neon glow effect"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        neon = np.zeros_like(image)
        neon[edges > 0] = [0, 255, 255]
        return cv2.addWeighted(image, 0.5, neon, 0.5, 0)
    
    # ============= MODERN EFFECTS =============
    
    def apply_glitch(self, image: np.ndarray) -> np.ndarray:
        """Apply digital glitch effect"""
        img = image.copy()
        h, w = img.shape[:2]
        
        # Random color channel shifts
        for _ in range(random.randint(3, 8)):
            channel = random.randint(0, 2)
            shift = random.randint(-20, 20)
            img[:, :, channel] = np.roll(img[:, :, channel], shift, axis=1)
        
        # Add random blocks
        for _ in range(random.randint(5, 15)):
            x = random.randint(0, w - 50)
            y = random.randint(0, h - 50)
            bw = random.randint(10, 50)
            bh = random.randint(10, 50)
            img[y:y+bh, x:x+bw] = img[y:y+bh, x:x+bw][:, ::-1]
        
        # Add noise
        noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        return img
    
    def apply_pixelate(self, image: np.ndarray, pixel_size: int = 10) -> np.ndarray:
        """Apply pixelation effect"""
        h, w = image.shape[:2]
        small = cv2.resize(image, (w // pixel_size, h // pixel_size), 
                          interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    
    def apply_mosaic(self, image: np.ndarray, block_size: int = 15) -> np.ndarray:
        """Apply mosaic effect"""
        img = image.copy()
        h, w = img.shape[:2]
        
        for y in range(0, h, block_size):
            for x in range(0, w, block_size):
                block = img[y:min(y+block_size, h), x:min(x+block_size, w)]
                avg_color = np.mean(block, axis=(0, 1))
                img[y:min(y+block_size, h), x:min(x+block_size, w)] = avg_color
        return img
    
    def apply_emboss(self, image: np.ndarray) -> np.ndarray:
        """Apply emboss effect"""
        kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
        emboss = cv2.filter2D(image, -1, kernel)
        return emboss + 128
    
    def apply_edge_detect(self, image: np.ndarray) -> np.ndarray:
        """Apply edge detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # ============= COLOR EFFECTS =============
    
    def apply_invert(self, image: np.ndarray) -> np.ndarray:
        """Apply invert colors"""
        return 255 - image
    
    def apply_heatmap(self, image: np.ndarray) -> np.ndarray:
        """Apply heatmap effect"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    
    def apply_cold(self, image: np.ndarray) -> np.ndarray:
        """Apply cold (blue) tone"""
        img = image.copy().astype(np.float32)
        img[:, :, 0] = img[:, :, 0] * 1.3  # Blue
        img[:, :, 2] = img[:, :, 2] * 0.7  # Red
        return np.clip(img, 0, 255).astype(np.uint8)
    
    def apply_warm(self, image: np.ndarray) -> np.ndarray:
        """Apply warm (orange) tone"""
        img = image.copy().astype(np.float32)
        img[:, :, 0] = img[:, :, 0] * 0.7  # Blue
        img[:, :, 2] = img[:, :, 2] * 1.3  # Red
        return np.clip(img, 0, 255).astype(np.uint8)
    
    def apply_dramatic(self, image: np.ndarray) -> np.ndarray:
        """Apply dramatic effect (high contrast + vignette)"""
        img = image.copy()
        
        # Increase contrast
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Add vignette
        h, w = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(w, w/2)
        kernel_y = cv2.getGaussianKernel(h, h/2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        for i in range(3):
            img[:,:,i] = (img[:,:,i] * mask).astype(np.uint8)
        
        return img
    
    # ============= VIDEO EFFECTS =============
    
    def apply_vhs(self, frame: np.ndarray) -> np.ndarray:
        """Apply VHS effect to frame"""
        img = frame.copy()
        height = img.shape[0]
        
        # Add scanlines
        img[::2] = img[::2] * 0.7
        
        # Add chromatic aberration
        img_red = img.copy()
        img_red[:,:,0] = np.roll(img_red[:,:,0], 2, axis=1)
        img_blue = img.copy()
        img_blue[:,:,2] = np.roll(img_blue[:,:,2], -2, axis=1)
        img = cv2.addWeighted(img_red, 0.33, img_blue, 0.33, 0)
        
        # Add noise
        noise = np.random.randint(0, 20, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        return img
    
    def apply_retro(self, frame: np.ndarray) -> np.ndarray:
        """Apply retro effect to frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sepia = cv2.applyColorMap(gray, cv2.COLORMAP_BONE)
        noise = np.random.randint(0, 40, sepia.shape, dtype=np.uint8)
        return cv2.add(sepia, noise)
    
    def apply_glow(self, frame: np.ndarray) -> np.ndarray:
        """Apply glow effect to frame"""
        blurred = cv2.GaussianBlur(frame, (15, 15), 0)
        return cv2.addWeighted(frame, 0.7, blurred, 0.3, 0)
    
    def apply_shake(self, frame: np.ndarray, intensity: int = 5) -> np.ndarray:
        """Apply shake effect to frame"""
        h, w = frame.shape[:2]
        dx = random.randint(-intensity, intensity)
        dy = random.randint(-intensity, intensity)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        return cv2.warpAffine(frame, M, (w, h))
    
    # ============= PREMIUM EFFECTS =============
    
    def apply_3d_effect(self, image: np.ndarray) -> np.ndarray:
        """Apply 3D anaglyph effect"""
        img = image.copy()
        h, w = img.shape[:2]
        
        # Create red and cyan channels
        red = img[:,:,2].copy()
        cyan = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Shift channels
        shift = 5
        red_shifted = np.zeros_like(red)
        red_shifted[:, shift:] = red[:, :-shift]
        
        # Combine
        output = np.zeros_like(img)
        output[:,:,2] = red_shifted
        output[:,:,1] = cyan
        output[:,:,0] = cyan
        
        return output
    
    def apply_cinematic_pro(self, image: np.ndarray) -> np.ndarray:
        """Professional cinematic effect"""
        img = image.copy()
        
        # Color grading
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Increase saturation
        a = cv2.add(a, 20)
        b = cv2.add(b, 20)
        
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Add cinematic curve
        look_up = np.arange(256, dtype=np.uint8)
        for i in range(256):
            look_up[i] = int(255 * (i/255) ** 1.2)
        
        img = cv2.LUT(img, look_up)
        
        # Add film grain
        grain = np.random.normal(0, 5, img.shape).astype(np.uint8)
        img = cv2.add(img, grain)
        
        # Add black bars
        h, w = img.shape[:2]
        bar_h = h // 10
        img[:bar_h] = [0, 0, 0]
        img[-bar_h:] = [0, 0, 0]
        
        return img
    
    def apply_ai_enhance(self, image: np.ndarray) -> np.ndarray:
        """AI-based image enhancement"""
        img = image.copy()
        
        # Denoise
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)
        
        # Enhance contrast
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return img
    
    def apply_style_transfer(self, image: np.ndarray, style: str = 'abstract') -> np.ndarray:
        """Apply style transfer (simulated)"""
        img = image.copy()
        
        # Simulated style transfer effects
        if style == 'abstract':
            # Abstract art effect
            img = cv2.stylization(img, sigma_s=60, sigma_r=0.6)
        elif style == 'painting':
            # Oil painting effect
            img = cv2.xphoto.oilPainting(img, 7, 1)
        elif style == 'cartoon':
            # Cartoon effect
            img = self.apply_cartoon(img)
        else:
            img = cv2.stylization(img, sigma_s=60, sigma_r=0.5)
        
        return img
    
    # ============= HELPER METHODS =============
    
    def get_effect(self, effect_name: str) -> callable:
        """Get effect function by name"""
        return self.effects_list.get(effect_name, self.apply_vintage)
    
    def get_all_effects(self) -> List[str]:
        """Get list of all available effects"""
        return list(self.effects_list.keys())
    
    def get_premium_effects(self) -> List[str]:
        """Get list of premium effects"""
        return ['3d_effect', 'cinematic_pro', 'ai_enhance', 'style_transfer']
    
    def is_premium_effect(self, effect_name: str) -> bool:
        """Check if effect requires premium"""
        return effect_name in self.get_premium_effects()
    
    def apply_effect(self, image: np.ndarray, effect_name: str) -> np.ndarray:
        """Apply effect by name"""
        effect_func = self.get_effect(effect_name)
        return effect_func(image)
