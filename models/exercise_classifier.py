import numpy as np
from collections import deque

class ExerciseClassifier:
    """
    Classify exercises and count repetitions based on pose data
    Supports: squats, push-ups, bicep curls, lunges, planks
    """

    def __init__(self):
        self.exercise_type = None
        self.counter = 0
        self.stage = None

        # Exercise-specific thresholds
        self.thresholds = {
            'squat': {
                'down_angle': 90,
                'up_angle': 160
            },
            'pushup': {
                'down_angle': 90,
                'up_angle': 160
            },
            'curl': {
                'down_angle': 160,
                'up_angle': 40
            },
            'lunge': {
                'down_angle': 90,
                'up_angle': 160
            }
        }

        # Smoothing buffer
        self.angle_buffer = deque(maxlen=5)

        # Form feedback
        self.form_issues = []

    def set_exercise(self, exercise_type):
        """Set the exercise type to track"""
        self.exercise_type = exercise_type.lower()
        self.counter = 0
        self.stage = None
        self.angle_buffer.clear()
        print(f"Exercise set to: {exercise_type}")

    def smooth_angle(self, angle):
        """Apply moving average smoothing to angle"""
        self.angle_buffer.append(angle)
        return np.mean(self.angle_buffer)

    def classify_squat(self, angles):
        """
        Classify squat exercise and count reps

        Args:
            angles: Dict of body angles

        Returns:
            counter: Rep count
            stage: Current stage (up/down)
        """
        # Use knee angle for squat detection
        knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
        knee_angle = self.smooth_angle(knee_angle)

        # Check form
        self.form_issues = []

        # Squat logic
        if knee_angle < self.thresholds['squat']['down_angle']:
            self.stage = "down"

            # Form check: knees shouldn't go too far forward
            # (simplified check)

        if knee_angle > self.thresholds['squat']['up_angle'] and self.stage == 'down':
            self.stage = "up"
            self.counter += 1

        return self.counter, self.stage, knee_angle

    def classify_pushup(self, angles):
        """
        Classify push-up exercise and count reps

        Args:
            angles: Dict of body angles

        Returns:
            counter: Rep count
            stage: Current stage (up/down)
        """
        # Use elbow angle for push-up detection
        elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
        elbow_angle = self.smooth_angle(elbow_angle)

        # Push-up logic
        if elbow_angle < self.thresholds['pushup']['down_angle']:
            self.stage = "down"

        if elbow_angle > self.thresholds['pushup']['up_angle'] and self.stage == 'down':
            self.stage = "up"
            self.counter += 1

        # Form check
        self.form_issues = []
        shoulder_angle = (angles['left_shoulder'] + angles['right_shoulder']) / 2
        if shoulder_angle < 140:
            self.form_issues.append("Keep body straight")

        return self.counter, self.stage, elbow_angle

    def classify_curl(self, angles):
        """
        Classify bicep curl exercise and count reps

        Args:
            angles: Dict of body angles

        Returns:
            counter: Rep count
            stage: Current stage (up/down)
        """
        # Use elbow angle for curl detection (right arm)
        elbow_angle = angles['right_elbow']
        elbow_angle = self.smooth_angle(elbow_angle)

        # Curl logic (up = flexed, down = extended)
        if elbow_angle < self.thresholds['curl']['up_angle']:
            self.stage = "up"

        if elbow_angle > self.thresholds['curl']['down_angle'] and self.stage == 'up':
            self.stage = "down"
            self.counter += 1

        self.form_issues = []

        return self.counter, self.stage, elbow_angle

    def classify_lunge(self, angles):
        """
        Classify lunge exercise and count reps

        Args:
            angles: Dict of body angles

        Returns:
            counter: Rep count
            stage: Current stage (up/down)
        """
        # Use front knee angle for lunge detection
        front_knee_angle = angles['left_knee']  # Assuming left leg forward
        front_knee_angle = self.smooth_angle(front_knee_angle)

        # Lunge logic
        if front_knee_angle < self.thresholds['lunge']['down_angle']:
            self.stage = "down"

        if front_knee_angle > self.thresholds['lunge']['up_angle'] and self.stage == 'down':
            self.stage = "up"
            self.counter += 1

        self.form_issues = []

        return self.counter, self.stage, front_knee_angle

    def classify(self, angles):
        """
        Main classification method

        Args:
            angles: Dict of body angles

        Returns:
            results: Dict with counter, stage, angle, form_issues
        """
        if not angles:
            return None

        if self.exercise_type == 'squat':
            counter, stage, angle = self.classify_squat(angles)
        elif self.exercise_type == 'pushup':
            counter, stage, angle = self.classify_pushup(angles)
        elif self.exercise_type == 'curl':
            counter, stage, angle = self.classify_curl(angles)
        elif self.exercise_type == 'lunge':
            counter, stage, angle = self.classify_lunge(angles)
        else:
            return None

        return {
            'counter': counter,
            'stage': stage,
            'angle': angle,
            'form_issues': self.form_issues
        }

    def reset(self):
        """Reset counter and stage"""
        self.counter = 0
        self.stage = None
        self.angle_buffer.clear()