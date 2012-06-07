from numpy import sin,cos,radians,abs,angle

def polarToRealImag(mag,phase):
    """
    Converts magnitude-phase to real-imaginary
    so all complex results are consistent
    @param mag magnitude c^2
    @param phase phase angle phi (degrees; theta)
    @retval realValue the real component a of a+bi
    @retval imagValue the imaginary component b of a+bi
    """
    realValue = mag*cos(radians(phase)) # is phase in degrees/radians?
    imagValue = mag*sin(radians(phase))
    return complex(realValue,imagValue)

def realImagToMagPhase(realImag):
    """returns the magnitude and phase (degrees) of a complex number"""
    return abs(realImag),angle(realImag,deg=True)