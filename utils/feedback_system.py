import numpy as np
from datetime import datetime

class FeedbackSystem:
    """
    Real-time feedback system for exercise form
    Provides corrective guidance and performance metrics
    """

    def __init__(self):
        self.session_start = None
        self.session_data = {
            'total_reps': 0,
            'form_warnings': [],
            'angles_history': [],
            'timestamps': []
        }

    def start_session(self):
        """Start a new exercise session"""
        self.session_start = datetime.now()
        self.session_data = {
            'total_reps': 0,
            'form_warnings': [],
            'angles_history': [],
            'timestamps': []
        }
        print("Session started!")

    def check_squat_form(self, keypoints, angles):
        """
        Check squat form and provide feedback

        Args:
            keypoints: Dict of keypoints
            angles: Dict of body angles

        Returns:
            feedback: List of form corrections
        """
        feedback = []

        # Check knee alignment
        knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
        if knee_angle < 70:
            feedback.append("⚠️ Don't squat too deep - knees at 90°")

        # Check back straightness (simplified)
        hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
        if hip_angle < 130:
            feedback.append("⚠️ Keep back straight")

        # Check depth
        if knee_angle > 110:
            feedback.append("💡 Go deeper for better results")

        return feedback

    def check_pushup_form(self, keypoints, angles):
        """
        Check push-up form and provide feedback

        Args:
            keypoints: Dict of keypoints
            angles: Dict of body angles

        Returns:
            feedback: List of form corrections
        """
        feedback = []

        # Check elbow angle
        elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
        if elbow_angle < 70:
            feedback.append("⚠️ Don't go too low - elbows at 90°")

        # Check body alignment
        shoulder_angle = (angles['left_shoulder'] + angles['right_shoulder']) / 2
        hip_angle = (angles['left_hip'] + angles['right_hip']) / 2

        if abs(shoulder_angle - hip_angle) > 20:
            feedback.append("⚠️ Keep body straight - engage core")

        # Check elbow flare
        if elbow_angle < 45:
            feedback.append("💡 Tuck elbows closer to body")

        return feedback

    def check_curl_form(self, keypoints, angles):
        """
        Check bicep curl form and provide feedback

        Args:
            keypoints: Dict of keypoints
            angles: Dict of body angles

        Returns:
            feedback: List of form corrections
        """
        feedback = []

        # Check elbow position (should stay at sides)
        left_shoulder = keypoints['left_shoulder']
        left_elbow = keypoints['left_elbow']

        # Check if elbow moves forward too much
        if abs(left_elbow['y'] - left_shoulder['y']) < 50:
            feedback.append("⚠️ Keep elbows at your sides")

        # Check full range of motion
        elbow_angle = angles['right_elbow']
        if elbow_angle < 30:
            feedback.append("✓ Good form - full contraction")
        elif elbow_angle < 50:
            feedback.append("💡 Contract bicep fully")

        if elbow_angle > 170:
            feedback.append("✓ Good extension")

        return feedback

    def check_lunge_form(self, keypoints, angles):
        """
        Check lunge form and provide feedback

        Args:
            keypoints: Dict of keypoints
            angles: Dict of body angles

        Returns:
            feedback: List of form corrections
        """
        feedback = []

        # Check front knee angle
        front_knee = angles['left_knee']
        if front_knee < 80:
            feedback.append("⚠️ Front knee going too far forward")

        # Check back knee
        back_knee = angles['right_knee']
        if back_knee > 120:
            feedback.append("💡 Lower back knee more")

        # Check torso upright
        hip_angle = angles['left_hip']
        if hip_angle < 160:
            feedback.append("⚠️ Keep torso upright")

        return feedback

    def get_feedback(self, exercise_type, keypoints, angles):
        """
        Get exercise-specific feedback

        Args:
            exercise_type: Type of exercise
            keypoints: Dict of keypoints
            angles: Dict of body angles

        Returns:
            feedback: List of feedback messages
        """
        if exercise_type == 'squat':
            return self.check_squat_form(keypoints, angles)
        elif exercise_type == 'pushup':
            return self.check_pushup_form(keypoints, angles)
        elif exercise_type == 'curl':
            return self.check_curl_form(keypoints, angles)
        elif exercise_type == 'lunge':
            return self.check_lunge_form(keypoints, angles)
        else:
            return []

    def log_rep(self, rep_count, angles):
        """Log a completed repetition"""
        self.session_data['total_reps'] = rep_count
        self.session_data['angles_history'].append(angles)
        self.session_data['timestamps'].append(datetime.now())

    def get_session_summary(self):
        """
        Get session summary statistics

        Returns:
            summary: Dict with session metrics
        """
        if not self.session_start:
            return None

        duration = (datetime.now() - self.session_start).total_seconds()

        summary = {
            'duration_seconds': duration,
            'duration_formatted': f"{int(duration // 60)}m {int(duration % 60)}s",
            'total_reps': self.session_data['total_reps'],
            'avg_reps_per_minute': (self.session_data['total_reps'] / duration * 60) if duration > 0 else 0,
            'form_warnings_count': len(self.session_data['form_warnings'])
        }

        return summary
