"""
Universal Simulation Testing Framework for Ruby Robot

This module provides a unified interface for testing robot subsystems using 
WPILib and Phoenix 6 simulation features. It enables real physics-based testing
rather than just mocking.

Key Features:
- Real motor simulation with Phoenix 6 TalonFXSimState
- Physics-based mechanism simulation using WPILib
- Command testing with actual feedback loops
- Performance monitoring and validation
- Easy integration with existing robot code

Usage:
    from testing.sim_framework import SimTestFramework
    
    # Create test framework
    test_framework = SimTestFramework()
    
    # Test a subsystem
    results = test_framework.test_subsystem(my_subsystem, test_scenarios)
"""

import time
import math
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field

import wpilib
from wpilib import RobotController
from wpilib.simulation import DriverStationSim
from commands2 import CommandScheduler, Command
from phoenix6.hardware import TalonFX
from phoenix6 import utils


@dataclass
class SimTestResult:
    """Results from a simulation test."""
    test_name: str
    passed: bool
    duration: float
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class MotorTestData:
    """Data captured from a motor during testing."""
    timestamps: List[float] = field(default_factory=list)
    voltages: List[float] = field(default_factory=list)
    velocities: List[float] = field(default_factory=list)
    positions: List[float] = field(default_factory=list)
    currents: List[float] = field(default_factory=list)


class SimMotorMonitor:
    """Monitor and capture data from a TalonFX motor in simulation."""
    
    def __init__(self, motor: TalonFX, name: str):
        self.motor = motor
        self.name = name
        self.sim_state = motor.sim_state
        self.data = MotorTestData()
        self.start_time = None
        self.sim_setup_func = None
        
        # Set up simulation with default behavior
        self._setup_basic_simulation()
        
    def _setup_basic_simulation(self):
        """Set up basic simulation for the motor."""
        # Set supply voltage for simulation
        self.sim_state.set_supply_voltage(12.0)
        print(f"🔧 Motor {self.name} simulation initialized")
        
    def set_simulation_setup(self, setup_func: Callable[[TalonFX], None]):
        """Set a custom simulation setup function for this motor."""
        self.sim_setup_func = setup_func
        if setup_func:
            setup_func(self.motor)
        
    def start_monitoring(self):
        """Start capturing motor data."""
        self.start_time = time.time()
        self.data = MotorTestData()
        
    def update(self):
        """Capture current motor state."""
        if self.start_time is None:
            return
            
        current_time = time.time() - self.start_time
        
        # Get motor data using correct Phoenix 6 API
        voltage = self.sim_state.motor_voltage
        velocity = self.motor.get_velocity().value  # RPS from actual motor, not sim_state
        position = self.motor.get_position().value  # rotations from actual motor
        current = self.sim_state.supply_current
        
        # Store data
        self.data.timestamps.append(current_time)
        self.data.voltages.append(voltage)
        self.data.velocities.append(velocity)
        self.data.positions.append(position)
        self.data.currents.append(current)
        
    def stop_monitoring(self):
        """Stop capturing data."""
        self.start_time = None
        
    def get_peak_velocity_rpm(self) -> float:
        """Get peak velocity in RPM."""
        if not self.data.velocities:
            return 0.0
        return max(abs(v) for v in self.data.velocities) * 60.0
        
    def get_final_velocity_rpm(self) -> float:
        """Get final velocity in RPM."""
        if not self.data.velocities:
            return 0.0
        return self.data.velocities[-1] * 60.0
        
    def get_peak_voltage(self) -> float:
        """Get peak voltage magnitude."""
        if not self.data.voltages:
            return 0.0
        return max(abs(v) for v in self.data.voltages)


class SimTestFramework:
    """Universal framework for testing robot subsystems in simulation."""
    
    def __init__(self):
        self.motor_monitors: Dict[str, SimMotorMonitor] = {}
        self.test_results: List[SimTestResult] = []
        self.is_simulation_enabled = False
        
    def setup_simulation(self):
        """Initialize simulation environment."""
        print("🔧 Setting up simulation environment...")
        
        # Check if we're in simulation mode
        if not utils.is_simulation():
            print("⚠️  Warning: Not in simulation mode!")
            print("   Run with: robotpy sim")
            return False
            
        # Enable robot in test mode
        DriverStationSim.setEnabled(True)
        DriverStationSim.setTest(True)
        
        # Note: Battery voltage is set automatically in simulation
        
        self.is_simulation_enabled = True
        print("✅ Simulation environment ready")
        return True
        
    def register_motor(self, motor: TalonFX, name: str, sim_setup_func: Callable[[TalonFX], None] = None) -> SimMotorMonitor:
        """Register a motor for monitoring during tests with optional simulation setup.
        
        Args:
            motor: The TalonFX motor to monitor
            name: Name for this motor in test results
            sim_setup_func: Optional function to set up custom simulation behavior
        """
        monitor = SimMotorMonitor(motor, name)
        if sim_setup_func:
            monitor.set_simulation_setup(sim_setup_func)
        self.motor_monitors[name] = monitor
        print(f"📊 Registered motor '{name}' for monitoring")
        return monitor
        
    def _update_motor_simulation(self):
        """Update simulation state for all registered motors."""
        battery_voltage = RobotController.getBatteryVoltage()
        
        for monitor in self.motor_monitors.values():
            # Update supply voltage from robot battery
            monitor.sim_state.set_supply_voltage(battery_voltage)
            
            # Run custom simulation update if provided
            if monitor.sim_setup_func:
                monitor.sim_setup_func(monitor.motor)
        
    def run_command_test(self, 
                        command: Command, 
                        test_name: str,
                        expected_duration: float = None,
                        timeout: float = 10.0,
                        validation_func: Callable[[Dict[str, SimMotorMonitor]], bool] = None) -> SimTestResult:
        """
        Run a command and monitor motor behavior.
        
        Args:
            command: Command to test
            test_name: Name for this test
            expected_duration: Expected command duration (for validation)
            timeout: Maximum time to wait for command completion
            validation_func: Function to validate motor behavior
            
        Returns:
            SimTestResult with test outcome and data
        """
        print(f"\n🧪 Running test: {test_name}")
        
        result = SimTestResult(test_name=test_name, passed=False, duration=0.0)
        
        try:
            # Start monitoring all motors
            for monitor in self.motor_monitors.values():
                monitor.start_monitoring()
                
            # Schedule the command
            CommandScheduler.getInstance().schedule(command)
            start_time = time.time()
            
            # Run until command finishes or timeout
            print(f"   ⏳ Running command (timeout: {timeout}s)...")
            while not command.isFinished() and (time.time() - start_time) < timeout:
                # Update simulation
                CommandScheduler.getInstance().run()
                
                # Update motor monitors
                for monitor in self.motor_monitors.values():
                    monitor.update()
                    
                # Update simulation state for all motors
                self._update_motor_simulation()
                    
                time.sleep(0.02)  # 50Hz update rate
                
            end_time = time.time()
            result.duration = end_time - start_time
            
            # Stop monitoring
            for monitor in self.motor_monitors.values():
                monitor.stop_monitoring()
                
            # Check if command completed
            if command.isFinished():
                print(f"   ✅ Command completed in {result.duration:.3f}s")
            else:
                print(f"   ⏰ Command timed out after {result.duration:.3f}s")
                result.errors.append("Command timed out")
                
            # Validate expected duration
            if expected_duration is not None:
                duration_error = abs(result.duration - expected_duration)
                if duration_error > 0.1:  # 100ms tolerance
                    result.warnings.append(
                        f"Duration mismatch: expected {expected_duration:.3f}s, got {result.duration:.3f}s"
                    )
                    
            # Run custom validation
            if validation_func:
                try:
                    validation_passed = validation_func(self.motor_monitors)
                    if not validation_passed:
                        result.errors.append("Custom validation failed")
                except Exception as e:
                    result.errors.append(f"Validation error: {e}")
                    
            # Collect motor data
            result.data = {
                'motor_data': {name: {
                    'peak_velocity_rpm': monitor.get_peak_velocity_rpm(),
                    'final_velocity_rpm': monitor.get_final_velocity_rpm(),
                    'peak_voltage': monitor.get_peak_voltage(),
                    'data_points': len(monitor.data.timestamps)
                } for name, monitor in self.motor_monitors.items()}
            }
            
            # Determine if test passed
            result.passed = len(result.errors) == 0 and command.isFinished()
            
            # Print results
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"   {status}")
            
            if result.errors:
                for error in result.errors:
                    print(f"     ❌ {error}")
                    
            if result.warnings:
                for warning in result.warnings:
                    print(f"     ⚠️  {warning}")
                    
        except Exception as e:
            result.errors.append(f"Test exception: {e}")
            print(f"   ❌ Test failed with exception: {e}")
            
        finally:
            # Clean up
            CommandScheduler.getInstance().cancelAll()
            
        self.test_results.append(result)
        return result
        
    def validate_velocity_range(self, 
                               motor_name: str, 
                               expected_rpm: float, 
                               tolerance_percent: float = 20.0) -> bool:
        """Validate that a motor reached expected velocity."""
        if motor_name not in self.motor_monitors:
            return False
            
        monitor = self.motor_monitors[motor_name]
        peak_rpm = monitor.get_peak_velocity_rpm()
        expected_abs = abs(expected_rpm)
        tolerance = expected_abs * (tolerance_percent / 100.0)
        
        return abs(peak_rpm - expected_abs) <= tolerance
        
    def validate_motor_direction(self, 
                                motor_name: str, 
                                expected_positive: bool) -> bool:
        """Validate motor direction."""
        if motor_name not in self.motor_monitors:
            return False
            
        monitor = self.motor_monitors[motor_name]
        if not monitor.data.velocities:
            return False
            
        # Check the average velocity direction
        avg_velocity = sum(monitor.data.velocities) / len(monitor.data.velocities)
        
        if expected_positive:
            return avg_velocity > 0
        else:
            return avg_velocity < 0
            
    def print_test_summary(self):
        """Print a summary of all test results."""
        print("\n" + "=" * 60)
        print("📋 SIMULATION TEST SUMMARY")
        print("=" * 60)
        
        if not self.test_results:
            print("   No tests run")
            return
            
        passed = sum(1 for result in self.test_results if result.passed)
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"   {result.test_name}: {status} ({result.duration:.3f}s)")
            
            # Print motor data summary
            if 'motor_data' in result.data:
                for motor_name, data in result.data['motor_data'].items():
                    print(f"     {motor_name}: {data['peak_velocity_rpm']:.0f} RPM peak, "
                          f"{data['peak_voltage']:.1f}V peak")
                          
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All simulation tests passed!")
        else:
            print("⚠️  Some tests failed - check implementation")
            
    def cleanup(self):
        """Clean up simulation resources."""
        CommandScheduler.getInstance().cancelAll()
        self.motor_monitors.clear()
        print("🧹 Simulation cleanup complete")


# Utility functions for common test scenarios

def create_velocity_validator(expected_rpms: Dict[str, float], 
                            tolerance_percent: float = 20.0) -> Callable:
    """Create a validation function for motor velocities."""
    def validator(monitors: Dict[str, SimMotorMonitor]) -> bool:
        for motor_name, expected_rpm in expected_rpms.items():
            if motor_name not in monitors:
                return False
                
            monitor = monitors[motor_name]
            peak_rpm = monitor.get_peak_velocity_rpm()
            expected_abs = abs(expected_rpm)
            tolerance = expected_abs * (tolerance_percent / 100.0)
            
            if abs(peak_rpm - expected_abs) > tolerance:
                print(f"     Velocity validation failed for {motor_name}: "
                      f"expected {expected_abs:.0f} RPM, got {peak_rpm:.0f} RPM")
                return False
                
        return True
    return validator


def create_direction_validator(expected_directions: Dict[str, bool]) -> Callable:
    """Create a validation function for motor directions."""
    def validator(monitors: Dict[str, SimMotorMonitor]) -> bool:
        for motor_name, expected_positive in expected_directions.items():
            if motor_name not in monitors:
                return False
                
            monitor = monitors[motor_name]
            if not monitor.data.velocities:
                return False
                
            avg_velocity = sum(monitor.data.velocities) / len(monitor.data.velocities)
            actual_positive = avg_velocity > 0
            
            if actual_positive != expected_positive:
                direction = "positive" if expected_positive else "negative"
                actual_dir = "positive" if actual_positive else "negative"
                print(f"     Direction validation failed for {motor_name}: "
                      f"expected {direction}, got {actual_dir}")
                return False
                
        return True
    return validator