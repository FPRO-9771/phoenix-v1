## Setup for a clean computer (Mac)

### Install Pyenv

Check if it's already installed
```bash
  pyenv --version
```
If not:
```bash
  brew install pyenv
```
Confirm by checking pyenv --version. If that doesn't work you need to update the path.

### Navigate to your project directory

### Install and use Python 3.13
```bash
  pyenv install 3.13.0
```
```bash
  pyenv local 3.13.0
```

### Set up a virtual environment
Create it (note that you can change the ".venv" name)
```bash
  python3 -m venv .venv
```
Then activate it
```bash
  source .venv/bin/activate
```

### Verify Python version in your virtual environment

```bash
  python3 --version
```
Should return 3.13.0

### install required packages

```bash
    pip install wpilib robotpy phoenix6 robotpy\[commands2\] pynetworktables
```

---
## Setup for a clean computer (Windows)

## Install pyenv-win in PowerShell.

https://github.com/pyenv-win/pyenv-win

```bash
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Reopen PowerShell

Run to check if the installation was successful.

```bash
  pyenv --version
```

Run to check a list of Python versions supported by pyenv-win

```bash
  pyenv install -l
```

Run to install the supported version

```bash
  pyenv install 3.10
```

Run to set a Python version as the global version

```bash
  pyenv global 3.10
``` 

Check which Python version you are using and its path

```bash
  pyenv version
```

<version> (set by \path\to\.pyenv\pyenv-win\.python-version)
Check that Python is working

```bash
  python -c "import sys; print(sys.executable)"
```

\path\to\.pyenv\pyenv-win\versions\<version>\python.exe


# RoboRIO set up

## 2025 image required

We need to latest image RIO to be compatible with the latest Phoenix and robotpy
URL to download: https://github.com/wpilibsuite/2025Beta/releases/tag/NI_GAME_TOOLS_BETA_2

Funky - the software required a RIO version one earlier. So I found that here:
https://github.com/wpilibsuite/2025Beta/releases

## Install base software on the RIO
 python -m robotpy installer download-python        

Need to install the latest versions onto the RIO

```bash
 python -m robotpy installer install phoenix6== 25.0.0b3 
 ```
Maybe we need to install all the packages listed above


# BN Notes
- python v3.13.0
- delete all site-packages from .venv/Lib
- reinstall pip
- run pip script above
- robotpy sim runs

## now on rio
- run robotpy sync
- (this will run a long script to install stuff on rio)
- robotpy deploy fails becuase of some issues with tests
- but when i run "robotpy deploy --skip-tests" is seems to deploy

But... I get this error:

﻿﻿﻿﻿﻿﻿ Exception ignored on calling ctypes callback function <function SwerveDrivetrain.register_telemetry.<locals>.telem_callback at 0xb17676b8>: ﻿
﻿﻿﻿﻿﻿﻿ Traceback (most recent call last): ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/phoenix6/swerve/swerve_drivetrain.py", line 619, in telem_callback ﻿
﻿﻿﻿﻿﻿﻿     telemetry_function(self.__cached_state) ﻿
﻿﻿﻿﻿﻿﻿   File "/home/lvuser/py/telemetry.py", line 52, in telemeterize ﻿
﻿﻿﻿﻿﻿﻿     distance_diff = pose.translation().minus(self.last_pose.translation()) ﻿
﻿﻿﻿﻿﻿﻿ AttributeError: 'wpimath.geometry._geometry.Translation2d' object has no attribute 'minus' ﻿
﻿﻿﻿﻿﻿﻿ ﻿Warning﻿: Joystick Axis 4 missing (max 4), check if all controllers are plugged in ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/wpilib/_impl/start.py", line 247, in _start ﻿
﻿﻿﻿﻿﻿﻿     self.robot.startCompetition() ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/home/lvuser/py/robot.py", line 18, in robotPeriodic ﻿
﻿﻿﻿﻿﻿﻿     CommandScheduler.getInstance().run() ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/commands2/commandscheduler.py", line 301, in run ﻿
﻿﻿﻿﻿﻿﻿     self._schedule(scommand) ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/commands2/commandscheduler.py", line 212, in _schedule ﻿
﻿﻿﻿﻿﻿﻿     self._initCommand(command, *requirements) ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/commands2/commandscheduler.py", line 168, in _initCommand ﻿
﻿﻿﻿﻿﻿﻿     command.initialize() ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/commands2/functionalcommand.py", line 50, in initialize ﻿
﻿﻿﻿﻿﻿﻿     self._onInit() ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/home/lvuser/py/subsystems/command_swerve_drivetrain.py", line 33, in <lambda> ﻿
﻿﻿﻿﻿﻿﻿     return InstantCommand(lambda: self.set_control(request_supplier()), self) ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿   File "/home/lvuser/py/robot_container.py", line 54, in <lambda> ﻿
﻿﻿﻿﻿﻿﻿     .with_rotational_rate(-self.joystick.getRightX() * self.max_angular_rate) ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿  ﻿
﻿﻿﻿﻿﻿﻿ Exception ignored on calling ctypes callback function <function SwerveDrivetrain.register_telemetry.<locals>.telem_callback at 0xb17676b8>: ﻿
﻿﻿﻿﻿﻿﻿ Traceback (most recent call last): ﻿
﻿﻿﻿﻿﻿﻿   File "/usr/local/lib/python3.13/site-packages/phoenix6/swerve/swerve_drivetrain.py", line 619, in telem_callback ﻿
﻿﻿﻿﻿﻿﻿     telemetry_function(self.__cached_state) ﻿
﻿﻿﻿﻿﻿﻿   File "/home/lvuser/py/telemetry.py", line 52, in telemeterize ﻿
﻿﻿﻿﻿﻿﻿     distance_diff = pose.translation().minus(self.last_pose.translation()) ﻿
﻿﻿﻿﻿﻿﻿ AttributeError: 'wpimath.geometry._geometry.Translation2d' object has no attribute 'minus' ﻿
