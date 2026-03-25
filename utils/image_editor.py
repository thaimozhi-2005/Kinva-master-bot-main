#!/usr/bin/env python3
"""
Kinva Master Bot - Advanced Image Editor
Author: @funnytamilan
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import logging
import os
import random
from typing import Tuple, List, Optional, Union

logger = logging.getLogger(__name__)

class ImageEditor:
    """Advanced Image Editor with 30+ Effects"""
    
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from path"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        return img
    
    def save_image(self, img: np.ndarray, output_path: str) -> str:
        """Save image to path"""
        cv2.imwrite(output_path, img)
        return output_path
    
    # ============= BASIC FILTERS =============
    
    def apply_vintage_filter(self, image_path: str) -> np.ndarray:
        """Apply vintage filter"""
        img = self.load_image(image_path)
        img = cv2.applyColorMap(img, cv2.COLORMAP_BONE)
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        return img
    
    def apply_cinematic_filter(self, image_path: str) -> np.ndarray:
        """Apply cinematic filter"""
        img = self.load_image(image_path)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return img
    
    def apply_black_white_filter(self, image_path: str) -> np.ndarray:
        """Apply black and white filter"""
        img = self.load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    def apply_sepia_filter(self, image_path: str) -> np.ndarray:
        """Apply sepia filter"""
        img = self.load_image(image_path).astype(np.float32)
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(img, kernel)
        return np.clip(sepia, 0, 255).astype(np.uint8)
    
    def apply_blur_filter(self, image_path: str, intensity: int = 15) -> np.ndarray:
        """Apply blur filter"""
        img = self.load_image(image_path)
        return cv2.GaussianBlur(img, (intensity, intensity), 0)
    
    def apply_sharpen_filter(self, image_path: str) -> np.ndarray:
        """Apply sharpen filter"""
        img = self.load_image(image_path)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(img, -1, kernel)
    
    def apply_glitch_effect(self, image_path: str) -> np.ndarray:
        """Apply digital glitch effect"""
        img = self.load_image(image_path)
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
            block_w = random.randint(10, 50)
            block_h = random.randint(10, 50)
            img[y:y+block_h, x:x+block_w] = img[y:y+block_h, x:x+block_w][:, ::-1]
        
        # Add noise
        noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        return img
    
    def apply_watercolor_effect(self, image_path: str) -> np.ndarray:
        """Apply watercolor painting effect"""
        img = self.load_image(image_path)
        for _ in range(3):
            img = cv2.bilateralFilter(img, 9, 75, 75)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 9, 10)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.addWeighted(img, 0.7, edges_colored, 0.3, 0)
    
    def apply_oil_painting_effect(self, image_path: str, size: int = 5) -> np.ndarray:
        """Apply oil painting effect"""
        img = self.load_image(image_path)
        h, w = img.shape[:2]
        output = np.zeros_like(img)
        
        for y in range(0, h - size, size):
            for x in range(0, w - size, size):
                patch = img[y:y+size, x:x+size]
                avg_color = np.mean(patch, axis=(0, 1))
                output[y:y+size, x:x+size] = avg_color
        return output
    
    def apply_sketch_effect(self, image_path: str) -> np.ndarray:
        """Apply pencil sketch effect"""
        img = self.load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    def apply_cartoon_effect(self, image_path: str) -> np.ndarray:
        """Apply cartoon effect"""
        img = self.load_image(image_path)
        smooth = cv2.bilateralFilter(img, 9, 75, 75)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 9, 10)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return cv2.bitwise_and(smooth, edges_colored)
    
    def apply_neon_effect(self, image_path: str) -> np.ndarray:
        """Apply neon glow effect"""
        img = self.load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        neon = np.zeros_like(img)
        neon[edges > 0] = [0, 255, 255]
        return cv2.addWeighted(img, 0.5, neon, 0.5, 0)
    
    def apply_pixelate_effect(self, image_path: str, pixel_size: int = 10) -> np.ndarray:
        """Apply pixelation effect"""
        img = self.load_image(image_path)
        h, w = img.shape[:2]
        small = cv2.resize(img, (w // pixel_size, h // pixel_size), 
                          interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    
    def apply_mosaic_effect(self, image_path: str, block_size: int = 15) -> np.ndarray:
        """Apply mosaic effect"""
        img = self.load_image(image_path)
        h, w = img.shape[:2]
        output = img.copy()
        
        for y in range(0, h, block_size):
            for x in range(0, w, block_size):
                block = img[y:min(y+block_size, h), x:min(x+block_size, w)]
                avg_color = np.mean(block, axis=(0, 1))
                output[y:min(y+block_size, h), x:min(x+block_size, w)] = avg_color
        return output
    
    def apply_emboss_effect(self, image_path: str) -> np.ndarray:
        """Apply emboss effect"""
        img = self.load_image(image_path)
        kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
        emboss = cv2.filter2D(img, -1, kernel)
        return emboss + 128
    
    def apply_edge_detect(self, image_path: str) -> np.ndarray:
        """Apply edge detection"""
        img = self.load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def apply_invert(self, image_path: str) -> np.ndarray:
        """Apply invert colors"""
        img = self.load_image(image_path)
        return 255 - img
    
    def apply_vignette(self, image_path: str) -> np.ndarray:
        """Apply vignette effect"""
        img = self.load_image(image_path)
        h, w = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(w, w/2)
        kernel_y = cv2.getGaussianKernel(h, h/2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        for i in range(3):
            img[:,:,i] = (img[:,:,i] * mask).astype(np.uint8)
        return img
    
    def apply_heatmap(self, image_path: str) -> np.ndarray:
        """Apply heatmap effect"""
        img = self.load_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    
    # ============= TEXT & OVERLAY =============
    
    def add_text(self, image_path: str, text: str, position: str = 'center',
                 font_size: int = 40, color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        """Add text to image"""
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load custom font, fallback to default
        try:
            font = ImageFont.truetype("fonts/Poppins-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        if position == 'center':
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
        elif position == 'top':
            x = (img.width - text_width) // 2
            y = 50
        elif position == 'bottom':
            x = (img.width - text_width) // 2
            y = img.height - text_height - 50
        elif position == 'top-left':
            x, y = 20, 20
        elif position == 'top-right':
            x = img.width - text_width - 20
            y = 20
        elif position == 'bottom-left':
            x, y = 20, img.height - text_height - 20
        elif position == 'bottom-right':
            x = img.width - text_width - 20
            y = img.height - text_height - 20
        else:
            x, y = 10, 10
        
        # Add shadow and text
        draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=color, font=font)
        
        return img
    
    def add_watermark(self, image_path: str, watermark_text: str = "Kinva Master") -> Image.Image:
        """Add watermark to image"""
        img = Image.open(image_path).convert('RGBA')
        
        # Create transparent overlay
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        try:
            font = ImageFont.truetype("fonts/Poppins-Regular.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Calculate position (bottom-right)
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = img.width - text_width - 20
        y = img.height - text_height - 20
        
        # Add semi-transparent background
        draw.rectangle([(x-10, y-5), (x+text_width+10, y+text_height+5)], 
                      fill=(0, 0, 0, 128))
        
        # Add text
        draw.text((x, y), watermark_text, fill=(255, 255, 255, 255), font=font)
        
        # Composite
        img = Image.alpha_composite(img, overlay)
        
        return img.convert('RGB')
    
    # ============= RESIZE & CROP =============
    
    def resize_image(self, image_path: str, width: int = None, height: int = None,
                    maintain_ratio: bool = True) -> Image.Image:
        """Resize image"""
        img = Image.open(image_path)
        
        if maintain_ratio:
            if width and not height:
                ratio = width / img.width
                height = int(img.height * ratio)
            elif height and not width:
                ratio = height / img.height
                width = int(img.width * ratio)
        
        width = width or img.width
        height = height or img.height
        
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    def crop_image(self, image_path: str, left: int, top: int, right: int, bottom: int) -> Image.Image:
        """Crop image"""
        img = Image.open(image_path)
        return img.crop((left, top, right, bottom))
    
    def crop_center(self, image_path: str, crop_width: int, crop_height: int) -> Image.Image:
        """Crop from center"""
        img = Image.open(image_path)
        
        left = (img.width - crop_width) // 2
        top = (img.height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        
        return img.crop((left, top, right, bottom))
    
    # ============= COLOR ADJUSTMENT =============
    
    def adjust_brightness(self, image_path: str, factor: float) -> Image.Image:
        """Adjust brightness"""
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def adjust_contrast(self, image_path: str, factor: float) -> Image.Image:
        """Adjust contrast"""
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def adjust_saturation(self, image_path: str, factor: float) -> Image.Image:
        """Adjust saturation"""
        img = Image.open(image_path)
        enhancer = ImageEnhance.Color(img)
        return enhancer.enhance(factor)
    
    def adjust_sharpness(self, image_path: str, factor: float) -> Image.Image:
        """Adjust sharpness"""
        img = Image.open(image_path)
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(factor)
    
    # ============= ROTATION & FLIP =============
    
    def rotate_image(self, image_path: str, angle: int) -> Image.Image:
        """Rotate image"""
        img = Image.open(image_path)
        return img.rotate(angle, expand=True)
    
    def flip_image(self, image_path: str, direction: str) -> Image.Image:
        """Flip image horizontally or vertically"""
        img = Image.open(image_path)
        
        if direction == 'horizontal':
            return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            return img
    
    # ============= BACKGROUND REMOVAL =============
    
    def remove_background(self, image_path: str) -> bytes:
        """Remove background using rembg AI"""
        try:
            from rembg import remove
            with open(image_path, 'rb') as f:
                input_data = f.read()
            return remove(input_data)
        except Exception as e:
            logger.error(f"Background removal error: {e}")
            with open(image_path, 'rb') as f:
                return f.read()
    
    # ============= COLLAGE =============
    
    def create_collage(self, image_paths: List[str], layout: str = 'grid', columns: int = 2) -> Image.Image:
        """Create collage from multiple images"""
        images = [Image.open(path) for path in image_paths]
        
        if layout == 'grid':
            rows = (len(images) + columns - 1) // columns
            max_width = max(img.width for img in images)
            max_height = max(img.height for img in images)
            
            collage = Image.new('RGB', (max_width * columns, max_height * rows), (255, 255, 255))
            
            for i, img in enumerate(images):
                row = i // columns
                col = i % columns
                img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
                collage.paste(img, (col * max_width, row * max_height))
            
            return collage
        
        elif layout == 'horizontal':
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            collage = Image.new('RGB', (total_width, max_height), (255, 255, 255))
            x = 0
            for img in images:
                collage.paste(img, (x, 0))
                x += img.width
            return collage
        
        elif layout == 'vertical':
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            collage = Image.new('RGB', (max_width, total_height), (255, 255, 255))
            y = 0
            for img in images:
                collage.paste(img, (0, y))
                y += img.height
            return collage
        
        else:
            return images[0]
    
    # ============= AI ENHANCEMENT =============
    
    def enhance_image_ai(self, image_path: str) -> np.ndarray:
        """AI-based image enhancement"""
        img = self.load_image(image_path)
        
        # Denoise
        img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)
        
        # Increase contrast
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return img
