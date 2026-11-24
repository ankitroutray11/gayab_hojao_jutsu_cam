# Gayab Hojao Jutsu Cam (गायब हो जाओ Jutsu Cam) 🥷✨

An AI-powered real-time webcam suite that brings anime & desi disappearance memes to your live camera feed. Powered by **MediaPipe 3D Hand Tracking & Selfie Segmentation**, **OpenCV**, and **PyVirtualCam**.

Outputs directly to **OBS Virtual Camera** (or a clean preview window) so you can vanish mid-call in **Google Meet, Zoom, Discord, and Microsoft Teams**.

---

## ⚡ Jutsu Modes & Gestures

All meme modes are active simultaneously in the same live session without manual switching:

### 1. 🥷 Gayab Hojao Jutsu (Ninja Substitution / Kawarimi)
- **Gesture**: Join both palms together in front of your chest in the classic ninja hand seal.
- **Visuals**: An explosive anime smoke puff erupts across the camera while you vanish, leaving behind an anime substitution wooden log that drops to the floor.
- **Sound**: Ninja smoke poof SFX.

### 2. ⚡ Chhoo-Mantar (Goku Instant Transmission / Shunkan Ido)
- **Gesture**: Touch two joined fingers (index and middle) to your forehead or temple and hold for 0.75 seconds.
- **Visuals**: Charges an animated Super Saiyan Ki aura with crackling lightning arcs, followed by vertical manga speed lines as you teleport out of the frame.
- **Sound**: High-frequency DBZ instant transmission warp SFX.

### 3. ✨ Shanti Dissolve (Thanos Particle Disintegration)
- **Gesture**: Flash a steady Peace Sign (V-sign) with one hand.
- **Visuals**: Your silhouette dissolves into glowing golden and cyan particle dust floating into the air.
- **Sound**: Mystical particle shimmer SFX.

### 4. 🔄 Wapas Aao Jutsu (Reappearance)
- Repeat any gesture or press **`R`** to instantly rematerialize back into view.

---

## 🎮 In-App Controls & Shortcuts

| Key | Action |
| :---: | :--- |
| **`SPACE`** | Recalibrate background (step aside for 2 seconds to capture room background) |
| **`R`** | Reappear / Rematerialize into view |
| **`1`** | Manually trigger Gayab Hojao (Smoke & Log) |
| **`2`** | Manually trigger Instant Transmission Teleport |
| **`3`** | Manually trigger Particle Dissolve |
| **`C`** | Cycle to next connected webcam index (0, 1, 2, ...) |
| **`Q` / `ESC`** | Quit application |

---

## 🚀 Quick Start

### 1. Launch with One Click
Double-click **`start_gayab_cam.bat`** in the project folder.

### 2. Or Run via Python
```bash
python -m pip install -r requirements.txt
python gayab_cam.py
```

### 3. Using in Calls (Google Meet, Discord, Zoom)
1. Launch `gayab_cam.py`.
2. Select **OBS Virtual Camera** (or **Gayab Cam**) as your camera input in your meeting app.
3. If using OBS Studio, select the clean preview window as a Window Capture source.

---

## 🛡️ Privacy & Performance
- **100% Local Inference**: All segmentation, gesture recognition, and particle rendering run entirely on your local machine. No frames or data are ever transmitted or saved.
- **Featherlight & Fast**: Achieves 30+ FPS real-time rendering.
