#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTables as NT
import wpiJoystickOverlay as joy
import isClose as ic
from wpilib.drive import DifferentialDrive
import autoPositions as ap
import ctre

#Notes for robot installation
#Make sure new robotpy, cscore, and robotpy-ctre are all installed
	
class MyRobot(wp.IterativeRobot):
	def robotInit(self):
		'''Robot initialization function'''
		self.leftMotor1 = ctre.WPI_VictorSPX(1) #motor initialization
		self.leftMotor2 = ctre.WPI_VictorSPX(3)
		self.leftMotor3 = ctre.WPI_VictorSPX(5)
		self.rightMotor1 = ctre.WPI_VictorSPX(0)
		self.rightMotor2 = ctre.WPI_VictorSPX(2)
		self.rightMotor3 = ctre.WPI_VictorSPX(4)
		self.armMotor = ctre.WPI_VictorSPX(6)
		self.leftIntakeMotor = ctre.WPI_VictorSPX(7)
		self.rightIntakeMotor = ctre.WPI_VictorSPX(8)
		
		self.leftSide = wp.SpeedControllerGroup(self.leftMotor1, self.leftMotor2, self.leftMotor3) #speed controller groups
		self.rightSide = wp.SpeedControllerGroup(self.rightMotor1, self.rightMotor2, self.rightMotor3)
		self.intakeMotors = wp.SpeedControllerGroup(self.leftIntakeMotor, self.rightIntakeMotor)
		
		self.myRobot = DifferentialDrive(self.leftSide, self.rightSide)
		self.myRobot.setExpiration(0.1)
		
		self.leftStick = wp.Joystick(0)
		self.rightStick = wp.Joystick(1)
		self.armStick = wp.Joystick(2)
		
		self.gyro = wp.ADXRS450_Gyro(0)
		self.rightEncd = wp.Encoder(0,1)
		self.leftEncd = wp.Encoder(2,3)
		
		self.compressor = wp.Compressor()
		
		wp.SmartDashboard.putNumber("Straight Position", 4000)
		self.chooser = wp.SendableChooser()
		self.chooser.addDefault("None", 4)
		self.chooser.addObject("Straight/Enc", 1)
		self.chooser.addObject("Left Turn Auto", 2)
		self.chooser.addObject("Right Turn Auto", 3)
		self.chooser.addObject("Straight/Timer", 5)
		wp.SmartDashboard.putData("Choice", self.chooser)
		wp.CameraServer.launch("vision.py:main")
	
	def robotPeriodic(self):
		wp.SmartDashboard.putNumber("Gyro:",round(self.gyro.getAngle(), 2))
		wp.SmartDashboard.putNumber("Right Encoder:",self.rightEncd.get())
		wp.SmartDashboard.putNumber("Left Encoder:",self.leftEncd.get())
		
		calGyro = wp.SmartDashboard.getBoolean("calGyro:", True)
		resetGyro = wp.SmartDashboard.getBoolean("resetGyro:", True)
		encodeReset = wp.SmartDashboard.getBoolean("resetEnc:", True)
		
		if(resetGyro):
			self.gyro.reset()
			wp.SmartDashboard.putBoolean("resetGyro:", False)
			
		if(calGyro):
			self.gyro.calibrate()
			wp.SmartDashboard.putBoolean("calGyro:", False)
			
		if(encodeReset):
			self.rightEncd.reset()
			self.leftEncd.reset()
			wp.SmartDashboard.putBoolean("resetEnc:", False)
		self.auto = self.chooser
	
	def autonomousInit(self):
		self.auto = self.chooser
		self.leftMotorVal = 0
		self.rightMotorVal = 0
		self.gyroFuncGain = 40
		self.leftMotVal = 0
		self.rightMotVal = 0
		
	def autonomousPeriodic(self):
		#autonomous code will go here
		if(self.auto == 1):
			if(self.rightEncd <= ap.moveStraightPos):
				self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, -0.65, self.gyroFuncGain)
			else:
				self.leftMotVal, self.rightMotVal = 0, 0
		
		self.myRobot.tankDrive(self.leftMotVal, self.rightMotVal)
		
		
		
	def teleopInit(self):
		#telop init here
		self.myRobot.setSafetyEnabled(True)
		self.pastFrontFlipButton = False
		self.flip = True
		
	def teleopPeriodic(self):
		#teleop code will go here
		#Joystick Variables
		leftJoyValY = self.leftStick.getY()
		rightJoyValY = self.rightStick.getY()
		armJoyValY = self.armStick.getY()
		frontFlipButton = self.rightStick.getRawButton(2)
		
		#FrontFlip
		if(self.pastFrontFlipButton == False and frontFlipButton):
			self.flip = not self.flip
		self.pastFrontFlipButton = frontFlipButton
		
		leftMotVal, rightMotVal = rf.flip(self.flip, leftJoyValY, rightJoyValY)
		
		self.myRobot.tankDrive(leftMotVal, rightMotVal)
		
		
		
if __name__ == '__main__':
    wp.run(MyRobot)