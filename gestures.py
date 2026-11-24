"""
Gayab Hojao Jutsu Cam - Gesture & Hand Pose Detection Module
Detects Ninja Hand Seals, Goku Teleport forehead touch, and Peace Sign Dissolve.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class DetectedGesture:
    name: str # 'NINJA_SEAL', 'GOKU_TELEPORT', 'V_SIGN', or 'NONE'
    confidence: float
    hand_pos: Tuple[float, float] = (0.5, 0.5)

def _dist(p1, p2) -> float:
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def is_v_sign(landmarks) -> bool:
    """Checks if a hand is forming a clear V / Peace sign."""
    # Landmarks:
    # 0: WRIST, 4: THUMB_TIP, 8: INDEX_TIP, 6: INDEX_PIP
    # 12: MIDDLE_TIP, 10: MIDDLE_PIP, 16: RING_TIP, 14: RING_PIP
    # 20: PINKY_TIP, 18: PINKY_PIP
    wrist = landmarks[0]
    
    # Index & Middle extended: tips higher than PIP joints
    index_extended = landmarks[8].y < landmarks[6].y
    middle_extended = landmarks[12].y < landmarks[10].y
    
    # Ring & Pinky curled: tips lower than or close to PIP joints
    ring_curled = landmarks[16].y > landmarks[14].y or _dist(landmarks[16], wrist) < _dist(landmarks[14], wrist)
    pinky_curled = landmarks[20].y > landmarks[18].y or _dist(landmarks[20], wrist) < _dist(landmarks[18], wrist)
    
    # Check separation between index and middle
    tips_separated = _dist(landmarks[8], landmarks[12]) > 0.04
    
    return index_extended and middle_extended and ring_curled and pinky_curled and tips_separated

def is_goku_teleport_pose(landmarks) -> bool:
    """Checks if index & middle fingers are extended together and near upper face/forehead."""
    wrist = landmarks[0]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    
    # Extended upwards
    index_extended = index_tip.y < landmarks[6].y
    middle_extended = middle_tip.y < landmarks[10].y
    
    # Fingers are held together (not wide like V sign)
    fingers_together = _dist(index_tip, middle_tip) < 0.065
    
    # Ring and pinky curled
    ring_curled = landmarks[16].y > landmarks[14].y or _dist(landmarks[16], wrist) < _dist(landmarks[14], wrist)
    pinky_curled = landmarks[20].y > landmarks[18].y or _dist(landmarks[20], wrist) < _dist(landmarks[18], wrist)
    
    # Position: upper half of screen (forehead / temple region)
    near_forehead = index_tip.y < 0.42
    
    return index_extended and middle_extended and fingers_together and ring_curled and pinky_curled and near_forehead

def is_ninja_seal(hands_landmarks) -> bool:
    """
    Checks if two hands are pressed together in front of torso/chest in a Ninja Jutsu hand seal.
    """
    if len(hands_landmarks) < 2:
        return False
        
    hand1 = hands_landmarks[0]
    hand2 = hands_landmarks[1]
    
    wrist1 = hand1[0]
    wrist2 = hand2[0]
    
    # Distance between wrists
    wrist_dist = _dist(wrist1, wrist2)
    
    # Distance between palms / index knuckles (landmarks 5 and 9)
    palm1 = hand1[9]
    palm2 = hand2[9]
    palm_dist = _dist(palm1, palm2)
    
    # Index fingertips close together
    tip1 = hand1[8]
    tip2 = hand2[8]
    tip_dist = _dist(tip1, tip2)
    
    # Hands pointing generally upward
    pointing_up1 = hand1[8].y < hand1[0].y
    pointing_up2 = hand2[8].y < hand2[0].y
    
    # Both hands joined tightly in chest/torso zone
    hands_joined = (wrist_dist < 0.32 and palm_dist < 0.22 and tip_dist < 0.18)
    
    return hands_joined and pointing_up1 and pointing_up2

def evaluate_gestures(hands_landmarks) -> DetectedGesture:
    """Evaluates all visible hands and returns the detected active gesture."""
    if not hands_landmarks:
        return DetectedGesture(name="NONE", confidence=0.0)
        
    # Check 1: Ninja hand seal (two hands required)
    if is_ninja_seal(hands_landmarks):
        cx = (hands_landmarks[0][0].x + hands_landmarks[1][0].x) / 2.0
        cy = (hands_landmarks[0][8].y + hands_landmarks[1][8].y) / 2.0
        return DetectedGesture(name="NINJA_SEAL", confidence=0.95, hand_pos=(cx, cy))
        
    # Check single hand poses
    for hand in hands_landmarks:
        if is_goku_teleport_pose(hand):
            tip = hand[8]
            return DetectedGesture(name="GOKU_TELEPORT", confidence=0.92, hand_pos=(tip.x, tip.y))
            
        if is_v_sign(hand):
            tip = hand[8]
            return DetectedGesture(name="V_SIGN", confidence=0.90, hand_pos=(tip.x, tip.y))
            
    return DetectedGesture(name="NONE", confidence=0.0)
