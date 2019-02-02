#!/usr/bin/env python3

import wpilib as wp
import robotfuncs as rf
import time as tm
from networktables import NetworkTables as NT
import wpiJoystickOverlay as joy
import isClose as ic

def update_dash(roboSelf, chooser, gearSensor, right = 0.0, left = 0.0): 
	wp.SmartDashboard.putNumber("Gyro:",round(roboSelf.gyro.getAngle(), 2))
	wp.SmartDashboard.putNumber("Right Encoder:",roboSelf.rightEncd.get())
	wp.SmartDashboard.putNumber("Left Encoder:",roboSelf.leftEncd.get())
	wp.SmartDashboard.putNumber("Shoot Encoder:",roboSelf.shootEncd.get())
	wp.SmartDashboard.putNumber("Shoot Speed:",roboSelf.shootEncd.getRate())
			
	wp.SmartDashboard.putNumber("Right Motor:", right)
	wp.SmartDashboard.putNumber("Left Motor:", left)
	
	wp.SmartDashboard.putBoolean("Gear Sensor:", gearSensor.get())
	
	calGyro = wp.SmartDashboard.getBoolean("calGyro:", True)
	resetGyro = wp.SmartDashboard.getBoolean("resetGyro:", True)
	encodeReset = wp.SmartDashboard.getBoolean("resetEnc:", True)
	shootAuto = wp.SmartDashboard.getBoolean("Shooting Auto", True)
	
	
	if(resetGyro):
		roboSelf.gyro.reset()
		wp.SmartDashboard.putBoolean("resetGyro:", False)
		
	if(calGyro):
		roboSelf.gyro.calibrate()
		wp.SmartDashboard.putBoolean("calGyro:", False)
		
	if(encodeReset):
		roboSelf.rightEncd.reset()
		roboSelf.leftEncd.reset()
		roboSelf.shootEncd.reset()
		wp.SmartDashboard.putBoolean("resetEnc:", False)
		
	return chooser.getSelected(), shootAuto

#deleted old camera code because new stuff works better
	
class MyRobot(wp.SampleRobot):
	def robotInit(self):
		'''Robot initialization function'''
		self.motorFrontRight = wp.VictorSP(2)
		self.motorBackRight = wp.VictorSP(4)
		self.motorMiddleRight = wp.VictorSP(6)
		self.motorFrontLeft = wp.VictorSP(1)
		self.motorBackLeft = wp.VictorSP(3)
		self.motorMiddleLeft = wp.VictorSP(5)
		self.intakeMotor = wp.VictorSP(8)
		self.shootMotor1 = wp.VictorSP(7)        	
		self.shootMotor2 = wp.VictorSP(9)
		self.liftMotor = wp.VictorSP(0)  
		
		self.gyro = wp.ADXRS450_Gyro(0)     
		self.accel = wp.BuiltInAccelerometer()
		self.gearSensor = wp.DigitalInput(6)
		self.LED = wp.DigitalOutput(9)
		self.rightEncd = wp.Encoder(0,1)	
		self.leftEncd = wp.Encoder(2,3)
		self.shootEncd = wp.Counter(4)
		
		self.compressor = wp.Compressor()
		self.shifter = wp.DoubleSolenoid(0,1)
		self.ptoSol = wp.DoubleSolenoid(2,3)
		self.kicker = wp.DoubleSolenoid(4,5)
		self.gearFlap = wp.DoubleSolenoid(6,7)
		
		self.stick = wp.Joystick(0)
		self.stick2 = wp.Joystick(1)
		self.stick3 = wp.Joystick(2)
		
		
		#Initial Dashboard Code
		wp.SmartDashboard.putNumber("Turn Left pos 1:", 11500)
		wp.SmartDashboard.putNumber("Lpos 2:", -57)
		wp.SmartDashboard.putNumber("Lpos 3:", 5000)
		wp.SmartDashboard.putNumber("stdist:", 6000)
		wp.SmartDashboard.putNumber("Turn Right pos 1:", 11500)
		wp.SmartDashboard.putNumber("Rpos 2:", 57)
		wp.SmartDashboard.putNumber("Rpos 3:", 5000)
		wp.SmartDashboard.putNumber("pos 4:", 39)
		wp.SmartDashboard.putNumber("-pos 4:", -39)
		wp.SmartDashboard.putNumber("Time", 5)
		wp.SmartDashboard.putBoolean("Shooting Auto", False)
		wp.SmartDashboard.putNumber("P", .08)
		wp.SmartDashboard.putNumber("I", 0.005)
		wp.SmartDashboard.putNumber("D", 0)
		wp.SmartDashboard.putNumber("FF", 0.85)
		self.chooser = wp.SendableChooser()
		self.chooser.addDefault("None", 4)
		self.chooser.addObject("Left Turn Auto", 1)
		self.chooser.addObject("Straight/Enc", 2)
		self.chooser.addObject("Right Turn Auto", 3)
		self.chooser.addObject("Straight/Timer", 5)
		self.chooser.addObject("Shoot ONLY", 6)
		wp.SmartDashboard.putData("Choice", self.chooser)
		wp.CameraServer.launch("vision.py:main")
		
	def autonomous(self):
			self.gyro.reset()
			rSide = 0
			lSide = 0
			straightAngle = 0
			turnGain = 50
			straitGain = 40 
			pos1 = wp.SmartDashboard.getNumber("Turn Left pos 1:", 4000)
			pos2 = wp.SmartDashboard.getNumber("Lpos 2:", 41)
			pos3 = wp.SmartDashboard.getNumber("Lpos 3:", 5000)
			pos4 = wp.SmartDashboard.getNumber("pos 4:", 50.75)
			negPos4 = wp.SmartDashboard.getNumber("-pos 4:", 50.75)			
			pos5 = wp.SmartDashboard.getNumber("stdist:", 5000)
			a3pos1 = wp.SmartDashboard.getNumber("Turn Right pos 1:", 1000)
			a3pos2 = wp.SmartDashboard.getNumber("Rpos 2:", 1000)
			a3pos3 = wp.SmartDashboard.getNumber("Rpos 3:", 1000)
			straightTime = wp.SmartDashboard.getNumber("Time", 5)
			intakeMotorSpeed = 0
			stage1 = True
			stage2 = False #stageNums are for the individual stages of auto
			stage3 = False
			setR = 0
			setL = 0
			shiftSet = 1
			kickerSet = 2
			auto, shootAuto = update_dash(self, self.chooser, self.gearSensor)
			startTime = tm.time()
			ptoSet = 1
			gearFlapSet = 2
			shootBegin = tm.time()
			pastGear = False
			shootSpeed = 0
			turned = False
			sStage1 = True
			sStage2 = False
			stage4 = False

			while self.isAutonomous() and self.isEnabled():
				self.shifter.set(shiftSet)
				self.gearFlap.set(gearFlapSet)
				self.compressor.setClosedLoopControl(True)
				auto, shootAuto = update_dash(self, self.chooser, self.gearSensor, setR, setL)
				if(auto == 1):
					if(abs(self.leftEncd.get()) < pos1 and abs(self.rightEncd.get()) < pos1 and stage1):
						setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.65, straitGain)
						stage2 = True
					elif(self.gyro.getAngle() > (pos2 + 0.1) and stage2):
						stage1 = False
						setR, setL = rf.angleFunc(self.gyro.getAngle(), pos2, turnGain)
						self.leftEncd.reset()
						self.rightEncd.reset()
						stage3 = True
					elif(abs(self.leftEncd.get()) < pos3 and abs(self.rightEncd.get()) < pos3 and stage3):
						stage2 = False
						setR, setL = rf.gyroFunc(self.gyro.getAngle(), pos2, -0.65, straitGain)
					else:
						setR = 0
						setL = 0
						stage4 = True
						stage3 = False
					
					if(shootAuto and stage4):
						shootSpeed = 1
						if(self.gearSensor.get() == 1):
							startTime = tm.time()
						if(self.gearSensor.get() == 0 and tm.time() > startTime + 2):
							if(self.gyro.getAngle() < (negPos4 + 0.2) and turned == False):
								print('going there')
								setR, setL = rf.angleFunc(self.gyro.getAngle(), negPos4, 15)
								shootBegin = tm.time()
							else:
								setR, setL = 0, 0
								turned = True
								
							if(turned):
								if(tm.time() < shootBegin + 0.75):
									kickerSet = 2
								elif(tm.time() < shootBegin + 1):
									kickerSet = 1
								else:
									shootBegin = tm.time()
						else:
							setL, setR = 0, 0
								
				if(auto == 2):
					self.gyro.reset()
					if(abs(self.rightEncd.get()) < pos5 or abs(self.leftEncd.get()) < pos5): 
						setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.5, straitGain)
					else:
						setR = 0
						setL = 0
								
				if(auto == 3):
					if(abs(self.leftEncd.get()) < a3pos1 and abs(self.rightEncd.get()) < a3pos1 and stage1):  # 
						setR, setL = rf.gyroFunc(self.gyro.getAngle(), 0, -0.65, straitGain)
						stage2 = True
					elif(abs(self.gyro.getAngle()) < (a3pos2 -.1) and stage2): #abs(self.leftEncd.get()) < pos2 and
						stage1 = False
						setR, setL = rf.angleFunc(self.gyro.getAngle(), a3pos2, turnGain)
						self.leftEncd.reset()
						self.rightEncd.reset()
						stage3 = True
					elif(abs(self.leftEncd.get()) < a3pos3 and abs(self.rightEncd.get()) < a3pos3 and stage3):
						stage2 = False
						setR, setL = rf.gyroFunc(self.gyro.getAngle(), a3pos2, -0.65, straitGain)
					else:
						setR = 0
						setL = 0
						stage4 = True
						stage3 = False
						
					if(shootAuto and stage4):
						shootSpeed = 1
						if(self.gearSensor.get() == 1):
							startTime = tm.time()
						if(self.gearSensor.get() == 0 and tm.time() > startTime + 2):
							if(self.gyro.getAngle() > (pos4 + 0.20) and turned == False):
								print('going there')
								setR, setL = rf.angleFunc(self.gyro.getAngle(), pos4, 15)
								shootBegin = tm.time()
							else:
								setR, setL = 0, 0
								turned = True
								
							if(turned):
								if(tm.time() < shootBegin + 0.75):
									kickerSet = 2
								elif(tm.time() < shootBegin + 1):
									kickerSet = 1
								else:
									shootBegin = tm.time()
						else:
							setL, setR = 0, 0
						
				if(auto == 4):
					print("No auto selected, doing nothing")
					pass
				if(auto == 5):
					if(tm.time() < (startTime + 5)):
						setR, setL = -0.5, -0.5
						setR *= 0.97
					else:
						setR = 0
						setL = 0
				if(auto == 6):
					shootSpeed = 1
					if(self.gearSensor.get() == 1):
						startTime = tm.time()
					if(self.gearSensor.get() == 0 and tm.time() > startTime + 1):
						if(self.gyro.getAngle() > (negPos4 + 0.5) and turned == False):
							print('going there')
							setR, setL = rf.angleFunc(self.gyro.getAngle(), negPos4, 50)
							shootBegin = tm.time()
						else:
							setR, setL = 0, 0
							turned = True
							
						if(turned):
							if(tm.time() < shootBegin + 0.95):
								kickerSet = 1
							elif(tm.time() < shootBegin + 1.15):
								kickerSet = 2
							else:
								shootBegin = tm.time()
							print(shootBegin)
					else:
						setL, setR = 0, 0
						
				
				
				self.motorFrontRight.set(setR * -1)
				self.motorMiddleRight.set(setR * -1)
				self.motorBackRight.set(setR * -1)	
				self.motorFrontLeft.set(setL)
				self.motorMiddleLeft.set(setL)
				self.motorBackLeft.set(setL)
				self.intakeMotor.set(intakeMotorSpeed)
				self.shootMotor1.set(shootSpeed)
				self.ptoSol.set(ptoSet)
				self.kicker.set(kickerSet)
				
				wp.Timer.delay(0.015)   # wait 5ms to avoid hogging CPU cycles
			
	def disabled(self):
		auto, shootAuto = update_dash(self, self.chooser, self.gearSensor)
		while self.isDisabled():
			auto, shootAuto = update_dash(self, self.chooser, self.gearSensor)
			wp.Timer.delay(0.015)   # wait 5ms to avoid hogging CPU cycles

	def operatorControl(self):
		past = False           #only used if we need to switch from tank to arcade, probably useless in this year's game
		driveType = True	   #see above line
		past2 = False          #Used in frontflip operation
		flipVar = True        #Also used in frontflip
		dtGain = 0.075         #Deadband amount
		setR = 0               #Default motor/compressor/shifter values
		setL = 0
		compressor = False
		highOn = True
		lowOn = False
		past3 = False
		gearFlapSet = 2
		gearFlip = False
		wantedSpeed = 300
		speedGain = 100
		intakeIsEnabled = False
		shiftSet = 2
		ptoSet = 1
		kickerSet = 1
		intakeMotorSpeed = 1
		pastIntake = False
		shootMotorSpeed = 0
		correctedR = 0
		correctedL = 0
		holdAngle = 0
		straitGain = 43
		isDTClose = False
		self.compressor.start()
		gear = False
		LED = 0
		while self.isOperatorControl() and self.isEnabled():
			joyValY = self.stick.getY()
			joyValX = self.stick.getX()
			joyVal2 = self.stick2.getY()
			shootSpeed = self.stick3.getZ()
			currentAccel = self.accel.getY()
			
			#driveTypeButton = self.stick2.getRawButton(3)
			driveSideButton = self.stick2.getRawButton(2)  #Front Flip Button
			intakeForward = self.stick3.getRawButton(3)    #Button to bring ballss in
			shootButton = self.stick3.getRawButton(2)	   #Trigger to shoot
			intakeBackward = self.stick3.getRawButton(11)  #Button to spit balls out
			gyroButton = self.stick.getRawButton(8)        #Button to calibrate gyro, mostly used in debugging
			highButton = self.stick2.getRawButton(5)      #Button to shift into high gear, might not work depending on hardware
			lowButton = self.stick2.getRawButton(4)	   #Button to shift into low gear, see above
			compressorButton = self.stick3.getRawButton(8)
			forwardFlip = self.stick.getRawButton(6)
			flipFlip = self.stick.getRawButton(7)
			ptoOn = self.stick2.getRawButton(11)
			ptoOff = self.stick2.getRawButton(10)
			kickerButton = self.stick3.getRawButton(1)
			gearFlapButton = self.stick3.getRawButton(4)
			gearFlapButton2 = self.stick3.getRawButton(5)
			
			P = wp.SmartDashboard.getNumber("P", 1)
			I = wp.SmartDashboard.getNumber("I", 1)
			D = wp.SmartDashboard.getNumber("D", 1)
			FF = wp.SmartDashboard.getNumber("FF", 1)
			
			self.shootPID.setPID(P,I,D,FF)

			#toggle drivetype button
			#if (past == False and driveTypeButton == True):
			#	driveType = not driveType                           FLIP TO ARCADE DRIVE
			#past = driveTypeButton                                 IN CASE WE NEED IT, MOSTLY USELESS

			#toggle driveside button
			if (past2 == False and driveSideButton):
				flipVar = not flipVar
			past2 = driveSideButton
			
			if (forwardFlip):                                       #FrontFlip
				flipVar = False
			elif (flipFlip):
				flipVar = True
			
			rightM, leftM = rf.tank(joyValY, joyVal2)
				
			lSide, rSide = rf.flip(flipVar, rightM, leftM) 
			
			#Intake
			intakeMotorSpeed = 0
			
			if(pastIntake == False and intakeForward):
				intakeIsEnabled = not intakeIsEnabled
			pastIntake = intakeForward
			
			if(intakeIsEnabled):
				intakeMotorSpeed = -1
				
			if(intakeBackward):
				intakeMotorSpeed = 1
				
			#Gears
			if(self.gearSensor.get() == 1):
				gear = True
				LED = 0
			else:
				gear = False
				LED = 1
			if(gearFlapButton):
				gearFlapSet = 1
			if(gearFlapButton2):
				gearFlapSet = 2
			
			#if(LEDoffButton):
			#	LED = 0
			
			#toggle compressor button
			if (compressor == False and compressorButton == True):
				compressor = not compressor
				
			past3 = compressorButton
			
			if(compressor == False and compressorButton):
				self.compressor.start()
			if(compressor == True and compressorButton):
				self.compressor.stop()
			
			#toggle shifting button
			if(highButton):
				shiftSet = 1
			if(lowButton):
				shiftSet = 2
				
			#toggle pto
			if(ptoOn):
				ptoSet = 2
			if(ptoOff):
				ptoSet = 1
				
			##This sets our dead band on the joystick
			if ((rSide <= dtGain*-1) or (rSide >= dtGain)):
				setR = rf.deadband(rSide, dtGain)
			else:
				setR = 0
			
			if ((lSide <= dtGain*-1) or (lSide >= dtGain)):
				setL = rf.deadband(lSide, dtGain)
			else:
				setL = 0
			
			#Locks robot motion to forward when PTO is engaged
			if(ptoSet == 2):
				self.compressor.setClosedLoopControl(False)
				if(joyValY > 0):
					setL = 0
			else:
				self.compressor.setClosedLoopControl(True)
			
			#Drivetrain bias correction
			
			
			#motor sets
			self.motorFrontRight.set(setR)
			self.motorBackRight.set(setR)
			self.motorMiddleRight.set(setR)			
			self.motorFrontLeft.set(setL * -1)
			self.motorBackLeft.set(setL * -1)
			self.motorMiddleLeft.set(setL * -1)	
			self.intakeMotor.set(intakeMotorSpeed)
			self.shifter.set(shiftSet)
			self.ptoSol.set(ptoSet)
			self.gearFlap.set(gearFlapSet)
			self.LED.set(LED)
			print(self.shootPID.get())
			#smartdashboard outputs
			auto, shootAuto = update_dash(self, self.chooser, self.gearSensor)

			wp.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wp.run(MyRobot)