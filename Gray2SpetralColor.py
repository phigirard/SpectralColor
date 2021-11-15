#@ Integer(label="Wavelength start", description="Start of the wavelength range",value=409, persist=False)  wavelength0
#@ Integer(label="Wavelength step", description="Wavelength resolution",value=9, persist=False)  step

from ij.gui import GenericDialog  
from ij import WindowManager as WM 
from ij import IJ, ImagePlus, CompositeImage
from ij.process import LUT
from ij.plugin.filter import Analyzer
from ij.measure import ResultsTable, Measurements

from java.awt import Color
from jarray import zeros
from math import *
  


# Taken from Earl F. Glynn's web page:
# <a href="http://www.efg2.com/Lab/ScienceAndEngineering/Spectra.htm">Spectra Lab Report</a>

def waveLengthToRGB(Wavelength) :
	Gamma = 0.80
	IntensityMax = 255
	Red = 0.0
	Green = 0.0
	Blue = 0.0
	if((Wavelength >= 380) and (Wavelength < 440)) :
		Red = float(440-Wavelength ) / (440 - 380)
		Green = 0.0
		Blue = 1.0
	elif ((Wavelength >= 440) and (Wavelength < 490)) :
		Red = 0.0
		Green = float(Wavelength - 440) / (490 - 440)
		Blue = 1.0
	elif((Wavelength >= 490) and (Wavelength < 510)) :
		Red = 0.0
		Green = 1.0
		Blue = -float(Wavelength - 510) / (510 - 490)
	elif((Wavelength >= 510) and (Wavelength < 580)):
		Red = float(Wavelength - 510) / (580 - 510)
		Green = 1.0
		Blue = 0.0
	elif((Wavelength >= 580) and (Wavelength < 645)):
		Red = 1.0
		Green = -float(Wavelength - 645) / (645 - 580)
		Blue = 0.0
	elif((Wavelength >= 645) and (Wavelength < 781)):
		Red = 1.0
		Green = 0.0
		Blue = 0.0
	else :
		Red = 0.0
		Green = 0.0
		Blue = 0.0

    # Let the intensity fall off near the vision limits
	if((Wavelength >= 380) and (Wavelength < 420)) :
		factor = 0.3 + 0.7 * (Wavelength - 380) / (420 - 380)
	elif((Wavelength >= 420) and (Wavelength < 701)) :
		factor = 1.0
	elif((Wavelength >= 701) and (Wavelength < 781)) :
		factor = 0.3 + 0.7 * (780 - Wavelength) / (780 - 700)
	else :
		factor = 0.0

	rgb = zeros(3, 'i')


	rgb[0] = 0 if Red == 0 else int(round(IntensityMax * pow(Red * factor, Gamma)))
	rgb[1] = 0 if Green == 0 else  int(round(IntensityMax * pow(Green * factor, Gamma)))
	rgb[2] = 0 if Blue == 0 else int(round(IntensityMax * pow(Blue * factor, Gamma)))
	return rgb



imp = WM.getCurrentImage()  
if not imp:  
	print "Open an image first!"  

n = imp.getStackSize()

impComp=CompositeImage(imp.duplicate(), CompositeImage.COLOR )

IJ.run(impComp, "Select All", "")
Analyzer.setMeasurements(Measurements.MIN_MAX)
Analyzer.setPrecision(5)
rt = ResultsTable.getResultsTable()
rt.reset() 
IJ.run(impComp, "Measure Stack...", "")
maxmax= max(rt.getColumnAsDoubles( rt.getColumnIndex( 'Max') ))
rt.reset() 
rt.getResultsWindow().close(False)
for i in range(n):
	impComp.setSlice(i+1)
	impComp.setDisplayRange(0, maxmax)
	IJ.run(impComp, "Apply LUT", "stack")

luts = impComp.getLuts()
for i in range(n):
	rgb = waveLengthToRGB(wavelength0+ i*step)
	luts[i] = LUT.createLutFromColor(Color(rgb[0],rgb[1],rgb[2]))

impComp.setLuts(luts)
impComp.updateAllChannelsAndDraw() #updateAndDraw()
for i in range(n):
	impComp.setSlice(i+1)
	IJ.resetMinAndMax(impComp)
	IJ.run(impComp, "Enhance Contrast", "saturated=0.35")

IJ.run(impComp, "RGB Color", "")
impComp.show()
print 'End'

