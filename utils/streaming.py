#!/usr/bin/env python3
"""
Kinva Master Bot - Streaming Manager
Author: @funnytamilan
"""

import cv2
import numpy as np
import logging
import os
import time
import threading
import queue
from typing import Generator, Dict, Optional, Any
from datetime import datetime
import asyncio
import json

logger = logging.getLogger(__name__)


class StreamManager:
    """Manage video streaming for live editing"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict] = {}
        self.stream_queues: Dict[str, queue.Queue] = {}
        self.stream_threads: Dict[str, threading.Thread] = {}
        self.stream_status: Dict[str, Dict] = {}
        self.max_streams = 10
        self.stream_timeout = 300  # 5 minutes timeout
        
    def generate_frames(self, video_path: str) -> Generator:
        """Generate video frames for streaming"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return
        
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    logger.warning("Failed to encode frame")
                    break
                
                # Control frame rate
                time.sleep(0.033)  # ~30 fps
                
        except Exception as e:
            logger.error(f"Error generating frames: {e}")
        finally:
            cap.release()
    
    def generate_stream_with_effects(self, video_path: str, effects: list = None) -> Generator:
        """Generate video frames with applied effects"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return
        
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break
                
                # Apply effects if any
                if effects:
                    for effect in effects:
                        frame = self._apply_effect(frame, effect)
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.033)
                
        except Exception as e:
            logger.error(f"Error generating stream with effects: {e}")
        finally:
            cap.release()
    
    def start_stream(self, session_id: str, video_path: str, 
                     user_id: int = None, effects: list = None) -> bool:
        """Start a new stream session"""
        try:
            if len(self.active_streams) >= self.max_streams:
                logger.warning(f"Max streams reached, cannot start stream for {session_id}")
                return False
            
            # Create stream queue
            self.stream_queues[session_id] = queue.Queue(maxsize=100)
            
            # Store stream info
            self.active_streams[session_id] = {
                'session_id': session_id,
                'video_path': video_path,
                'user_id': user_id,
                'effects': effects or [],
                'started_at': datetime.now(),
                'last_activity': datetime.now(),
                'viewers': 0,
                'status': 'active'
            }
            
            # Start stream thread
            thread = threading.Thread(
                target=self._stream_worker,
                args=(session_id,),
                daemon=True
            )
            thread.start()
            self.stream_threads[session_id] = thread
            
            logger.info(f"Stream started for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return False
    
    def _stream_worker(self, session_id: str):
        """Background worker for streaming"""
        stream_info = self.active_streams.get(session_id)
        if not stream_info:
            return
        
        video_path = stream_info['video_path']
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Cannot open video for streaming: {video_path}")
            self.stop_stream(session_id)
            return
        
        try:
            frame_count = 0
            while session_id in self.active_streams:
                success, frame = cap.read()
                if not success:
                    # Loop video if needed
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Apply effects
                for effect in stream_info.get('effects', []):
                    frame = self._apply_effect(frame, effect)
                
                # Add timestamp overlay
                frame = self._add_timestamp(frame)
                
                # Add watermark for free users
                if not self._is_premium_user(stream_info.get('user_id')):
                    frame = self._add_watermark(frame)
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_data = buffer.tobytes()
                    
                    # Put in queue for all viewers
                    if session_id in self.stream_queues:
                        try:
                            self.stream_queues[session_id].put(frame_data, timeout=1)
                        except queue.Full:
                            logger.warning(f"Stream queue full for {session_id}")
                
                frame_count += 1
                stream_info['last_activity'] = datetime.now()
                
                # Control frame rate
                time.sleep(0.033)
                
        except Exception as e:
            logger.error(f"Stream worker error: {e}")
        finally:
            cap.release()
            self._cleanup_stream(session_id)
    
    def get_stream_frames(self, session_id: str) -> Generator:
        """Get frames from stream queue"""
        if session_id not in self.stream_queues:
            return
        
        stream_queue = self.stream_queues[session_id]
        
        try:
            while session_id in self.active_streams:
                try:
                    frame_data = stream_queue.get(timeout=5)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                except queue.Empty:
                    # Send heartbeat
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting stream frames: {e}")
    
    def stop_stream(self, session_id: str) -> bool:
        """Stop an active stream"""
        try:
            if session_id in self.active_streams:
                self.active_streams[session_id]['status'] = 'stopping'
                
                # Clear queue
                if session_id in self.stream_queues:
                    while not self.stream_queues[session_id].empty():
                        try:
                            self.stream_queues[session_id].get_nowait()
                        except queue.Empty:
                            break
                
                # Remove from active streams
                del self.active_streams[session_id]
                
                logger.info(f"Stream stopped for session: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
            return False
    
    def _cleanup_stream(self, session_id: str):
        """Clean up stream resources"""
        try:
            if session_id in self.stream_queues:
                del self.stream_queues[session_id]
            
            if session_id in self.stream_threads:
                del self.stream_threads[session_id]
            
            if session_id in self.stream_status:
                del self.stream_status[session_id]
                
        except Exception as e:
            logger.error(f"Error cleaning up stream: {e}")
    
    def add_effect(self, session_id: str, effect: str) -> bool:
        """Add effect to active stream"""
        if session_id not in self.active_streams:
            return False
        
        stream_info = self.active_streams[session_id]
        if effect not in stream_info['effects']:
            stream_info['effects'].append(effect)
            stream_info['last_activity'] = datetime.now()
            logger.info(f"Effect {effect} added to stream {session_id}")
            return True
        
        return False
    
    def remove_effect(self, session_id: str, effect: str) -> bool:
        """Remove effect from active stream"""
        if session_id not in self.active_streams:
            return False
        
        stream_info = self.active_streams[session_id]
        if effect in stream_info['effects']:
            stream_info['effects'].remove(effect)
            stream_info['last_activity'] = datetime.now()
            logger.info(f"Effect {effect} removed from stream {session_id}")
            return True
        
        return False
    
    def get_stream_info(self, session_id: str) -> Optional[Dict]:
        """Get information about active stream"""
        if session_id in self.active_streams:
            info = self.active_streams[session_id].copy()
            info['duration'] = (datetime.now() - info['started_at']).seconds
            return info
        return None
    
    def get_all_streams(self) -> Dict[str, Dict]:
        """Get all active streams"""
        streams = {}
        for sid, info in self.active_streams.items():
            streams[sid] = {
                'session_id': sid,
                'user_id': info['user_id'],
                'effects': info['effects'],
                'duration': (datetime.now() - info['started_at']).seconds,
                'viewers': info['viewers'],
                'status': info['status']
            }
        return streams
    
    def is_streaming(self, session_id: str) -> bool:
        """Check if stream is active"""
        return session_id in self.active_streams
    
    def add_viewer(self, session_id: str) -> bool:
        """Add a viewer to stream"""
        if session_id in self.active_streams:
            self.active_streams[session_id]['viewers'] += 1
            return True
        return False
    
    def remove_viewer(self, session_id: str) -> bool:
        """Remove a viewer from stream"""
        if session_id in self.active_streams:
            self.active_streams[session_id]['viewers'] = max(0, 
                self.active_streams[session_id]['viewers'] - 1)
            return True
        return False
    
    def _apply_effect(self, frame: np.ndarray, effect: str) -> np.ndarray:
        """Apply effect to frame"""
        try:
            if effect == 'vintage':
                frame = cv2.applyColorMap(frame, cv2.COLORMAP_BONE)
                noise = np.random.randint(0, 30, frame.shape, dtype=np.uint8)
                frame = cv2.add(frame, noise)
                
            elif effect == 'black_white':
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                
            elif effect == 'sepia':
                frame = frame.astype(np.float32)
                kernel = np.array([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]])
                frame = cv2.transform(frame, kernel)
                frame = np.clip(frame, 0, 255).astype(np.uint8)
                
            elif effect == 'blur':
                frame = cv2.GaussianBlur(frame, (15, 15), 0)
                
            elif effect == 'glitch':
                h, w = frame.shape[:2]
                channel = np.random.randint(0, 2)
                shift = np.random.randint(-20, 20)
                frame[:, :, channel] = np.roll(frame[:, :, channel], shift, axis=1)
                
            elif effect == 'neon':
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                kernel = np.ones((3,3), np.uint8)
                edges = cv2.dilate(edges, kernel, iterations=1)
                neon = np.zeros_like(frame)
                neon[edges > 0] = [0, 255, 255]
                frame = cv2.addWeighted(frame, 0.5, neon, 0.5, 0)
                
            return frame
            
        except Exception as e:
            logger.error(f"Error applying effect {effect}: {e}")
            return frame
    
    def _add_timestamp(self, frame: np.ndarray) -> np.ndarray:
        """Add timestamp overlay to frame"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, timestamp, (10, 30), font, 0.7, (255, 255, 255), 2)
            return frame
        except:
            return frame
    
    def _add_watermark(self, frame: np.ndarray) -> np.ndarray:
        """Add watermark for free users"""
        try:
            watermark = "Kinva Master"
            font = cv2.FONT_HERSHEY_SIMPLEX
            h, w = frame.shape[:2]
            cv2.putText(frame, watermark, (w - 150, h - 20), font, 0.5, (255, 255, 255), 1)
            return frame
        except:
            return frame
    
    def _is_premium_user(self, user_id: int) -> bool:
        """Check if user is premium"""
        # This would connect to database
        return False
    
    def cleanup_inactive_streams(self):
        """Clean up inactive streams (timeout)"""
        now = datetime.now()
        inactive = []
        
        for sid, info in self.active_streams.items():
            last_activity = info.get('last_activity', info.get('started_at'))
            if last_activity and (now - last_activity).seconds > self.stream_timeout:
                inactive.append(sid)
        
        for sid in inactive:
            self.stop_stream(sid)
            logger.info(f"Cleaned up inactive stream: {sid}")
        
        return len(inactive)
