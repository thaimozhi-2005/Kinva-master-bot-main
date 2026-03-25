#!/usr/bin/env python3
"""
Kinva Master Bot - Advanced Video Editor
Author: @funnytamilan
"""

import moviepy.editor as mp
import cv2
import numpy as np
import logging
import os
import random
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class VideoEditor:
    """Advanced Video Editor with 20+ Effects"""
    
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def load_video(self, video_path: str) -> mp.VideoFileClip:
        """Load video from path"""
        try:
            return mp.VideoFileClip(video_path)
        except Exception as e:
            logger.error(f"Error loading video: {e}")
            raise
    
    def save_video(self, clip: mp.VideoFileClip, output_path: str, 
                   codec: str = 'libx264', audio_codec: str = 'aac') -> str:
        """Save video clip to path"""
        try:
            clip.write_videofile(output_path, codec=codec, audio_codec=audio_codec)
            clip.close()
            return output_path
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            raise
    
    # ============= BASIC EDITING =============
    
    def trim_video(self, video_path: str, start_time: float, end_time: float) -> mp.VideoFileClip:
        """Trim video between timestamps"""
        video = self.load_video(video_path)
        return video.subclip(start_time, end_time)
    
    def merge_videos(self, video_paths: List[str]) -> mp.VideoFileClip:
        """Merge multiple videos"""
        clips = [self.load_video(path) for path in video_paths]
        return mp.concatenate_videoclips(clips, method="compose")
    
    def change_speed(self, video_path: str, speed_factor: float) -> mp.VideoFileClip:
        """Change video playback speed"""
        video = self.load_video(video_path)
        return video.fx(mp.vfx.speedx, speed_factor)
    
    def reverse_video(self, video_path: str) -> mp.VideoFileClip:
        """Reverse video"""
        video = self.load_video(video_path)
        return video.fx(mp.vfx.time_mirror)
    
    # ============= AUDIO EDITING =============
    
    def add_music(self, video_path: str, music_path: str, volume: float = 0.5) -> mp.VideoFileClip:
        """Add background music to video"""
        video = self.load_video(video_path)
        audio = mp.AudioFileClip(music_path)
        
        # Loop music if needed
        if audio.duration < video.duration:
            audio = audio.loop(duration=video.duration)
        else:
            audio = audio.subclip(0, video.duration)
        
        # Adjust volume
        audio = audio.volumex(volume)
        
        # Mix with original audio
        if video.audio:
            final_audio = mp.CompositeAudioClip([video.audio, audio])
        else:
            final_audio = audio
        
        return video.set_audio(final_audio)
    
    def remove_audio(self, video_path: str) -> mp.VideoFileClip:
        """Remove audio from video"""
        video = self.load_video(video_path)
        return video.without_audio()
    
    def extract_audio(self, video_path: str) -> mp.AudioFileClip:
        """Extract audio from video"""
        video = self.load_video(video_path)
        return video.audio
    
    # ============= VIDEO EFFECTS =============
    
    def apply_vhs_effect(self, video_path: str) -> mp.VideoFileClip:
        """Apply VHS retro effect"""
        video = self.load_video(video_path)
        
        def vhs_frame(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            height = frame.shape[0]
            
            # Add scanlines
            frame[::2] = frame[::2] * 0.7
            
            # Add chromatic aberration
            frame_red = frame.copy()
            frame_red[:,:,0] = np.roll(frame_red[:,:,0], 2, axis=1)
            frame_blue = frame.copy()
            frame_blue[:,:,2] = np.roll(frame_blue[:,:,2], -2, axis=1)
            frame = cv2.addWeighted(frame_red, 0.33, frame_blue, 0.33, 0)
            
            # Add noise
            noise = np.random.randint(0, 20, frame.shape, dtype=np.float32)
            frame = frame + noise
            
            return np.clip(frame, 0, 255).astype(np.uint8)
        
        return video.fl(vhs_frame)
    
    def apply_glitch_effect(self, video_path: str) -> mp.VideoFileClip:
        """Apply digital glitch effect"""
        video = self.load_video(video_path)
        
        def glitch_frame(get_frame, t):
            frame = get_frame(t)
            
            # Random glitch
            if random.random() < 0.05:
                h, w = frame.shape[:2]
                # Add random color shift
                for channel in range(3):
                    if random.random() < 0.3:
                        shift = random.randint(-30, 30)
                        frame[:, :, channel] = np.roll(frame[:, :, channel], shift, axis=1)
                
                # Add random blocks
                if random.random() < 0.5:
                    x = random.randint(0, w - 100)
                    y = random.randint(0, h - 100)
                    block_w = random.randint(20, 100)
                    block_h = random.randint(20, 100)
                    frame[y:y+block_h, x:x+block_w] = frame[y:y+block_h, x:x+block_w][:, ::-1]
            
            return frame
        
        return video.fl(glitch_frame)
    
    def apply_black_white(self, video_path: str) -> mp.VideoFileClip:
        """Apply black and white effect"""
        video = self.load_video(video_path)
        
        def bw_frame(get_frame, t):
            frame = get_frame(t)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        return video.fl(bw_frame)
    
    def apply_sepia(self, video_path: str) -> mp.VideoFileClip:
        """Apply sepia effect"""
        video = self.load_video(video_path)
        
        def sepia_frame(get_frame, t):
            frame = get_frame(t).astype(np.float32)
            kernel = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]])
            sepia = cv2.transform(frame, kernel)
            return np.clip(sepia, 0, 255).astype(np.uint8)
        
        return video.fl(sepia_frame)
    
    def apply_blur_effect(self, video_path: str, intensity: int = 5) -> mp.VideoFileClip:
        """Apply blur effect"""
        video = self.load_video(video_path)
        
        def blur_frame(get_frame, t):
            frame = get_frame(t)
            return cv2.GaussianBlur(frame, (intensity, intensity), 0)
        
        return video.fl(blur_frame)
    
    def apply_zoom_in(self, video_path: str, zoom: float = 1.2) -> mp.VideoFileClip:
        """Apply zoom in effect"""
        video = self.load_video(video_path)
        
        def zoom_frame(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            new_h = int(h / zoom)
            new_w = int(w / zoom)
            y1 = (h - new_h) // 2
            x1 = (w - new_w) // 2
            cropped = frame[y1:y1+new_h, x1:x1+new_w]
            return cv2.resize(cropped, (w, h))
        
        return video.fl(zoom_frame)
    
    def apply_zoom_out(self, video_path: str, zoom: float = 0.8) -> mp.VideoFileClip:
        """Apply zoom out effect"""
        video = self.load_video(video_path)
        
        def zoom_out_frame(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            new_h = int(h * zoom)
            new_w = int(w * zoom)
            resized = cv2.resize(frame, (new_w, new_h))
            output = np.zeros((h, w, 3), dtype=np.uint8)
            y1 = (h - new_h) // 2
            x1 = (w - new_w) // 2
            output[y1:y1+new_h, x1:x1+new_w] = resized
            return output
        
        return video.fl(zoom_out_frame)
    
    def apply_shake(self, video_path: str, intensity: int = 5) -> mp.VideoFileClip:
        """Apply shake effect"""
        video = self.load_video(video_path)
        
        def shake_frame(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            dx = random.randint(-intensity, intensity)
            dy = random.randint(-intensity, intensity)
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            return cv2.warpAffine(frame, M, (w, h))
        
        return video.fl(shake_frame)
    
    def apply_glow(self, video_path: str) -> mp.VideoFileClip:
        """Apply glow effect"""
        video = self.load_video(video_path)
        
        def glow_frame(get_frame, t):
            frame = get_frame(t)
            blurred = cv2.GaussianBlur(frame, (15, 15), 0)
            return cv2.addWeighted(frame, 0.7, blurred, 0.3, 0)
        
        return video.fl(glow_frame)
    
    def apply_fade_in(self, video_path: str, duration: float = 1.0) -> mp.VideoFileClip:
        """Apply fade in effect"""
        video = self.load_video(video_path)
        
        def fade_in_frame(get_frame, t):
            frame = get_frame(t)
            if t < duration:
                alpha = t / duration
                return (frame * alpha).astype(np.uint8)
            return frame
        
        return video.fl(fade_in_frame)
    
    def apply_fade_out(self, video_path: str, duration: float = 1.0) -> mp.VideoFileClip:
        """Apply fade out effect"""
        video = self.load_video(video_path)
        
        def fade_out_frame(get_frame, t):
            frame = get_frame(t)
            if t > video.duration - duration:
                alpha = (video.duration - t) / duration
                return (frame * alpha).astype(np.uint8)
            return frame
        
        return video.fl(fade_out_frame)
    
    def apply_retro(self, video_path: str) -> mp.VideoFileClip:
        """Apply retro effect"""
        video = self.load_video(video_path)
        
        def retro_frame(get_frame, t):
            frame = get_frame(t)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sepia = cv2.applyColorMap(gray, cv2.COLORMAP_BONE)
            noise = np.random.randint(0, 40, sepia.shape, dtype=np.uint8)
            return cv2.add(sepia, noise)
        
        return video.fl(retro_frame)
    
    # ============= TRANSITIONS =============
    
    def add_fade_transition(self, video_paths: List[str], fade_duration: float = 0.5) -> mp.VideoFileClip:
        """Add fade transition between clips"""
        clips = [self.load_video(path) for path in video_paths]
        
        for i, clip in enumerate(clips):
            if i > 0:
                clip = clip.crossfadein(fade_duration)
            clips[i] = clip
        
        return mp.concatenate_videoclips(clips, method="compose")
    
    # ============= TEXT & SUBTITLES =============
    
    def add_text_overlay(self, video_path: str, text: str, duration: float = 3,
                         position: str = "center", font_size: int = 40) -> mp.VideoFileClip:
        """Add text overlay to video"""
        video = self.load_video(video_path)
        
        # Create text clip
        txt_clip = mp.TextClip(text, fontsize=font_size, color='white', 
                               font='Arial', stroke_color='black', stroke_width=2)
        txt_clip = txt_clip.set_position(position).set_duration(duration)
        
        # Composite
        final = mp.CompositeVideoClip([video, txt_clip])
        return final.set_duration(video.duration)
    
    def add_subtitles(self, video_path: str, subtitles: List[Dict]) -> mp.VideoFileClip:
        """Add subtitles to video"""
        video = self.load_video(video_path)
        
        text_clips = []
        for sub in subtitles:
            txt_clip = mp.TextClip(sub['text'], fontsize=24, color='white', 
                                   font='Arial', stroke_color='black', stroke_width=1)
            txt_clip = (txt_clip.set_position(('center', 'bottom'))
                       .set_start(sub['start'])
                       .set_duration(sub['duration']))
            text_clips.append(txt_clip)
        
        final = mp.CompositeVideoClip([video] + text_clips)
        return final
    
    # ============= COMPRESSION & QUALITY =============
    
    def compress_video(self, video_path: str, target_size_mb: float = 10) -> str:
        """Compress video to target size"""
        video = self.load_video(video_path)
        duration = video.duration
        target_bitrate = (target_size_mb * 8 * 1024) / duration
        
        output_path = f"{self.temp_dir}/compressed_{os.path.basename(video_path)}"
        video.write_videofile(output_path, bitrate=f'{target_bitrate}k',
                             codec='libx264', audio_codec='aac')
        video.close()
        return output_path
    
    def change_resolution(self, video_path: str, width: int, height: int) -> mp.VideoFileClip:
        """Change video resolution"""
        video = self.load_video(video_path)
        return video.resize((width, height))
    
    def upscale_to_4k(self, video_path: str) -> mp.VideoFileClip:
        """Upscale video to 4K"""
        video = self.load_video(video_path)
        return video.resize((3840, 2160))
    
    # ============= SLOW MOTION & TIMELAPSE =============
    
    def slow_motion(self, video_path: str, factor: float = 0.5) -> mp.VideoFileClip:
        """Create slow motion effect"""
        video = self.load_video(video_path)
        return video.fx(mp.vfx.speedx, factor)
    
    def timelapse(self, video_path: str, factor: float = 2.0) -> mp.VideoFileClip:
        """Create timelapse effect"""
        video = self.load_video(video_path)
        return video.fx(mp.vfx.speedx, factor)
    
    # ============= ROTATION =============
    
    def rotate_video(self, video_path: str, angle: int) -> mp.VideoFileClip:
        """Rotate video"""
        video = self.load_video(video_path)
        
        def rotate_frame(get_frame, t):
            frame = get_frame(t)
            if angle == 90:
                return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif angle == 180:
                return cv2.rotate(frame, cv2.ROTATE_180)
            elif angle == 270:
                return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            return frame
        
        return video.fl(rotate_frame)
    
    # ============= VIDEO INFO =============
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get video information"""
        video = self.load_video(video_path)
        info = {
            'duration': video.duration,
            'size': (video.size[0], video.size[1]),
            'fps': video.fps,
            'audio': video.audio is not None,
            'path': video_path
        }
        video.close()
        return info
    
    # ============= CUT VIDEO =============
    
    def cut_video(self, video_path: str, segments: List[Tuple[float, float]]) -> mp.VideoFileClip:
        """Cut multiple segments from video"""
        video = self.load_video(video_path)
        clips = [video.subclip(start, end) for start, end in segments]
        return mp.concatenate_videoclips(clips)
    
    # ============= EXTRACT FRAMES =============
    
    def extract_frames(self, video_path: str, interval: int = 30) -> List[np.ndarray]:
        """Extract frames from video"""
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        return frames
