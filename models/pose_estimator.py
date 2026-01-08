import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    """
    Real-time Pose Estimation using MediaPipe
    Detects 33 body keypoints with 3D coordinates
    """

    def __init__(self, static_mode=False, model_complexity=1, 
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize MediaPipe Pose

        Args:
            static_mode: Whether to treat input as static images
            model_complexity: 0=Lite, 1=Full, 2=Heavy
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.pose = self.mp_pose.Pose(
            static_image_mode=static_mode,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        # Keypoint names (33 landmarks)
        self.keypoint_names = [
            'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
            'right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
            'left_index', 'right_index', 'left_thumb', 'right_thumb',
            'left_hip', 'right_hip', 'left_knee', 'right_knee',
            'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
            'left_foot_index', 'right_foot_index'
        ]

    def detect_pose(self, image):
        """
        Detect pose landmarks in image

        Args:
            image: Input image (BGR format)

        Returns:
            landmarks: Pose landmarks
            image_rgb: RGB image for processing
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Process
        results = self.pose.process(image_rgb)

        image_rgb.flags.writeable = True

        return results, image_rgb

    def extract_keypoints(self, results, image_shape):
        """
        Extract keypoint coordinates from results

        Args:
            results: MediaPipe pose results
            image_shape: Shape of input image (height, width)

        Returns:
            keypoints: Dict with keypoint coordinates and confidence
        """
        if not results.pose_landmarks:
            return None

        h, w = image_shape[:2]
        keypoints = {}

        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            keypoint_name = self.keypoint_names[idx]

            keypoints[keypoint_name] = {
                'x': landmark.x * w,  # Pixel coordinates
                'y': landmark.y * h,
                'z': landmark.z,      # Depth (relative to hips)
                'visibility': landmark.visibility,
                'normalized_x': landmark.x,  # Normalized [0, 1]
                'normalized_y': landmark.y,
                'normalized_z': landmark.z
            }

        return keypoints

    def draw_landmarks(self, image, results):
        """
        Draw pose landmarks on image

        Args:
            image: Input image
            results: MediaPipe pose results

        Returns:
            annotated_image: Image with drawn landmarks
        """
        annotated_image = image.copy()

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )

        return annotated_image

    def calculate_angle(self, point1, point2, point3):
        """
        Calculate angle between three points

        Args:
            point1, point2, point3: Keypoint dicts with x, y coordinates

        Returns:
            angle: Angle in degrees
        """
        # Extract coordinates
        a = np.array([point1['x'], point1['y']])
        b = np.array([point2['x'], point2['y']])
        c = np.array([point3['x'], point3['y']])

        # Calculate vectors
        ba = a - b
        bc = c - b

        # Calculate angle
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

        return np.degrees(angle)

    def calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points

        Args:
            point1, point2: Keypoint dicts with x, y coordinates

        Returns:
            distance: Euclidean distance
        """
        x1, y1 = point1['x'], point1['y']
        x2, y2 = point2['x'], point2['y']

        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def get_body_angles(self, keypoints):
        """
        Calculate important body angles

        Args:
            keypoints: Dict of keypoints

        Returns:
            angles: Dict of calculated angles
        """
        if not keypoints:
            return None

        angles = {}

        try:
            # Left arm angle (shoulder-elbow-wrist)
            angles['left_elbow'] = self.calculate_angle(
                keypoints['left_shoulder'],
                keypoints['left_elbow'],
                keypoints['left_wrist']
            )

            # Right arm angle
            angles['right_elbow'] = self.calculate_angle(
                keypoints['right_shoulder'],
                keypoints['right_elbow'],
                keypoints['right_wrist']
            )

            # Left leg angle (hip-knee-ankle)
            angles['left_knee'] = self.calculate_angle(
                keypoints['left_hip'],
                keypoints['left_knee'],
                keypoints['left_ankle']
            )

            # Right leg angle
            angles['right_knee'] = self.calculate_angle(
                keypoints['right_hip'],
                keypoints['right_knee'],
                keypoints['right_ankle']
            )

            # Hip angle (shoulder-hip-knee)
            angles['left_hip'] = self.calculate_angle(
                keypoints['left_shoulder'],
                keypoints['left_hip'],
                keypoints['left_knee']
            )

            angles['right_hip'] = self.calculate_angle(
                keypoints['right_shoulder'],
                keypoints['right_hip'],
                keypoints['right_knee']
            )

            # Shoulder angle (hip-shoulder-elbow)
            angles['left_shoulder'] = self.calculate_angle(
                keypoints['left_hip'],
                keypoints['left_shoulder'],
                keypoints['left_elbow']
            )

            angles['right_shoulder'] = self.calculate_angle(
                keypoints['right_hip'],
                keypoints['right_shoulder'],
                keypoints['right_elbow']
            )

        except KeyError as e:
            print(f"Missing keypoint for angle calculation: {e}")
            return None

        return angles

    def close(self):
        """Release resources"""
        self.pose.close()