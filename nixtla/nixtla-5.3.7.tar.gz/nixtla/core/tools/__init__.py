# -*- coding: utf-8 -*-
'''
Created on Feb 24, 2014

This module implements several tools needed throughout the process

@author: curiel
'''

default_config_ini = '''[Modules]
TrackingModule = nixtla.tracking.interface.ITrackingModule
SegmentationModule = nixtla.segmentation.interface.ISegmentationModule  
ModellingModule = nixtla.modelling.interface.IModellingModule
VerificationModule = nixtla.verification.interface.IVerificationModule

[Pipeline]
workflow = [(TrackingModule, SegmentationModule), 
            (SegmentationModule, ModellingModule),
            (ModellingModule, VerificationModule)]
entry_module = TrackingModule
annotator = nixtla.core.annotation.elan.ElanAnnotation
results_file_path = ~/results.eaf
annotation_video_path = ./res/SignerA.mp4

[TrackingModule]
implementedBy =  nixtla.tracking.text_based.implementation.TrackingModule
#tracking_files = [./res/TrackingResultA.txt,
#                             ./res/TrackingResultB.txt]
tracking_files = [./res/TrackingResultA.txt]
raw_video_file = ./res/SignerA.mp4
corpus_processing_class = nixtla.core.tools.corpora.dictasign.DictaSignSpecific
rounded = True

[SegmentationModule]
implementedBy =  nixtla.segmentation.handspeed_based.implementation.SegmentationModule
analysis_window = 5

# With respect to which articulators we are cutting segments
articulators = [right_hand, left_hand]

# Speed threshold to use in segmentation
#speed_threshold = 6.0
speed_threshold = 1.86

# maximum noise level of tracker 1.0
noise_threshold = 0.5 
small_movement_threshold = 3.0

# Calculated on a long movement
long_threshold = 9.0 

# Calculated on a fast, short movement
short_threshold = 16.0 

# Between noise_threshold and long_threshold, 
# movements can have intention or not, so we can try to see them
# as trills or else use knowledge to discard them.

[ModellingModule]
implementedBy =  nixtla.modelling.channel_based.implementation.ModellingModule
history_verification_length = 30

# We will create histories for each articulator of interest
articulators = [right_hand, left_hand]
ruleset = ./res/rules.ini

[VerificationModule]
implementedBy =  nixtla.verification.simple_method.implementation.VerificationModule'''

default_database_ini = '''# Created on Nov 17, 2014
# @author: Arturo CURIEL

# Each articulator automatically transforms into an alias for
# "True" on postures, and generates aliases to describe 
# "any" movement.
KEYPOSTURE = right_hand || left_hand
TRANSITION = right_hand_movement ^ left_hand_movement

BOTH = right_hand & left_hand

# We can use any rule defined on the rules.ini file
TOUCHING = left_hand touches right_hand || right_hand touches left_hand
RIGHT_NEUTRAL =  right_hand located in NEUTRAL

# We can combine previously defined terms
NOTOUCHING = ~TOUCHING

JOINING = NOTOUCHING & [TRANSITION](TOUCHING)
SEPARATING = TOUCHING & [TRANSITION](NOTOUCHING)

TAP = [JOINING](SEPARATING)'''

default_rules_ini = '''# Created on Nov 16, 2014
# @author: Arturo CURIEL

[Global]
# Aliases for articulators
articulator = [right_hand, left_hand, head]

# Aliases for directions
direction = [LEFT, UP_LEFT, UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT]

# Aliases for regions
region = [UPPER, LOWER, RSIDE, NEUTRAL, TORSO, LSIDE]

# Rules to be used in key postures
[Posture]
$articulator touches $articulator = nixtla.rulesets.hands_2d_only.touches.Touches
$articulator located in $region =  nixtla.rulesets.hands_2d_only.located_in.LocatedIn
$articulator lies in direction $direction with respect to $articulator = nixtla.rulesets.hands_2d_only.lies_in.LiesIn

# Rules to be used in transitions
[Transition]
$articulator moves towards $direction = nixtla.rulesets.hands_2d_only.moves_to.MovesTo
$articulator rotates = nixtla.rulesets.hands_2d_only.rotates.Rotates
$articulator rotates clockwise = nixtla.rulesets.hands_2d_only.rotates_cl.RotatesClockwise
$articulator rotates counter clockwise = nixtla.rulesets.hands_2d_only.rotates_co.RotatesCounterclockwise
$articulator trills = nixtla.rulesets.hands_2d_only.trills.Trills

# Formulae to satisfy. We can either describe everything here or call
# an external database file.
[Formulae]
database_file = ./res/database.ini'''