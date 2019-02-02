#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTables as NT
import wpiJoystickOverlay as joy
import isClose as ic
from wpilib.drive import DifferentialDrive
import autoPositions as ap
#import ctre
	
class MyRobot(wp.IterativeRobot):
	def robotInit(self):
		'''Robot initialization function'''
		self.leftMotor1 = wp.VictorSP(1) #motor initialization
		self.leftMotor2 = wp.VictorSP(3)
		self.leftMotor3 = wp.VictorSP(5)
		self.rightMotor1 = wp.VictorSP(2)
		self.rightMotor2 = wp.VictorSP(4)
		self.rightMotor3 = wp.VictorSP(6)
		self.armMotor = wp.VictorSP(7)
		self.leftIntakeMotor = wp.VictorSP(8)
		self.rightIntakeMotor = wp.VictorSP(9)
		
		self.leftSide = wp.SpeedControllerGroup(self.leftMotor1, self.leftMotor2, self.leftMotor3) #speed controller groups
		self.rightSide = wp.SpeedControllerGroup(self.rightMotor1, self.rightMotor2, self.rightMotor3)
		self.intakeMotors = wp.SpeedControllerGroup(self.leftIntakeMotor, self.rightIntakeMotor)
		
		self.myRobot = DifferentialDrive(self.leftSide, self.rightSide)
		self.myRobot.setExpiration(0.1)
		
		self.leftStick = wp.Joystick(0)
		self.rightStick = wp.Joystick(1)
		self.armStick = wp.XboxController(2)
		
		self.gyro = wp.ADXRS450_Gyro(0)
		self.rightEncd = wp.Encoder(2,3)
		self.leftEncd = wp.Encoder(0,1)
		self.armPot = wp.AnalogPotentiometer(0, 270, -135)
		
		self.compressor = wp.Compressor()
		self.shifter = wp.DoubleSolenoid(0,1)
		
		wp.SmartDashboard.putNumber("Straight Position", 15000)
		wp.SmartDashboard.putNumber("leftMiddleAutoStraight", 13000)
		wp.SmartDashboard.putNumber("leftMiddleAutoLateral", 14000)
		wp.SmartDashboard.putNumber("Left Switch Pos 1", 18000)
		wp.SmartDashboard.putNumber("Left Switch Angle", 90)
		wp.SmartDashboard.putNumber("Left Switch Pos 2", 5000)
		wp.SmartDashboard.putNumber("Switch Score Arm Position", 70)
		wp.SmartDashboard.putNumber("Front Position 1", 74)
		wp.SmartDashboard.putNumber("Front Position 2", 16)
		wp.SmartDashboard.putNumber("Front Position 3", -63)
		wp.SmartDashboard.putNumber("lvl2 Position 1", 60)
		wp.SmartDashboard.putNumber("lvl2 Position 3", -50)
		wp.SmartDashboard.putNumber("lvl3 Position 3", -38)
		wp.SmartDashboard.putNumber("lvl3 Position 1", 45)
		
		wp.SmartDashboard.putBoolean("switchScore?", False)
		
		self.chooser = wp.SendableChooser()
		self.chooser.addDefault("None", 4)
		self.chooser.addObject("Straight/Enc", 1)
		self.chooser.addObject("Left Side Switch Auto", 2)
		self.chooser.addObject("Right Side Switch Auto (switch)", 3)
		self.chooser.addObject("Center Auto", 5)
		wp.SmartDashboard.putData("Choice", self.chooser)
		wp.CameraServer.launch("vision.py:main")
	
	def robotPeriodic(self):
		wp.SmartDashboard.putNumber("Gyro:",round(self.gyro.getAngle(), 2))
		wp.SmartDashboard.putNumber("Right Encoder:",self.rightEncd.get())
		wp.SmartDashboard.putNumber("Left Encoder:",self.leftEncd.get())
		wp.SmartDashboard.putNumber("Arm Postition", self.armPot.get())
		
		calGyro = wp.SmartDashboard.getBoolean("calGyro:", True)
		resetGyro = wp.SmartDashboard.getBoolean("resetGyro:", True)
		encodeReset = wp.SmartDashboard.getBoolean("resetEnc:", True)
		self.switchScore = wp.SmartDashboard.getBoolean("switchScore?", True)
		self.straightPos = wp.SmartDashboard.getNumber("Straight Position", 4000)
		self.leftAutoPos1 = wp.SmartDashboard.getNumber("Left Switch Pos 1", 4000)
		self.leftAutoPos2 = wp.SmartDashboard.getNumber("Left Switch Angle", 90)
		self.leftAutoPos3 = wp.SmartDashboard.getNumber("Left Switch Pos 2", 4000)
		self.frontArmPos1 = wp.SmartDashboard.getNumber("Front Position 1", 78)
		self.frontArmPos2 = wp.SmartDashboard.getNumber("Front Position 2", 22)
		self.frontArmPos3 = wp.SmartDashboard.getNumber("Front Position 3", -63)
		self.frontArmLvl2Pos1 = wp.SmartDashboard.getNumber("lvl2 Position 1", 68)
		self.frontArmLvl2Pos3 = wp.SmartDashboard.getNumber("lvl2 Position 3", -50)
		self.frontArmLvl3Pos3 = wp.SmartDashboard.getNumber("lvl3 Position 3", -38)
		self.frontArmLvl3Pos1 = wp.SmartDashboard.getNumber("lvl3 Position 1", 57)
		
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
		self.auto = self.chooser.getSelected()
	
	def autonomousInit(self):
		self.auto = self.chooser.getSelected()
		self.leftMotorVal = 0
		self.rightMotorVal = 0
		self.gyroFuncGain = 40
		self.angleFuncGain = 40
		self.leftMotVal = 0
		self.rightMotVal = 0
		self.armSet = 0
		self.intakeSet = 0
		self.posGain = 18
		self.armSpeed = 1
		self.armPos = self.armPot.get()
		self.startTime = tm.time()
		self.gamePlacement = wp.DriverStation.getInstance().getGameSpecificMessage()
		self.straightPos = wp.SmartDashboard.getNumber("Straight Position", 16000)
		self.leftAutoPos1 = wp.SmartDashboard.getNumber("Left Switch Pos 1", 4000)
		self.leftAutoPos2 = wp.SmartDashboard.getNumber("Left Switch Angle", 90)
		self.leftAutoPos3 = wp.SmartDashboard.getNumber("Left Switch Pos 2", 4000)
		self.leftMiddleAutoStraight = wp.SmartDashboard.getNumber("leftMiddleAutoStraight", 21)
		self.leftMiddleAutoLateral = wp.SmartDashboard.getNumber("leftMiddleAutoLateral", 21)
		self.switchScoreArmPos = wp.SmartDashboard.getNumber("Switch Score Arm Position", 70)
		self.frontArmPos1 = wp.SmartDashboard.getNumber("Front Position 1", 78)
		self.frontArmPos2 = wp.SmartDashboard.getNumber("Front Position 2", 22)
		self.frontArmPos3 = wp.SmartDashboard.getNumber("Front Position 3", -63)
		self.switchScore = wp.SmartDashboard.getBoolean("switchScore?", True)
		self.StartButtonPos = wp.SmartDashboard.getNumber("lvl3 Position 1", 57)
		self.stage1 = True
		self.stage2 = False
		self.stage3 = False
		self.stage4 = False
		self.stage5 = False
		self.stage6 = False
	def autonomousPeriodic(self):
		#autonomous code will go here
		armPos = self.armPot.get()
		self.gamePlacement = wp.DriverStation.getInstance().getGameSpecificMessage()
		if(self.auto == 1):
			if(abs(self.rightEncd.get()) < self.straightPos and self.stage1):
				self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)
				self.stage2 = True
			elif(self.stage2):
				self.stage1 = False
				self.leftMotVal, self.rightMotVal = 0, 0
				if(self.switchScore and self.gamePlacement != "" and self.gamePlacement == "RRR" or self.gamePlacement == "RRL" or self.gamePlacement == "RLR" or self.gamePlacement == "RLL"):
					self.intakeSet = -1
				else:
					self.instakeSet = 0
		if(self.auto == 2):
			#Guidlines for switch placement on left side:
			#check switch placement
			#Move Forward
			#Turn right 90 degrees
			#Move Forward to wall
			#place Cube
			
			if(self.gamePlacement != "" and self.gamePlacement == "LLL" or self.gamePlacement == "LRL" or self.gamePlacement == "LLR" or self.gamePlacement == "LRR"):
				if(abs(self.rightEncd.get()) < self.leftAutoPos1 and self.stage1):
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)					
					self.stage2 = True
				elif(self.gyro.getAngle() < self.leftAutoPos2 + 0.1 and self.stage2):
					self.stage1 = False
					self.leftMotVal, self.rightMotVal = rf.angleFunc(self.gyro.getAngle(), self.leftAutoPos2, self.angleFuncGain)
					self.leftEncd.reset()
					self.rightEncd.reset()
					self.stage3 = True
				elif(abs(self.rightEncd.get()) < self.leftAutoPos3 and self.stage3):
					self.stage2 = False
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), self.leftAutoPos2, 0.65, self.gyroFuncGain)
				else:
					
					self.leftMotVal, self.rightMotVal = 0, 0
					self.intakeSet = -1
					
			else:
				if(abs(self.rightEncd.get()) <= self.leftAutoPos1):
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)
					self.stage2 = True
				elif(self.stage2):
					self.stage1 = False
					self.leftMotVal, self.rightMotVal = 0, 0

		if(self.auto == 3):
			if(self.gamePlacement != "" and self.gamePlacement == "RRR" or self.gamePlacement == "RRL" or self.gamePlacement == "RLR" or self.gamePlacement == "RLL"):
					if(abs(self.rightEncd.get()) < self.leftAutoPos1 and self.stage1):
						self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)					
						self.stage2 = True
					elif(self.gyro.getAngle() > (self.leftAutoPos2 * -1) + 0.1 and self.stage2):
						self.stage1 = False
						self.leftMotVal, self.rightMotVal = rf.angleFunc(self.gyro.getAngle(), (self.leftAutoPos2 * -1), self.angleFuncGain)
						self.leftEncd.reset()
						self.rightEncd.reset()
						self.stage3 = True
					elif(abs(self.rightEncd.get()) < self.leftAutoPos3 and self.stage3):
						self.stage2 = False
						self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), (self.leftAutoPos2 * -1), 0.65, self.gyroFuncGain)
					else:
						self.leftMotVal, self.rightMotVal = 0, 0
						self.intakeSet = -1
					
			else:
				if(abs(self.rightEncd.get()) <= self.leftAutoPos1):
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)
					self.stage2 = True
				elif(self.stage2):
					self.stage1 = False
					self.leftMotVal, self.rightMotVal = 0, 0
		if(self.auto == 5):
			if(self.gamePlacement != "" and self.gamePlacement == "LLL" or self.gamePlacement == "LRL" or self.gamePlacement == "LLR" or self.gamePlacement == "LRR"):
				if(abs(self.rightEncd.get()) < (self.leftMiddleAutoStraight / 2) and self.stage1):
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)					
					self.stage2 = True
				elif(self.gyro.getAngle() > (self.leftAutoPos2 * -1) + 0.1 and self.stage2):
					self.stage1 = False
					self.leftMotVal, self.rightMotVal = rf.angleFunc(self.gyro.getAngle(), (self.leftAutoPos2 * -1), self.angleFuncGain)
					self.leftEncd.reset()
					self.rightEncd.reset()
					self.stage3 = True
				elif(abs(self.rightEncd.get()) < self.leftMiddleAutoLateral and self.stage3):
					self.stage2 = False
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), (self.leftAutoPos2 * -1), 0.65, self.gyroFuncGain)
					self.stage4 = True
				elif(self.gyro.getAngle() < (0) + 0.1 and self.stage4):
					self.stage3 = False
					self.leftMotVal, self.rightMotVal = rf.angleFunc(self.gyro.getAngle(), 0, self.angleFuncGain)
					self.leftEncd.reset()
					self.rightEncd.reset()
					self.stage5 = True
				elif(abs(self.rightEncd.get()) < (self.leftMiddleAutoStraight/1.50) and self.stage5):
					self.stage4 = False
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)
					if(armPos < (self.StartButtonPos - 1) or armPos > (self.StartButtonPos + 1)):
						self.armSet = rf.goToPos(armPos, self.StartButtonPos, self.armSpeed, self.posGain)
					else:
						self.armSet = 0
				else:
					self.leftMotVal, self.rightMotVal = 0, 0
					self.intakeSet = -1
			else:
				if(abs(self.rightEncd.get()) < self.straightPos and self.stage1):
					self.leftMotVal, self.rightMotVal = rf.gyroFunc(self.gyro.getAngle(), 0, 0.65, self.gyroFuncGain)
					if(armPos < (self.StartButtonPos - 1) or armPos > (self.StartButtonPos + 1)):
						self.armSet = rf.goToPos(armPos, self.StartButtonPos, self.armSpeed, self.posGain)
					else:
						self.armSet = 0
					if(abs(self.rightEncd.get()) > (self.straightPos - 1000)):
						self.intakeSet = -1
					self.stage2 = True
				elif(self.stage2):
					self.stage1 = False
					self.leftMotVal, self.rightMotVal = 0, 0
					self.intakeSet = -1
			
					
		self.leftIntakeMotor.set(self.intakeSet)
		self.rightIntakeMotor.set(self.intakeSet * -1)
		self.armMotor.set(self.armSet)
		self.myRobot.tankDrive(self.rightMotVal, self.leftMotVal)
		
		
		
	def teleopInit(self):
		self.myRobot.setSafetyEnabled(True)
		self.pastFrontFlipButton = False
		self.flip = True
		self.armSet = 0
		self.shiftSet = 1
		self.posGain = 27
		self.posGain2 = 27
		self.armSpeed = 1
		self.lastXButton = False
		self.lastYButton = False
		self.lastBButton = False
		self.lastAButton = False
		self.lastLBumper = False
		self.lastRBumper = False
		self.lastStartButton = False
		
		self.XButtonPos = wp.SmartDashboard.getNumber("Front Position 1", 77.6)
		self.YButtonPos = wp.SmartDashboard.getNumber("Front Position 2", 22)
		self.BButtonPos = wp.SmartDashboard.getNumber("Front Position 3", -62.8)
		self.AButtonPos = wp.SmartDashboard.getNumber("lvl2 Position 1", 30)
		self.frontArmLvl2Pos3 = wp.SmartDashboard.getNumber("lvl2 Position 3", -50)
		self.frontArmLvl3Pos3 = wp.SmartDashboard.getNumber("lvl3 Position 3", -38)
		self.StartButtonPos = wp.SmartDashboard.getNumber("lvl3 Position 1", 57)
		#wp.SmartDashboard.getNumber("Back Position 1", -90)
		#wp.SmartDashboard.getNumber("Back Position 2", -45)
		#wp.SmartDashboard.getNumber("Back Position 3", -30)
		
	def teleopPeriodic(self):
		#Joystick Variables
		leftJoyValY = self.leftStick.getY()
		rightJoyValY = self.rightStick.getY()
		armJoyValY = self.armStick.getRawAxis(3)
		frontFlipButton = self.rightStick.getRawButton(2)
		armPos = self.armPot.get()
		highShiftButton = self.rightStick.getRawButton(4)
		lowShiftButton = self.rightStick.getRawButton(5)
		self.compressorButtonOn = self.rightStick.getRawButton(9)
		self.compressorButtonOff = self.rightStick.getRawButton(8)
		self.intakeInButton = self.armStick.getRawButton(7)
		self.intakeOutButton = self.armStick.getRawButton(8)
		self.buttonX = self.armStick.getRawButton(1)
		self.buttonY = self.armStick.getRawButton(4)
		self.buttonB = self.armStick.getRawButton(3)
		self.buttonA = self.armStick.getRawButton(2)
		self.buttonStart = self.armStick.getRawButton(10)
		self.buttonLBumper = self.armStick.getRawButton(5)
		self.buttonRBumper = self.armStick.getRawButton(6)
		
		#Automatic arm positioning
		if(self.buttonX == True and self.lastXButton == False):
			self.lastXButton = True
			self.lastYButton = False
			self.lastBButton = False
			self.lastAButton = False
			self.lastStartButton = False
		if(self.buttonY == True and self.lastYButton == False):
			self.lastXButton = False
			self.lastYButton = True
			self.lastBButton = False
			self.lastAButton = False
			self.lastStartButton = False
		if(self.buttonB == True and self.lastBButton == False):
			self.lastXButton = False
			self.lastYButton = False
			self.lastBButton = True
			self.lastAButton = False
			self.lastStartButton = False
		if(self.buttonA and self.lastAButton == False):
			self.lastXButton = False
			self.lastYButton = False
			self.lastBButton = False
			self.lastAButton = True
			self.lastStartButton = False
		if(self.buttonStart and self.lastStartButton == False):
			self.lastXButton = False
			self.lastYButton = False
			self.lastBButton = False
			self.lastAButton = False
			self.lastStartButton = True
		if(armJoyValY > 0.075 or armJoyValY < -0.075):
			self.lastXButton = False
			self.lastYButton = False
			self.lastBButton = False
			
		if(self.lastXButton):
			if(armPos < (self.XButtonPos - 1) or armPos > (self.XButtonPos + 1)):
				self.armSet = rf.goToPos(armPos, self.XButtonPos, self.armSpeed, self.posGain)
			else:
				self.lastXButton = False
		elif(self.lastYButton):
			if(armPos < (self.YButtonPos - 1) or armPos > (self.YButtonPos + 1)):	
				self.armSet = rf.goToPos(armPos, self.YButtonPos, self.armSpeed, self.posGain)
			else:
				self.lastYButton = False
		elif(self.lastBButton):
			if(armPos < (self.BButtonPos - 1) or armPos > (self.BButtonPos + 1)):
				self.armSet = rf.goToPos(armPos, self.BButtonPos, self.armSpeed, self.posGain)
			else:
				self.lastBButton = False
		elif(self.lastAButton):
			if(armPos < (self.AButtonPos - 1) or armPos > (self.AButtonPos + 1)):
				self.armSet = rf.goToPos(armPos, self.AButtonPos, self.armSpeed, self.posGain)
			else:
				self.lastAButton = False
		elif(self.lastStartButton):
			if(armPos < (self.StartButtonPos - 1) or armPos > (self.StartButtonPos + 1)):
				self.armSet = rf.goToPos(armPos, self.StartButtonPos, self.armSpeed, self.posGain)
			else:
				self.lastBButton = False
		else:
			self.armSet = (armJoyValY * 0.75)
			
		#Intake Motor Control
		if(self.intakeInButton):
			self.intakeSet = 1
		elif(self.intakeOutButton):
			self.intakeSet = -1
		else:
			self.intakeSet = 0
		
		if(highShiftButton):
			self.shiftSet = 1
		elif(lowShiftButton):
			self.shiftSet = 2
		
		
		
		#FrontFlip
		if(self.pastFrontFlipButton == False and frontFlipButton):
			self.flip = not self.flip
		self.pastFrontFlipButton = frontFlipButton
		
		leftMotVal, rightMotVal = rf.flip(self.flip, leftJoyValY, rightJoyValY)
		self.armMotor.set(self.armSet)
		self.shifter.set(self.shiftSet)
		self.leftIntakeMotor.set(self.intakeSet)
		self.rightIntakeMotor.set(self.intakeSet * -1)
		self.myRobot.tankDrive(rightMotVal, leftMotVal)
		
		
		
		
		
if __name__ == '__main__':
    wp.run(MyRobot)