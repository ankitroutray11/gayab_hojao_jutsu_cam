import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import effects
import gestures


@dataclass
class _Pt:
    x: float
    y: float


def _base_hand(cx: float = 0.5, cy: float = 0.6):
    pts = [_Pt(cx, cy) for _ in range(21)]
    pts[0] = _Pt(cx, cy)  # wrist
    return pts


class TestGestures(unittest.TestCase):
    def test_empty_hands_returns_none(self):
        res = gestures.evaluate_gestures([])
        self.assertEqual(res.name, "NONE")

    def test_v_sign_detected(self):
        hand = _base_hand(0.5, 0.7)
        # Index & Middle extended wide apart
        hand[6] = _Pt(0.46, 0.55)
        hand[8] = _Pt(0.42, 0.40)
        hand[10] = _Pt(0.54, 0.55)
        hand[12] = _Pt(0.58, 0.40)
        # Ring & Pinky curled
        hand[14] = _Pt(0.56, 0.62)
        hand[16] = _Pt(0.56, 0.68)
        hand[18] = _Pt(0.60, 0.64)
        hand[20] = _Pt(0.60, 0.70)
        self.assertTrue(gestures.is_v_sign(hand))
        self.assertEqual(gestures.evaluate_gestures([hand]).name, "V_SIGN")

    def test_goku_teleport_detected(self):
        hand = _base_hand(0.5, 0.45)
        # Index & Middle extended close together in upper forehead region (y < 0.42)
        hand[6] = _Pt(0.49, 0.35)
        hand[8] = _Pt(0.49, 0.22)
        hand[10] = _Pt(0.51, 0.35)
        hand[12] = _Pt(0.51, 0.22)
        # Ring & Pinky curled
        hand[14] = _Pt(0.53, 0.38)
        hand[16] = _Pt(0.53, 0.44)
        hand[18] = _Pt(0.55, 0.40)
        hand[20] = _Pt(0.55, 0.45)
        self.assertTrue(gestures.is_goku_teleport_pose(hand))
        self.assertEqual(gestures.evaluate_gestures([hand]).name, "GOKU_TELEPORT")

    def test_ninja_seal_detected(self):
        h1 = _base_hand(0.48, 0.7)
        h2 = _base_hand(0.52, 0.7)
        for h in (h1, h2):
            h[9] = _Pt(0.50, 0.58)
            h[8] = _Pt(0.50, 0.45)
        self.assertTrue(gestures.is_ninja_seal([h1, h2]))
        self.assertEqual(gestures.evaluate_gestures([h1, h2]).name, "NINJA_SEAL")


class TestEffects(unittest.TestCase):
    def test_smoke_and_log_render(self):
        ps = effects.ParticleSystem()
        ps.trigger_smoke_puff(320, 240, count=15)
        ps.trigger_substitution_log(320, 240, target_y=400)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        ps.update_and_render(frame, 0.033)
        self.assertEqual(frame.shape, (480, 640, 3))
        self.assertGreater(int(frame.sum()), 0)

    def test_dissolve_particles_render(self):
        ps = effects.ParticleSystem()
        mask = np.zeros((100, 100), dtype=np.float32)
        mask[20:80, 20:80] = 1.0
        src = np.full((100, 100, 3), 120, dtype=np.uint8)
        ps.trigger_dissolve(mask, src, count=50)
        self.assertGreater(len(ps.dissolve_particles), 0)
        ps.update_and_render(src, 0.033)


if __name__ == "__main__":
    unittest.main()
