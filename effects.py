"""
Gayab Hojao Jutsu Cam - Visual Effects & Particle Engine
Implements Anime Smoke Explosion, Substitution Log Drop, Ki Aura Speedlines, and Particle Dissolve.
"""

import math
import random
import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOG_IMAGE_PATH = ASSETS_DIR / "substitution_log.png"

class SmokeParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float, max_life: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.max_radius = radius * random.uniform(1.8, 3.2)
        self.life = 0.0
        self.max_life = max_life
        self.color = color

    def update(self, dt: float) -> bool:
        self.life += dt
        if self.life >= self.max_life:
            return False
        # Expand and decelerate
        progress = self.life / self.max_life
        self.radius = self.radius + (self.max_radius - self.radius) * 0.12
        self.x += self.vx * (1.0 - progress * 0.7)
        self.y += self.vy * (1.0 - progress * 0.7) - 1.2 # slight buoyancy rise
        return True

class ParticleSystem:
    def __init__(self):
        self.smoke_particles: List[SmokeParticle] = []
        self.dissolve_particles: List[Tuple[float, float, float, float, Tuple[int, int, int], float]] = [] # x, y, vx, vy, color, alpha
        self.active_log = None # dict with log state
        self._log_img = None
        self._load_log_asset()

    def _load_log_asset(self):
        if LOG_IMAGE_PATH.exists():
            img = cv2.imread(str(LOG_IMAGE_PATH), cv2.IMREAD_UNCHANGED)
            if img is not None:
                self._log_img = img

    def trigger_smoke_puff(self, cx: int, cy: int, count: int = 45):
        """Spawns an anime smoke burst at (cx, cy)."""
        self.smoke_particles.clear()
        colors = [
            (240, 240, 245), # bright white smoke
            (210, 215, 225), # light anime grey
            (170, 180, 195), # soft shadow grey
            (255, 255, 255)  # highlight white
        ]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3.0, 14.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(1.0, 4.0)
            radius = random.uniform(25.0, 55.0)
            life = random.uniform(0.7, 1.4)
            color = random.choice(colors)
            px = cx + random.uniform(-40, 40)
            py = cy + random.uniform(-40, 40)
            self.smoke_particles.append(SmokeParticle(px, py, vx, vy, radius, life, color))

    def trigger_substitution_log(self, cx: int, cy: int, target_y: int):
        """Spawns an anime substitution log that drops to the floor."""
        self.active_log = {
            "x": cx,
            "y": float(cy),
            "vy": -4.0, # initial pop up
            "target_y": float(target_y),
            "rotation": random.uniform(-15.0, 15.0),
            "scale": 0.85,
            "grounded": False,
            "life": 4.0
        }

    def trigger_dissolve(self, mask: np.ndarray, frame_bgr: np.ndarray, count: int = 600):
        """Samples glowing particles from user silhouette and flings them outwards."""
        self.dissolve_particles.clear()
        y_indices, x_indices = np.where(mask > 0.5)
        if len(x_indices) == 0:
            return
            
        step = max(1, len(x_indices) // count)
        for i in range(0, len(x_indices), step):
            px = x_indices[i]
            py = y_indices[i]
            # Cyan/Gold mystical color tint
            b = int(frame_bgr[py, px, 0])
            g = int(min(255, frame_bgr[py, px, 1] + 60))
            r = int(min(255, frame_bgr[py, px, 2] + 80))
            
            angle = random.uniform(-math.pi * 0.9, -math.pi * 0.1) # drift upwards
            speed = random.uniform(2.0, 8.0)
            vx = math.cos(angle) * speed + random.uniform(-2, 2)
            vy = math.sin(angle) * speed
            alpha = 1.0
            self.dissolve_particles.append([float(px), float(py), vx, vy, (b, g, r), alpha])

    def update_and_render(self, frame: np.ndarray, dt: float):
        """Renders smoke puffs, substitution log, and particles on top of the frame."""
        h, w = frame.shape[:2]

        # 1. Update & Render Substitution Log
        if self.active_log and self._log_img is not None:
            log = self.active_log
            log["life"] -= dt
            if log["life"] <= 0:
                self.active_log = None
            else:
                if not log["grounded"]:
                    log["vy"] += 38.0 * dt # gravity
                    log["y"] += log["vy"]
                    if log["y"] >= log["target_y"]:
                        log["y"] = log["target_y"]
                        log["vy"] = -log["vy"] * 0.35 # bounce
                        if abs(log["vy"]) < 1.5:
                            log["grounded"] = True
                            
                # Render rotated log image onto frame
                log_h, log_w = self._log_img.shape[:2]
                nw, nh = int(log_w * log["scale"]), int(log_h * log["scale"])
                resized_log = cv2.resize(self._log_img, (nw, nh), interpolation=cv2.INTER_LINEAR)
                
                # Alpha composite
                lx = int(log["x"] - nw // 2)
                ly = int(log["y"] - nh // 2)
                
                # Boundary clipping
                x1, y1 = max(0, lx), max(0, ly)
                x2, y2 = min(w, lx + nw), min(h, ly + nh)
                
                if x2 > x1 and y2 > y1:
                    src_x1, src_y1 = x1 - lx, y1 - ly
                    src_x2, src_y2 = src_x1 + (x2 - x1), src_y1 + (y2 - y1)
                    
                    sub_patch = resized_log[src_y1:src_y2, src_x1:src_x2]
                    alpha_s = sub_patch[:, :, 3] / 255.0
                    alpha_l = 1.0 - alpha_s
                    
                    for c in range(3):
                        frame[y1:y2, x1:x2, c] = (alpha_s * sub_patch[:, :, c] + alpha_l * frame[y1:y2, x1:x2, c])

        # 2. Update & Render Dissolve Particles
        surviving_dissolve = []
        for p in self.dissolve_particles:
            px, py, vx, vy, color, alpha = p
            px += vx
            py += vy
            alpha -= dt * 0.95
            if alpha > 0 and 0 <= int(px) < w and 0 <= int(py) < h:
                ix, iy = int(px), int(py)
                cv2.circle(frame, (ix, iy), random.randint(2, 4), color, -1)
                surviving_dissolve.append([px, py, vx, vy, color, alpha])
        self.dissolve_particles = surviving_dissolve

        # 3. Update & Render Smoke Particles
        surviving_smoke = []
        if self.smoke_particles:
            overlay = frame.copy()
            for p in self.smoke_particles:
                if p.update(dt):
                    surviving_smoke.append(p)
                    progress = p.life / p.max_life
                    alpha = max(0.0, 1.0 - progress) * 0.75
                    ix, iy = int(p.x), int(p.y)
                    ir = max(4, int(p.radius))
                    if 0 <= ix < w and 0 <= iy < h:
                        cv2.circle(overlay, (ix, iy), ir, p.color, -1)
                        # Dark cartoon outline
                        cv2.circle(overlay, (ix, iy), ir, (60, 60, 75), 2)
            # Alpha blend smoke
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            self.smoke_particles = surviving_smoke

    def render_ki_charging(self, frame: np.ndarray, head_pos: Tuple[int, int], charge_progress: float):
        """Renders charging Ki aura energy arcs around forehead/temple."""
        hx, hy = head_pos
        h, w = frame.shape[:2]
        aura_color = (0, 220, 255) # Golden Saiyan glow
        radius = int(45 + 35 * charge_progress)
        
        # Pulsing circle aura
        cv2.circle(frame, (hx, hy), radius, aura_color, 3)
        cv2.circle(frame, (hx, hy), radius + 15, (0, 160, 255), 1)
        
        # Crackling electric lightning arcs
        arcs = int(4 + 8 * charge_progress)
        for _ in range(arcs):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.5, radius * 1.4)
            x1 = int(hx + math.cos(ang) * dist)
            y1 = int(hy + math.sin(ang) * dist)
            x2 = int(x1 + random.uniform(-25, 25))
            y2 = int(y1 + random.uniform(-25, 25))
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

    def render_speedlines(self, frame: np.ndarray):
        """Draws dynamic vertical anime speedlines across the screen during teleport."""
        h, w = frame.shape[:2]
        line_count = 35
        for _ in range(line_count):
            lx = random.randint(0, w)
            length = random.randint(h // 4, h)
            thickness = random.randint(2, 6)
            cv2.line(frame, (lx, 0), (lx, length), (255, 255, 255), thickness)
