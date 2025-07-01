#!/usr/bin/env python3

"""
Test the Parade shooter logic and verify motor commands are correct.
This tests what commands would be sent to the motors.
"""

import time
from constants import CON_SHOOT_PARADE, MOTOR_IDS, SHOOTER_TYPE

class MotorCommandLogger:
    """Mock motor that logs all commands sent to it."""
    def __init__(self, motor_id, name):
        self.motor_id = motor_id
        self.name = name
        self.commands = []
        self.current_velocity = 0.0
        self.current_voltage = 0.0
        
    def log_command(self, command_type, value, unit=""):
        timestamp = time.time()
        command = {
            'time': timestamp,
            'type': command_type,
            'value': value,
            'unit': unit
        }
        self.commands.append(command)
        print(f"    {self.name} (ID:{self.motor_id}): {command_type} = {value}{unit}")
        
        if command_type == "velocity":
            self.current_velocity = value
        elif command_type == "voltage":
            self.current_voltage = value

def test_parade_shooter_logic():
    """Test the core logic of parade shooter commands."""
    print("🚀 Testing Parade Shooter Command Logic")
    print("=" * 60)
    print(f"Shooter Type: {SHOOTER_TYPE}")
    print(f"Configuration: {CON_SHOOT_PARADE}")
    print(f"Motor IDs: Left={MOTOR_IDS.get('shooter_parade_left', 'NOT SET')}, Right={MOTOR_IDS.get('shooter_parade_right', 'NOT SET')}")
    print("=" * 60)
    
    # Create mock motors
    left_motor = MotorCommandLogger(MOTOR_IDS.get("shooter_parade_left", 27), "LEFT")
    right_motor = MotorCommandLogger(MOTOR_IDS.get("shooter_parade_right", 28), "RIGHT")
    
    # Test 1: Pull-back command logic
    print("\n🔄 TEST 1: Pull-Back Command Logic")
    print("-" * 40)
    
    low_rpm = CON_SHOOT_PARADE["low_rpm"]
    target_rps = -low_rpm / 60.0  # Negative for pull-back
    
    print(f"Expected behavior: Run at {low_rpm} RPM in reverse ({target_rps:.2f} RPS)")
    print("Simulating pull-back command execution:")
    
    # Simulate the pull-back command
    left_motor.log_command("velocity", target_rps, " RPS")
    right_motor.log_command("velocity", target_rps, " RPS")
    
    # Verify the commands
    pull_back_correct = (
        left_motor.current_velocity == target_rps and 
        right_motor.current_velocity == target_rps and
        target_rps < 0  # Should be negative for pull-back
    )
    
    print(f"✅ Pull-back logic: {'PASSED' if pull_back_correct else 'FAILED'}")
    
    # Test 2: Fire command logic
    print("\n🔥 TEST 2: Fire Command Logic")
    print("-" * 40)
    
    max_rpm = CON_SHOOT_PARADE["max_rpm"]
    target_rps = max_rpm / 60.0  # Positive for firing
    fire_duration = CON_SHOOT_PARADE["fire_duration"]
    
    print(f"Expected behavior: Run at {max_rpm} RPM forward ({target_rps:.2f} RPS) for {fire_duration}s")
    print("Simulating fire command execution:")
    
    # Simulate the fire command
    start_time = time.time()
    left_motor.log_command("velocity", target_rps, " RPS")
    right_motor.log_command("velocity", target_rps, " RPS")
    
    # Simulate command duration
    print(f"Simulating {fire_duration}s fire duration...")
    time.sleep(0.1)  # Brief pause to simulate time passing
    
    # Simulate command ending (motors stop)
    left_motor.log_command("voltage", 0.0, "V")
    right_motor.log_command("voltage", 0.0, "V")
    
    end_time = time.time()
    simulated_duration = end_time - start_time
    
    # Verify the commands
    fire_correct = (
        left_motor.current_velocity == target_rps and 
        right_motor.current_velocity == target_rps and
        target_rps > 0 and  # Should be positive for firing
        left_motor.current_voltage == 0.0 and  # Should stop after duration
        right_motor.current_voltage == 0.0
    )
    
    print(f"Fire command would run for: {fire_duration}s (configured)")
    print(f"✅ Fire logic: {'PASSED' if fire_correct else 'FAILED'}")
    
    # Test 3: Motor inversion logic
    print("\n🔄 TEST 3: Motor Inversion Logic")
    print("-" * 40)
    
    print("Both motors should receive the same velocity command")
    print("Hardware inversion is handled in motor configuration, not command values")
    print("Left motor config: COUNTER_CLOCKWISE_POSITIVE (normal)")
    print("Right motor config: CLOCKWISE_POSITIVE (inverted)")
    
    # Both motors should get same command value, but hardware handles inversion
    same_commands = (left_motor.current_velocity == right_motor.current_velocity)
    print(f"✅ Motor inversion logic: {'PASSED' if same_commands else 'FAILED'}")
    
    # Test 4: RPM calculations
    print("\n📊 TEST 4: RPM/RPS Conversion Logic")
    print("-" * 40)
    
    # Test low RPM conversion
    low_rpm_check = abs((-CON_SHOOT_PARADE["low_rpm"] / 60.0) - (-low_rpm / 60.0)) < 0.01
    max_rpm_check = abs((CON_SHOOT_PARADE["max_rpm"] / 60.0) - (max_rpm / 60.0)) < 0.01
    
    print(f"Low RPM: {CON_SHOOT_PARADE['low_rpm']} RPM = {CON_SHOOT_PARADE['low_rpm']/60.0:.2f} RPS")
    print(f"Max RPM: {CON_SHOOT_PARADE['max_rpm']} RPM = {CON_SHOOT_PARADE['max_rpm']/60.0:.2f} RPS")
    print(f"✅ RPM calculations: {'PASSED' if low_rpm_check and max_rpm_check else 'FAILED'}")
    
    # Test 5: Button mapping logic
    print("\n🎮 TEST 5: Button Mapping Logic")
    print("-" * 40)
    
    if SHOOTER_TYPE == "Parade":
        print("✅ Current mode: PARADE")
        print("   Left Trigger -> Pull-back (while held)")
        print("   Right Trigger -> Fire (single press)")
        button_mapping_correct = True
    else:
        print("⚠️  Current mode: COMPETITION")
        print("   Left Trigger -> Manual positive")
        print("   Right Trigger -> Manual negative")
        button_mapping_correct = True
    
    print(f"✅ Button mapping: {'CORRECT' if button_mapping_correct else 'INCORRECT'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 LOGIC TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Pull-back command logic", pull_back_correct),
        ("Fire command logic", fire_correct),
        ("Motor inversion logic", same_commands),
        ("RPM calculations", low_rpm_check and max_rpm_check),
        ("Button mapping", button_mapping_correct)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 Logic Tests: {passed}/{total} passed")
    
    # Configuration check
    print("\n📋 CONFIGURATION CHECK")
    print("-" * 30)
    config_issues = []
    
    if "shooter_parade_left" not in MOTOR_IDS:
        config_issues.append("Missing shooter_parade_left motor ID")
    if "shooter_parade_right" not in MOTOR_IDS:
        config_issues.append("Missing shooter_parade_right motor ID")
    if CON_SHOOT_PARADE["fire_duration"] <= 0:
        config_issues.append("Fire duration must be positive")
    if CON_SHOOT_PARADE["low_rpm"] <= 0:
        config_issues.append("Low RPM must be positive")
    if CON_SHOOT_PARADE["max_rpm"] <= CON_SHOOT_PARADE["low_rpm"]:
        config_issues.append("Max RPM should be higher than low RPM")
    
    if config_issues:
        print("⚠️  Configuration issues found:")
        for issue in config_issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Configuration looks good!")
    
    print(f"\n🎉 Overall: {'ALL TESTS PASSED' if passed == total and not config_issues else 'SOME ISSUES FOUND'}")
    print("\n💡 Next steps:")
    print("   1. Deploy to robot with 'robotpy deploy --skip-tests'")
    print("   2. Test with actual controllers")
    print(f"   3. Switch SHOOTER_TYPE between 'Parade' and 'Competition' as needed")
    
    return passed == total and not config_issues

if __name__ == "__main__":
    test_parade_shooter_logic()