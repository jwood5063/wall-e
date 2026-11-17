# Wall-E — ROS 2 Navigation Simulation Prototype

_The instructions we worked through on Oct 26–28, 2026 to simulate robot movement
before the chassis existed: ROS 2 Jazzy in Docker on the Ubuntu laptop, TurtleBot3
Gazebo sim, Nav2 waypoint driving. Recovered from the session record so the whole
sequence is in one place._

_Purpose: debug the nav stack (SLAM, waypoints, obstacle avoidance) in simulation
before any hardware arrived. The chassis has since landed, but this remains the
fast way to test Nav2 behaviour without risking the robot._

## 1. Docker on the laptop

Skip if `docker --version` already works.

```bash
sudo apt update && sudo apt install -y docker.io
sudo usermod -aG docker $USER
```

Log out and back in so the group applies.

## 2. Start the ROS 2 Jazzy container with a GUI

```bash
xhost +local:docker
docker run -it --name ros2-jazzy --net=host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  osrf/ros:jazzy-desktop-full bash
```

Notes from the session:
- The image pull is several GB — that's the slow part.
- `--net=host` keeps ROS 2 discovery painless.
- No `--rm`, so the container survives; restart it later with
  `docker start -ai ros2-jazzy`.

## 3. Inside the container: install TurtleBot3 + Nav2

```bash
apt update
apt install -y ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-msgs \
  ros-jazzy-turtlebot3-gazebo ros-jazzy-navigation2 ros-jazzy-nav2-bringup
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle
```

## 4. Launch sim + navigation

```bash
ros2 launch nav2_bringup tb3_simulation_launch.py
```

Gazebo opens with a TurtleBot3 (waffle) in a small walled world; RViz opens with
the Nav2 map of that world already loaded. First launch takes a minute while
models load. **The robot spawns at x = −2.0, y = −0.5, facing +x** — that pose
matters in step 6.

## 5. If the GUI doesn't start ($DISPLAY)

The GUI apps inherit `$DISPLAY` from the shell that started them, so it has to be
right on the laptop *before* the container and sim launch.

1. On the laptop, in a terminal opened from the desktop (not SSH/tmux):
   ```bash
   echo $DISPLAY
   ```
   Should print `:0`. Blank means that shell isn't part of the desktop session.
2. Let the container talk to the X server:
   ```bash
   xhost +local:docker
   ```
3. Get a container shell with DISPLAY set (the existing container already has
   the X11 socket mounted — no need to recreate it):
   ```bash
   docker exec -e DISPLAY=:0 -it ros2-jazzy bash
   ```
4. Test before relaunching anything:
   ```bash
   apt install -y x11-apps && xeyes
   ```
   Eyes on screen = display path works. Ctrl-C to kill.
5. Relaunch the sim from *that* shell (step 4 above) so Gazebo/RViz inherit it.

Wayland note: Ubuntu 24's default session is Wayland; RViz and Gazebo still work
as X11 apps through XWayland. If `xeyes` works but the sim windows come up black,
log out and pick "Ubuntu on Xorg" from the gear on the login screen.
`xhost -local:docker` revokes display access when done.

## 6. The failure we hit — and the fix

**What happened (Oct 26):** global costmap failed to activate — "transform from
base_link to map did not become available before timeout" — planner_server
failed, lifecycle manager aborted bringup, and AMCL kept warning "Please set the
initial pose..."

**Root cause:** one thing, not three. AMCL never got an initial pose, so it never
published the map→odom transform; without it the costmap couldn't activate,
which killed the planner and aborted the whole Nav2 bringup.

### Shell-only fix (no RViz toolbar)

1. Publish the initial pose — the **spawn pose**, not the origin:
   ```bash
   source /opt/ros/jazzy/setup.bash
   ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
     "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}"
   ```
   The AMCL warnings should stop.
2. Confirm the transform exists:
   ```bash
   ros2 run tf2_ros tf2_echo map base_link
   ```
   Streaming translations = chain fixed. Ctrl-C it.
3. Restart the aborted navigation lifecycle:
   ```bash
   ros2 service call /lifecycle_manager_navigation/manage_nodes \
     nav2_msgs/srv/ManageLifecycleNodes "{command: 0}"
   ```
4. Send the waypoint:
   ```bash
   ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
     "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}" --feedback
   ```

GUI equivalent, for reference: **2D Pose Estimate** in RViz is just a publisher
to `/initialpose`; **Nav2 Goal** sends the same action as step 4.

## 7. Relaunch loop — the robust version (use this one)

The one-shot `/initialpose` publish can get lost if AMCL isn't subscribed yet,
and the costmap times out the same way. This version republishes until AMCL
confirms. Paste-ready for any relaunch:

1. Launch the sim (step 4).
2. In a second shell in the container:
   ```bash
   for i in $(seq 1 15); do
     ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}"
     if timeout 5 ros2 topic echo /amcl_pose --once > /dev/null 2>&1; then echo "AMCL pose OK"; break; fi
     sleep 2
   done
   ```
3. Only if bringup already aborted, restart the lifecycle (step 6.3 command).
4. Waypoint to (0, 0):
   ```bash
   ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 0.0, y: 0.0}, orientation: {w: 1.0}}}}"
   ```

## 8. Diagnostics if it still misbehaves

- `/amcl_pose` never appears after all 15 publishes: note what
  `ros2 topic echo /amcl_pose --once` does (hangs vs errors) and the output of
  `ros2 run tf2_ros tf2_echo map base_link` — those two pin it down.
- AMCL gets a pose but localization looks wrong: first suspect is the spawn
  coordinates (−2.0, −0.5), not the loop.
- Lifecycle restart errors instead of activating: Ctrl-C and relaunch, then set
  the initial pose immediately — the failure only happens when the costmap's
  transform wait times out before AMCL gets its pose.

## Status note

**Confirmed working (Jim, 2026-11-16):** the simulation ran correctly after the
initial-pose fix — AMCL localized, Nav2 came up, and the robot drove to its
waypoint. The sequence above is a proven run, not just instructions.
