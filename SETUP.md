# Quick Setup Guide 

## Step 1: Installation
```bash
mkdir task3_pose_estimation
cd task3_pose_estimation

# Install dependencies
pip install opencv-python mediapipe numpy scipy
```

## Step 2: Create Structure
```bash
# Create directories
mkdir -p models utils scripts

# Create __init__.py files
touch models/__init__.py
touch utils/__init__.py
```

## Step 3: Test Installation
```python
import mediapipe as mp
import cv2
print("MediaPipe version:", mp.__version__)
print("OpenCV version:", cv2.__version__)
```

## Step 4: Run Real-time Tracking

**For Squats:**
```bash
python scripts/realtime_pose.py --exercise squat
```

**For Push-ups:**
```bash
python scripts/realtime_pose.py --exercise pushup
```

**For Bicep Curls:**
```bash
python scripts/realtime_pose.py --exercise curl
```

**For Lunges:**
```bash
python scripts/realtime_pose.py --exercise lunge
```

## Step 5: Analyze Video
```bash
python scripts/analyze_video.py \
    --video my_workout.mp4 \
    --exercise squat \
    --output analyzed.mp4
```

## Camera Setup Tips
1. Position 6-8 feet away
2. Full body visible
3. Good lighting
4. Simple background
5. Face camera

## Controls
- **Q**: Quit and show summary
- Window shows:
  - Rep counter
  - Current stage
  - Form feedback
  - Joint angles
  - FPS

## Troubleshooting

**Camera not found:**
```bash
# Try different camera index
python scripts/realtime_pose.py --exercise squat --camera 1
```

**Low FPS:**
- Close other apps
- Lower camera resolution
- Use better lighting
- Reduce detection confidence:
```bash
python scripts/realtime_pose.py --exercise squat --detection_confidence 0.3
```

**Inaccurate counting:**
- Ensure full body visible
- Perform exercises slower
- Maintain proper form
- Check lighting

## Windows PowerShell Setup
```powershell
New-Item -ItemType Directory -Force -Path models,utils,scripts
New-Item -ItemType File -Force -Path models\__init__.py,utils\__init__.py
```

================================================================================
DIRECTORY STRUCTURE
================================================================================

task3_pose_estimation/
├── models/
│   ├── __init__.py
│   ├── pose_estimator.py       
│   └── exercise_classifier.py  
├── utils/
│   ├── __init__.py
│   ├── feedback_system.py      
│   └── visualization.py        
├── scripts/
│   ├── realtime_pose.py       
│   └── analyze_video.py        
├── requirements.txt
├── README.md
├── SETUP.md
└── .gitignore

================================================================================
FEATURES SUMMARY
================================================================================

 33 Body Keypoints Detection
   - Full body tracking with MediaPipe Pose
   - 3D coordinates (x, y, z)
   - Visibility scores

 Exercise Recognition
   - Squats (knee angle based)
   - Push-ups (elbow angle based)
   - Bicep Curls (elbow angle based)
   - Lunges (knee angle based)

 Automatic Rep Counting
   - State machine (up/down stages)
   - Angle smoothing
   - Threshold-based detection

 Real-time Form Feedback
   - Posture correction
   - Angle validation
   - Movement guidance
   - Visual and text feedback

 Angle Measurement
   - Joint angle calculations
   - Real-time display
   - Multi-joint analysis

 Session Statistics
   - Duration tracking
   - Reps per minute
   - Form warnings count
   - Performance metrics

 Webcam & Video Support
   - Live webcam tracking
   - Video file analysis
   - Output video generation


Console Output:
======================================================================
REAL-TIME POSE ESTIMATION - FITNESS APPLICATION
======================================================================
Exercise: SQUAT
Press Q to quit
======================================================================

✓ Camera opened successfully

 Starting exercise tracking...

[Rep counting in progress...]

======================================================================
SESSION SUMMARY
======================================================================
Duration: 3m 45s
Total Reps: 18
Average Reps/Min: 4.8
Form Warnings: 2
======================================================================

✓ Session complete!

On-Screen Display:
┌─────────────────────────────────────────┐
│ REPS: 18      STAGE: down               │
│                                         │
│ Keep back straight                      │
│ Go deeper for better results            │
│                                         │
│ Angle: 95°                     FPS: 28  │
│ Exercise: SQUAT                         │
└─────────────────────────────────────────┘