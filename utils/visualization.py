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
    print('VIDEO POSE ANALYSIS')
    print('='*70)
    print(f'Video: {args.video}')
    print(f'Exercise: {args.exercise.upper()}')
    print('='*70)

    # Initialize components
    pose_estimator = PoseEstimator()
    exercise_classifier = ExerciseClassifier()
    exercise_classifier.set_exercise(args.exercise)
    feedback_system = FeedbackSystem()
    feedback_system.start_session()
    visualizer = PoseVisualizer()

    # Open video
    cap = cv2.VideoCapture(args.video)

    if not cap.isOpened():
        print(f"Error: Could not open video {args.video}")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"\nVideo Properties:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Total Frames: {total_frames}")
    print(f"  Duration: {total_frames/fps:.2f} seconds")

    # Setup video writer
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        print(f"\nOutput will be saved to: {args.output}")

    print("\n🏋️ Analyzing video...\n")

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Detect pose
        results, _ = pose_estimator.detect_pose(frame)
        annotated_frame = pose_estimator.draw_landmarks(frame, results)

        # Extract and analyze
        keypoints = pose_estimator.extract_keypoints(results, frame.shape)

        if keypoints:
            angles = pose_estimator.get_body_angles(keypoints)

            if angles:
                classification = exercise_classifier.classify(angles)

                if classification:
                    counter = classification['counter']
                    stage = classification['stage']
                    feedback = feedback_system.get_feedback(
                        args.exercise, keypoints, angles
                    )

                    # Visualize
                    visualizer.draw_counter(annotated_frame, counter, stage)
                    visualizer.draw_feedback(annotated_frame, feedback)
                    visualizer.draw_exercise_info(annotated_frame, args.exercise)

        # Write frame
        if args.output:
            out.write(annotated_frame)

        # Show progress
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})", end='\r')

    # Cleanup
    cap.release()
    if args.output:
        out.release()
    pose_estimator.close()

    print("\n\n" + '='*70)
    print('ANALYSIS COMPLETE')
    print('='*70)

    summary = feedback_system.get_session_summary()
    if summary:
        print(f"Total Reps: {summary['total_reps']}")
        print(f"Duration: {summary['duration_formatted']}")

    if args.output:
        print(f"\n✓ Output saved to: {args.output}")

    print('='*70)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze video for pose estimation')
    parser.add_argument('--video', type=str, required=True, help='Input video path')
    parser.add_argument('--exercise', type=str, required=True,
                       choices=['squat', 'pushup', 'curl', 'lunge'],
                       help='Exercise type')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video path (optional)')

    args = parser.parse_args()
    main(args)
