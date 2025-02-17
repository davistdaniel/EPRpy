#DESC	1.2 * DESCRIPTOR INFORMATION ***********************
*
*	Dataset Type and Format:
*
DSRC	EXP
BSEQ	BIG
IKKF	REAL
XTYP	IDX
YTYP	IGD
ZTYP	NODATA
*
*	Item Formats:
*
IRFMT	D
YFMT	D
*
*	Data Ranges and Resolutions:
*
XPTS	1024
XMIN	3273.650000
XWID	98.803418
YPTS	48
YMIN	0.000000
YWID	72031.990000
*
*	Documentational Text:
*
TITL	'tempo_time'
IRNAM	'Intensity'
XNAM	'Field'
YNAM	'Time'
IRUNI	''
XUNI	'G'
YUNI	's'
*
************************************************************
*
#SPL	1.2 * STANDARD PARAMETER LAYER
*
OPER    xuser
DATE    11/04/21
TIME    10:46:52
CMNT    
SAMP    
SFOR    
STAG    C
EXPT    CW
OXS1    IADC
AXS1    B0VL
AXS2    ETIM
AXS3    
A2RS    48
A1CT    0.33231
A1SW    0.00989
MWFQ    9.331e+09
MWPW    0.0006325
AVGS    25
SPTP    0.0586
RCAG    42
RCHM    1
B0MA    5e-05
B0MF    100000
RCPH    0.0
RCOF    0.0
A1RS    1024
RCTC    0
*
************************************************************
*
#DSL	1.0 * DEVICE SPECIFIC LAYER
*

.DVC     acqStart, 1.0


.DVC     delay, 1.0

Delay              200 ms
NbPoints           48

.DVC     fieldCtrl, 1.0

AllegroMode        True
CenterField        3323.10 G
Delay              0.0 s
FieldFlyback       On
FieldWait          Wait LED off
GFactor            2.006000
MeasuringHall      False
SetToSampleG       False
StaticFieldMon     3322.800 G
SweepDirection     Up
SweepWidth         98.9 G
WidthTM            200.0 G

.DVC     fieldSweep, 1.0


.DVC     freqCounter, 1.0

FrequencyMon       9.331000 GHz
QMonitBridge       On

.DVC     mwBridge, 1.0

AcqFineTuning      Never
AcqScanFTuning     Off
AcqSliceFTuning    Off
BridgeCalib        60.0
Power              0.6325 mW
PowerAtten         25.0 dB

.DVC     recorder, 1.0

BaselineCorr       Off
NbScansAcc         25
NbScansDone        25
NbScansToDo        25
ReplaceMode        Off
SmoothMode         Manual
SmoothPoints       1

.DVC     scanEnd, 1.0


.DVC     signalChannel, 1.0

AFCTrap            True
AllegroMode        True
AllowShortCt       False
Calibrated         True
ConvTime           58.60 ms
DModDetectSCT      First
DoubleModAcc       1
DoubleModFreq      5.000 kHz
DoubleMode         False
DualDetect         OFF
EliDelay           1.0 us
Enable1stHarm      True
Enable1stHarm90    False
Enable2ndHarm      False
Enable2ndHarm90    False
Enable3rdHarm      False
Enable3rdHarm90    False
Enable4thHarm      False
Enable4thHarm90    False
Enable5thHarm      False
Enable5thHarm90    False
EnableDisp         False
EnableImag         Disable
ExtLockIn          False
ExtTrigger         False
Gain               42 dB
GainB              42 dB
Harmonic           1
HighPass           True
InputPlugA         AC3
InputPlugB         AC3
Integrator         False
IsCalibExp         False
ModAmp             0.500 G
ModFreq            100.00 kHz
ModPhase           0.0
Offset             0.0 %
QuadMode           False
Resolution         1024
Resonator          1
SctNorm            True
SctRevision        Allegro
SetAllOrd          False
SetOrdDef          False
SpuExtension       True
SpuRevision        MultiHarmonic
SweepTime          60.00640 s
TimeConst          0
TimeExp            False
TuneCaps           45
dModSW             True

*
************************************************************
