
joyValY = self.stick.getY()
joyValX = self.stick.getX()
joyVal2 = self.stick.getRawAxis(3)
shootSpeed = self.stick3.getZ()


#driveTypeButton = self.stick2.getRawButton(3)
driveSideButton = self.stick.getRawButton(12)  #Front Flip Button
intakeForward = self.stick3.getRawButton(3)    #Button to bring ballss in
shootButton = self.stick3.getRawButton(2)	   #Trigger to shoot
intakeBackward = self.stick3.getRawButton(11)  #Button to spit balls out
gyroButton = self.stick3.getRawButton(9)        #Button to calibrate gyro, mostly used in debugging
highButton = self.stick.getRawButton(7)      #Button to shift into high gear, might not work depending on hardware
lowButton = self.stick.getRawButton(8)	   #Button to shift into low gear, see above
compressorButton = self.stick3.getRawButton(8)
forwardFlip = self.stick.getRawButton(1)
flipFlip = self.stick.getRawButton(2)
ptoOn = self.stick.getRawButton(5)
ptoOff = self.stick.getRawButton(6)
kickerButton = self.stick3.getRawButton(1)