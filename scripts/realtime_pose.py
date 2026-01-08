import sys
sys.path.append('.')

import cv2
import time
import argparse
from models.pose_estimator import PoseEstimator
from models.exercise_classifier import ExerciseClassifier
from utils.feedback_system import FeedbackSystem
from utils.visualization import PoseVisualizer

def main(args):
    print('='*70)
    print('REAL-TIME POSE ESTIMATION - FITNESS APPLICATION')
    print('='*70)
    print(f'Exercise: {args.exercise.upper()}')
    print('Press Q to quit')
    print('='*70)

    # Initialize components
    pose_estimator = PoseEstimator(
        min_detection_confidence=args.detection_confidence,
        min_tracking_confidence=args.tracking_confidence
    )

    exercise_classifier = ExerciseClassifier()
    exercise_classifier.set_exercise(args.exercise)

    feedback_system = FeedbackSystem()
    feedback_system.start_session()

    visualizer = PoseVisualizer()

    # Open webcam
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    print("\n✓ Camera opened successfully")
    print("\n🏋️ Starting exercise tracking...\n")

    # FPS calculation
    prev_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time > 0 else 0
        prev_time = curr_time

        # Detect pose
        results, image_rgb = pose_estimator.detect_pose(frame)

        # Draw landmarks
        annotated_frame = pose_estimator.draw_landmarks(frame, results)

        # Extract keypoints
        keypoints = pose_estimator.extract_keypoints(results, frame.shape)

        if keypoints:
            # Calculate angles
            angles = pose_estimator.get_body_angles(keypoints)

            if angles:
                # Classify exercise
                classification = exercise_classifier.classify(angles)

                if classification:
                    counter = classification['counter']
                    stage = classification['stage']
                    angle = classification['angle']

                    # Get feedback
                    feedback = feedback_system.get_feedback(
                        args.exercise, keypoints, angles
                    )

                    # Log rep if counter increased
                    if counter > feedback_system.session_data['total_reps']:
                        feedback_system.log_rep(counter, angles)

                    # Visualize
                    visualizer.draw_counter(annotated_frame, counter, stage)
                    visualizer.draw_feedback(annotated_frame, feedback)
                    visualizer.draw_exercise_info(annotated_frame, args.exercise, fps)

                    # Draw key angle
                    visualizer.draw_angle(
                        annotated_frame,
                        "Angle",
                        (10, annotated_frame.shape[0] - 30),
                        angle
                    )

        # Display
        cv2.imshow('Fitness Pose Estimation', annotated_frame)

        # Quit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pose_estimator.close()

    # Show session summary
    print('\n' + '='*70)
    print('SESSION SUMMARY')
    print('='*70)
    summary = feedback_system.get_session_summary()
    if summary:
        print(f"Duration: {summary['duration_formatted']}")
        print(f"Total Reps: {summary['total_reps']}")
        print(f"Average Reps/Min: {summary['avg_reps_per_minute']:.1f}")
        print(f"Form Warnings: {summary['form_warnings_count']}")
    print('='*70)
    print('\n✓ Session complete!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Real-time Pose Estimation for Fitness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Track squats
  python scripts/realtime_pose.py --exercise squat

  # Track push-ups
  python scripts/realtime_pose.py --exercise pushup

  # Track bicep curls
  python scripts/realtime_pose.py --exercise curl

  # Track lunges
  python scripts/realtime_pose.py --exercise lunge

  # Use specific camera
  python scripts/realtime_pose.py --exercise squat --camera 1
        '''
    )

    parser.add_argument('--exercise', type=str, required=True,
                       choices=['squat', 'pushup', 'curl', 'lunge'],
                       help='Exercise type to track')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--detection_confidence', type=float, default=0.5,
                       help='Minimum detection confidence (0-1)')
    parser.add_argument('--tracking_confidence', type=float, default=0.5,
                       help='Minimum tracking confidence (0-1)')

    args = parser.parse_args()
    main(args)
