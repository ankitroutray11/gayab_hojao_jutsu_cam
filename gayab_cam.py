"""
Gayab Hojao Jutsu Cam (गायब हो जाओ Jutsu Cam)
The Ultimate AI-Powered Desi & Anime Disappearance Webcam Suite
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from audio import play_sound_async
from effects import ParticleSystem
from gestures import evaluate_gestures

APP_DIR = Path(__file__).resolve().parent
MODELS_DIR = APP_DIR / "models"
SEGMENTER_MODEL_PATH = MODELS_DIR / "selfie_segmenter.tflite"
HAND_MODEL_PATH = MODELS_DIR / "hand_landmarker.task"

WINDOW_TITLE = "Gayab Hojao Jutsu Cam - Live Preview"


class GayabCamApp:
    def __init__(self, camera_idx: int = 0, width: int = 1280, height: int = 720, use_virtual_cam: bool = True, mirror: bool = True):
        self.camera_idx = camera_idx
        self.width = width
        self.height = height
        self.use_virtual_cam = use_virtual_cam
        self.mirror = mirror

        # State management
        self.is_vanished = False
        self.active_jutsu = "NONE" # 'NINJA', 'GOKU', 'DISSOLVE'
        self.charging_time = 0.0
        self.required_charge_time = 0.75 # seconds to hold goku pose
        self.cooldown = 0.0 # prevent instant toggling

        # Background calibration
        self.background_frame: Optional[np.ndarray] = None
        self.calibrating = True
        self.calibration_buffer = []
        self.calibration_target_frames = 25

        # VFX & Audio
        self.particle_system = ParticleSystem()
        self.teleport_flash_timer = 0.0

        # Initialize MediaPipe Task Runners
        self._init_models()

    def _init_models(self):
        print("[+] Checking MediaPipe Vision models...")
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        downloads = {
            SEGMENTER_MODEL_PATH: "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter_landscape/float16/latest/selfie_segmenter_landscape.tflite",
            HAND_MODEL_PATH: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
        }
        for path, url in downloads.items():
            if not path.exists():
                print(f"[+] Downloading model: {path.name}...")
                import urllib.request
                urllib.request.urlretrieve(url, str(path))
                print(f"[+] Downloaded {path.name} ({path.stat().st_size} bytes)")

        # 1. Image Segmenter (Selfie Segmentation)
        seg_base_opts = python.BaseOptions(model_asset_path=str(SEGMENTER_MODEL_PATH))
        seg_options = vision.ImageSegmenterOptions(
            base_options=seg_base_opts,
            running_mode=vision.RunningMode.IMAGE,
            output_category_mask=False,
            output_confidence_masks=True
        )
        self.segmenter = vision.ImageSegmenter.create_from_options(seg_options)

        # 2. Hand Landmarker
        hand_base_opts = python.BaseOptions(model_asset_path=str(HAND_MODEL_PATH))
        hand_options = vision.HandLandmarkerOptions(
            base_options=hand_base_opts,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.5
        )
        self.hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)
        print("[+] Models successfully loaded!")

    def calibrate_step(self, frame: np.ndarray) -> bool:
        """Collects calibration frames to compute a clean noise-free background."""
        self.calibration_buffer.append(frame.copy())
        if len(self.calibration_buffer) >= self.calibration_target_frames:
            # Median background across collected frames
            stacked = np.stack(self.calibration_buffer, axis=0)
            self.background_frame = np.median(stacked, axis=0).astype(np.uint8)
            self.calibration_buffer.clear()
            self.calibrating = False
            print("[+] Background calibrated and locked!")
            return True
        return False

    def trigger_ninja_jutsu(self, frame_w: int, frame_h: int):
        """Triggers Gayab Hojao Smoke & Substitution Log."""
        if self.cooldown > 0:
            return
        if not self.is_vanished:
            self.is_vanished = True
            self.active_jutsu = "NINJA"
            self.cooldown = 1.2
            play_sound_async("poof")
            cx, cy = frame_w // 2, frame_h // 2
            self.particle_system.trigger_smoke_puff(cx, cy, count=55)
            self.particle_system.trigger_substitution_log(cx, cy, target_y=frame_h - 110)
            print("[JUTSU] GAYAB HOJAO! Ninja Substitution triggered!")
        else:
            self.reappear("poof")

    def trigger_goku_teleport(self, frame_w: int, frame_h: int):
        """Triggers Instant Transmission teleport."""
        if self.cooldown > 0:
            return
        if not self.is_vanished:
            self.is_vanished = True
            self.active_jutsu = "GOKU"
            self.cooldown = 1.2
            self.teleport_flash_timer = 0.25
            play_sound_async("teleport")
            print("[JUTSU] CHHOO-MANTAR! Instant Transmission teleport triggered!")
        else:
            self.reappear("teleport")

    def trigger_dissolve(self, mask: np.ndarray, frame: np.ndarray):
        """Triggers particle dissolve."""
        if self.cooldown > 0:
            return
        if not self.is_vanished:
            self.is_vanished = True
            self.active_jutsu = "DISSOLVE"
            self.cooldown = 1.2
            play_sound_async("dissolve")
            self.particle_system.trigger_dissolve(mask, frame, count=700)
            print("[JUTSU] THANOS DISSOLVE! Particle disintegration triggered!")
        else:
            self.reappear("dissolve")

    def reappear(self, sfx: str = "reappear"):
        """Rematerializes back into view."""
        self.is_vanished = False
        self.active_jutsu = "NONE"
        self.cooldown = 1.0
        play_sound_async(sfx)
        print("[JUTSU] WAPAS AAO! Rematerialized back into camera view.")

    def run(self):
        cap = cv2.VideoCapture(self.camera_idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not cap.isOpened():
            print(f"[ERROR] Could not open camera at index {self.camera_idx}.")
            return

        # Attempt Virtual Camera setup
        vcam = None
        if self.use_virtual_cam:
            try:
                import pyvirtualcam
                vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=30, fmt=pyvirtualcam.PixelFormat.BGR)
                print(f"[+] Outputting stream to Virtual Camera: {vcam.device}")
            except Exception as e:
                print(f"[INFO] Virtual Camera not active ({e}). Running in window preview mode.")

        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_TITLE, self.width, self.height)

        prev_time = time.time()
        print("\n===========================================================")
        print("     GAYAB HOJAO JUTSU CAM IS READY!")
        print("  * Step out of the frame for 2 seconds to calibrate room background.")
        print("  * Gestures:")
        print("      - Join hands together (Jutsu seal) -> Gayab Hojao Smoke & Log!")
        print("      - 2 fingers to forehead (Goku pose) -> Instant Transmission!")
        print("      - Peace sign (V-sign) -> Particle Dissolve!")
        print("      - Repeat gesture or press [R] -> Reappear!")
        print("  * Keys: [SPACE] Recalibrate BG | [1,2,3] Manual | [Q] Quit")
        print("===========================================================\n")

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if self.mirror:
                    frame = cv2.flip(frame, 1)

                h, w = frame.shape[:2]
                curr_time = time.time()
                dt = curr_time - prev_time
                prev_time = curr_time
                fps = 1.0 / max(dt, 0.001)

                if self.cooldown > 0:
                    self.cooldown = max(0.0, self.cooldown - dt)

                # Calibration Phase
                if self.calibrating:
                    self.calibrate_step(frame)
                    cv2.putText(frame, "CALIBRATING BACKGROUND... PLEASE STEP ASIDE", (w // 2 - 280, h // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
                    cv2.imshow(WINDOW_TITLE, frame)
                    if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                        break
                    continue

                # Prepare frame for MediaPipe (RGB)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                # 1. Segmentation
                seg_result = self.segmenter.segment(mp_image)
                confidence_mask = seg_result.confidence_masks[0].numpy_view()
                person_mask = (confidence_mask > 0.45).astype(np.float32)
                # Smooth mask edges
                person_mask = cv2.GaussianBlur(person_mask, (15, 15), 0)

                # 2. Hand Gesture Evaluation
                hand_result = self.hand_landmarker.detect(mp_image)
                detected_gesture = evaluate_gestures(hand_result.hand_landmarks)

                # Process gestures
                if detected_gesture.name == "NINJA_SEAL":
                    self.trigger_ninja_jutsu(w, h)
                elif detected_gesture.name == "GOKU_TELEPORT":
                    if not self.is_vanished:
                        self.charging_time += dt
                        hx, hy = int(detected_gesture.hand_pos[0] * w), int(detected_gesture.hand_pos[1] * h)
                        progress = min(1.0, self.charging_time / self.required_charge_time)
                        self.particle_system.render_ki_charging(frame, (hx, hy), progress)
                        if self.charging_time >= self.required_charge_time:
                            self.trigger_goku_teleport(w, h)
                            self.charging_time = 0.0
                    else:
                        self.trigger_goku_teleport(w, h)
                elif detected_gesture.name == "V_SIGN":
                    self.trigger_dissolve(person_mask, frame)
                else:
                    self.charging_time = max(0.0, self.charging_time - dt * 2.0)

                # Render output composite
                output_frame = frame.copy()

                if self.is_vanished and self.background_frame is not None:
                    # Blend user out with background
                    bg = cv2.resize(self.background_frame, (w, h))
                    mask_3ch = np.repeat(person_mask[:, :, np.newaxis], 3, axis=2)
                    output_frame = (frame * (1.0 - mask_3ch) + bg * mask_3ch).astype(np.uint8)

                # Render active particles & substitution log
                self.particle_system.update_and_render(output_frame, dt)

                # Render teleport speedlines
                if self.teleport_flash_timer > 0:
                    self.teleport_flash_timer -= dt
                    self.particle_system.render_speedlines(output_frame)

                # Draw Anime HUD Banner
                self._draw_hud(output_frame, fps, detected_gesture.name)

                # Output to Virtual Camera
                if vcam is not None:
                    vcam.send(output_frame)

                # Display preview window
                cv2.imshow(WINDOW_TITLE, output_frame)

                # Keyboard shortcuts
                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), 27): # Q or ESC
                    break
                elif key == 32: # SPACE: Recalibrate
                    print("[+] Recalibrating background... step aside!")
                    self.calibrating = True
                elif key in (ord('r'), ord('R')):
                    self.reappear()
                elif key == ord('1'):
                    self.trigger_ninja_jutsu(w, h)
                elif key == ord('2'):
                    self.trigger_goku_teleport(w, h)
                elif key == ord('3'):
                    self.trigger_dissolve(person_mask, frame)
                elif key in (ord('c'), ord('C')):
                    # Cycle camera
                    cap.release()
                    self.camera_idx = (self.camera_idx + 1) % 4
                    print(f"[+] Switching to camera index {self.camera_idx}...")
                    cap = cv2.VideoCapture(self.camera_idx)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        finally:
            cap.release()
            if vcam is not None:
                vcam.close()
            cv2.destroyAllWindows()
            print("[+] Gayab Cam closed cleanly.")

    def _draw_hud(self, frame: np.ndarray, fps: float, gesture_name: str):
        h, w = frame.shape[:2]
        # Top HUD bar background
        hud_bg = frame[:55, :].copy()
        cv2.rectangle(hud_bg, (0, 0), (w, 55), (20, 20, 25), -1)
        cv2.addWeighted(hud_bg, 0.75, frame[:55, :], 0.25, 0, frame[:55, :])

        # Title & Mode
        status_text = "GAYAB (VANISHED)" if self.is_vanished else "VISIBLE"
        status_color = (0, 60, 255) if self.is_vanished else (0, 255, 120)

        cv2.putText(frame, "GAYAB HOJAO JUTSU CAM", (18, 35), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 220, 255), 2)
        cv2.putText(frame, f"STATUS: {status_text}", (390, 35), cv2.FONT_HERSHEY_DUPLEX, 0.65, status_color, 2)
        cv2.putText(frame, f"GESTURE: {gesture_name}", (720, 35), cv2.FONT_HERSHEY_DUPLEX, 0.60, (220, 220, 220), 1)
        cv2.putText(frame, f"FPS: {int(fps)}", (w - 120, 35), cv2.FONT_HERSHEY_DUPLEX, 0.60, (0, 255, 255), 1)

        # Bottom Shortcut hint banner
        hint_bar = frame[h - 32:h, :].copy()
        cv2.rectangle(hint_bar, (0, 0), (w, 32), (15, 15, 20), -1)
        cv2.addWeighted(hint_bar, 0.7, frame[h - 32:h, :], 0.3, 0, frame[h - 32:h, :])
        hints = "[SPACE] Reset BG | [R] Reappear | [1] Smoke Log | [2] Teleport | [3] Dissolve | [C] Cam | [Q] Quit"
        cv2.putText(frame, hints, (w // 2 - 360, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1)


def main():
    parser = argparse.ArgumentParser(description="Gayab Hojao Jutsu Cam")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--width", type=int, default=1280, help="Video width")
    parser.add_argument("--height", type=int, default=720, help="Video height")
    parser.add_argument("--no-virtual-camera", action="store_true", help="Disable OBS Virtual Camera output")
    parser.add_argument("--no-mirror", action="store_true", help="Disable horizontal webcam mirroring")
    args = parser.parse_args()

    app = GayabCamApp(
        camera_idx=args.camera,
        width=args.width,
        height=args.height,
        use_virtual_cam=not args.no_virtual_camera,
        mirror=not args.no_mirror
    )
    app.run()


if __name__ == "__main__":
    main()
