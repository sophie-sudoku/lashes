import maya.cmds as cmds
import importlib

class GUI(object):

    def __init__(self):
        self.approach = ""
        self.UIwindow = "UserInterface"
        self.size = (500, 400)
        self.interfaceWindowExists = True
        self.pathSelected = False
        self.pathLength = 1
        # parameter
        self.parm_bendUp = 0
        self.parm_amount = 0
        self.parm_minLength = 0
        self.parm_maxLength = 0
        self.parm_bendWhole = 0
        self.parm_scale = 0
        self.parm_randRot = 0
        self.parm_randLength = 0
        self.parm_color = 0
        self.parm_spacing = 0

    # firstWindow
    @classmethod
    def chooseApproach(cls):
        win = cls()
        win.createChooseApproachWindow()

    def createChooseApproachWindow(self):
        # ueberprueft, ob Fenster bereits existiert
        if cmds.window(self.UIwindow, exists = True):
            cmds.deleteUI(self.UIwindow)
        # window erstellen
        self.UIwindow = cmds.window(self.UIwindow, title = "Approach selection", widthHeight = self.size, mnb = False, mxb = False, sizeable = True)
        self.mainForm = cmds.columnLayout(columnAttach=('both', 0), columnWidth=self.size[0])
        # load picture : picture in folder prefs/GUI/
        imagePath = cmds.internalVar(upd = True) + "GUI/LOGO_Approaches.png"
        cmds.image(w=500, h=700, image = imagePath)
        cmds.columnLayout(columnAttach=('both', 10), columnAlign = "center", columnWidth=self.size[0], adj=True)#
        cmds.separator(h = 5, st="none")
        self.continueBtn = cmds.button(
            backgroundColor = (1,1,1),
            label='CONTINUE',
            height=30,
            width = 150,
            command=self.continueCmd
        )
        self.mainForm = cmds.columnLayout(columnAttach=('both', 0), columnWidth=self.size[0])
        cmds.showWindow(self.UIwindow)

    def continueCmd(self, *args):
        # check, if a path is selected
        self.lashesPath = cmds.ls(selection=True)
        if len(self.lashesPath) == 1:
            shape = cmds.ls(cmds.listHistory(self.lashesPath[0]))
            if self.isCurve(shape[0]):
                self.pathSelected = True
                self.pathLength = cmds.arclen(shape[0])
                print("pathlength: " + str(self.pathLength))
        if self.pathSelected:
            print("deformer approach with path-selection chosen")
            deformer = importlib.import_module("Lashes.deformerWithPath")
            self.approach = deformer.Deformer()
            cmds.deleteUI(self.UIwindow)
            self.createGUI()
            self.generateLashesTemplate()
        elif not self.pathSelected:
            print("deformer approach without path-selection chosen")
            deformer = importlib.import_module("Lashes.deformerApproach")
            self.approach = deformer.Deformer()
            cmds.deleteUI(self.UIwindow)
            self.createGUI()
            self.generateLashesTemplate()
        else:
            print("The chosen path is too short. You can scale it up during the lashes-creation, and scale it down afterwards. The size has to be over 41 due to editing of the cone-thickness, yours is " + str(self.pathLength) + " now")

    def isCurve(self, shape):
        return cmds.objExists(shape) and (cmds.objectType(shape, isType='bezierCurve') or cmds.objectType(shape, isType='nurbsCurve'))

    # secondWindow
    def createGUI(self, *args):
        cmds.cycleCheck(e=False)
        # ueberprueft, ob Fenster bereits existiert
        if cmds.window(self.UIwindow, exists = True):
            cmds.deleteUI(self.UIwindow)
        # window erstellen
        self.UIwindow = cmds.window(self.UIwindow, title = "Generating eyelashes", widthHeight = self.size, mnb = False, mxb = False, sizeable = True)
        self.mainForm = cmds.columnLayout(columnAttach=('both', 0), columnWidth=self.size[0])
        self.show_GUI_logo()
        cmds.columnLayout(columnAttach=('both', 10), columnAlign = "center", columnWidth=self.size[0])
        self.show_efficieny()
        self.show_transformations()
        if not self.pathSelected:
            self.show_animation()
        self.show_color()
        self.show_buttons()
        self.show_warning()
        cmds.showWindow(self.UIwindow)
        #createLashesTemplate()

    def show_GUI_logo(self, *args):
        # load picture : picture in folder prefs/GUI/
        imagePath = cmds.internalVar(upd = True) + "GUI/LOGO.png"
        cmds.image(w=500, h=200, image = imagePath)

    def show_efficieny(self, *args):
        cmds.separator(h = 15)
        self.transformationGrp = cmds.frameLayout(
            label='Efficieny',
            collapsable=False,
            backgroundColor = (0,0,0),
        )
        self.polyGrp = cmds.radioButtonGrp(
            label='POLY: ',
            labelArray3=[
                'low',
                'medium',
                'high'
            ],
            numberOfRadioButtons=3,
            select=1,
            changeCommand=self.changePoly
        )
        cmds.columnLayout(columnAttach=('both', 142), columnAlign = "center", columnWidth=self.size[0], adj=True)
        self.smoothness = cmds.checkBox(
            label='Smoothness',
            changeCommand=self.changeSmoothness
        )
        cmds.setParent('..')
        cmds.setParent('..')

    def show_transformations(self, *args):
        print("arclen: " + str(self.pathLength))
        cmds.separator(h = 10, style='none')
        self.transformationGrp = cmds.frameLayout(
            label='Transformations',
            collapsable=False,
            backgroundColor = (0,0,0),
        )
        if self.pathSelected:
            cmds.columnLayout(columnAttach=('both', 142), columnAlign = "center", columnWidth=self.size[0], adj=True)
            self.reverse = cmds.checkBox(
                label='Reverse',
                ann = "Reverses the direction of the path and that changes the twist of the lashes.",
                changeCommand=self.reversePath
            )
            cmds.setParent('..')
        self.distributionGrp = cmds.radioButtonGrp(
            label='Distribution: ',
            labelArray2=[
                'arc',
                'linear'
            ],
            numberOfRadioButtons=2,
            select=1,
            changeCommand=self.changeDistribution
        )
        if not self.pathSelected:
            self.scale = cmds.floatSliderGrp(
                field=True,
                label='scale',
                minValue=0.1,
                maxValue=10,
                value=1,
                ann = "Changes the scale of the lashesGroup",
                changeCommand=self.changeScale
            )
        self.lengthMin = cmds.floatSliderGrp(
            field=True,
            label='length_1',
            minValue=self.pathLength/10,
            maxValue=self.pathLength/5,
            fieldMinValue=self.pathLength/20,
            fieldMaxValue=self.pathLength,
            value=self.pathLength/7.5,
            ann = "The length for each lash is calculated depending on its position and \nthe chosen distribution to create an individual form.\n"
                  "The parameter for randomization is added to this calculation.",
            changeCommand=self.changeLength
        )
        self.lengthMax = cmds.floatSliderGrp(
            field=True,
            label='length_2',
            minValue=self.pathLength/5,
            maxValue=self.pathLength/1,
            fieldMinValue=self.pathLength/20,
            fieldMaxValue=self.pathLength,
            value=self.pathLength/2.5,
            ann = "The length for each lash is calculated depending on its position and \nthe chosen distribution to create an individual form.\n"
                  "The parameter for randomization is added to this calculation.",
            changeCommand=self.changeLength
        )
        self.amount = cmds.intSliderGrp(
            field=True,
            label='amount',
            minValue=3,
            maxValue=200,
            value=200,
            ann = "Sets the amount of the lashes.",
            changeCommand=self.changeAmount
        )
        if not self.pathSelected:
            self.bendWhole = cmds.intSliderGrp(
                field=True,
                label='bendWhole',
                minValue=-160,
                maxValue=0,
                value=-30,
                ann = "Defines the bending of the line, on which the lashes are applied.",
                changeCommand=self.changeBendWhole
            )
        self.bendUp = cmds.intSliderGrp(
            field=True,
            label='bendUp',
            minValue=-100,
            maxValue=100,
            value=50,
            ann = "Defines the bending of each lash.",
            changeCommand=self.changeBendUp
        )
        self.randRot = cmds.floatSliderGrp(
            field=True,
            label='randomizeRotation',
            minValue=0,
            maxValue=20,
            value=10,
            ann = "The randomization defines the rotation-maximum for each lash.",
            changeCommand=self.changeRandRot
        )
        self.randLength = cmds.floatSliderGrp(
            field=True,
            label='randomizeLength',
            minValue=0,
            maxValue=2,
            value=0,
            ann = "The randomization factor defines the deviation of the individual length, \ndepending on the position of the lash and the \nvalues for length_1 and length_2",
            changeCommand=self.changeRandLength
        )
        if self.pathSelected:
            self.spacing = cmds.floatSliderGrp(
                field=True,
                label='spacing',
                minValue=-self.pathLength/0.05,
                maxValue=self.pathLength/0.05,
                value=0,
                ann = "Spacing descibes the distance between the lashes, by changing the radius of each lash. \nIf smoothness is applied, the volume of the lashes decreases.\n"
                      "Therefore they do not touch anymore and to approach that, \nthe value of spacing has to be set down",
                changeCommand=self.changeSpacing
            )
        cmds.setParent('..')

    def show_animation(self, *args):
        self.transformationGrp = cmds.frameLayout(
            label='Animation',
            collapsable=False,
            backgroundColor = (0,0,0),
        )
        self.speedGrp = cmds.floatSliderGrp(
            field=True,
            label='speed',
            minValue=0,
            maxValue=10,
            value=0,
            changeCommand=self.changeAnimation
        )
        self.amplitudeGrp = cmds.intSliderGrp(
            field=True,
            label='amplitude',
            minValue=0,
            maxValue=45,
            value=0,
            changeCommand=self.changeAnimation
        )
        cmds.setParent('..')

    def show_color(self, *args):
        cmds.separator(h = 10, style='none')
        self.color = cmds.colorSliderGrp(
            label='Color: ',
            rgb=(0, 0, 0),
            ann = "Changes the color of the lashesColor material, that can be found in the Hypershade-Editor",
            changeCommand=self.changeColor
        )

    def show_buttons(self, *args):
        cmds.separator(h = 10, style='none')
        cmds.rowLayout( numberOfColumns=3)
        self.btnSize = ((self.size[0] - 30) / 3, 40)
        self.deleteBtn = cmds.button(
            backgroundColor = (1,1,1),
            label="delete lashes",
            height=self.btnSize[1],
            width = self.btnSize[0],
            command=self.deleteLashesCmd
        )
        self.applyBtn = cmds.button(
            backgroundColor = (1,1,1),
            label='Apply',
            height=self.btnSize[1],
            width = self.btnSize[0],
            command=self.applyCmd
        )
        self.applyBtn = cmds.button(
            backgroundColor = (1,1,1),
            label='Select all',
            height=self.btnSize[1],
            width = self.btnSize[0],
            command=self.selectAllCmd
        )
        cmds.setParent('..')
        cmds.separator(h = 15)

    def show_warning(self, *args):
        cmds.separator(h = 10, style='none')
        cmds.columnLayout(columnAttach=('both', 10), columnAlign = "center", columnWidth=self.size[0], adj=True)
        cmds.text(label="Maya constraints the minimum radius of each lash for automatic adjustments to 0.01.", align='center')
        cmds.text(label="In case that spacing doesn't work,try to scale up the path\nfor applying the lashes and resize lashesGroup afterwards.", align='center')
        cmds.setParent('..')

    # lashes Template
    def generateLashesTemplate(self, *args):
        amount = cmds.intSliderGrp(
                self.amount, q=True,
                value=True
            )
        self.parm_amount = amount
        minlength = cmds.floatSliderGrp(
                self.lengthMin, q=True,
                value=True
            )
        self.parm_minLength = minlength
        maxlength = cmds.floatSliderGrp(
                self.lengthMax, q=True,
                value=True
            )
        self.parm_maxLength = maxlength
        curvature_Up = cmds.intSliderGrp(
                self.bendUp, q=True,
                value=True
            )
        self.parm_bendUp = curvature_Up
        randomRot = cmds.floatSliderGrp(
                self.randRot, q=True,
                value=True
            )
        self.parm_randRot = randomRot
        randomLength = cmds.floatSliderGrp(
                self.randLength, q=True,
                value=True
            )
        self.parm_randLength = randomLength
        color = cmds.colorSliderGrp(
            self.color, q=True,
            rgbValue=True
        )
        if self.pathSelected:
            self.parm_color = color
            spacing = cmds.floatSliderGrp(
                    self.spacing, q=True,
                    value=True
                )
            self.parm_spacing = spacing
            self.approach.createLashesTemplate(amount, minlength, maxlength, curvature_Up, randomRot, randomLength, color)
            self.changePoly()
            self.changeSmoothness()
        else:
            curvature_Whole = cmds.intSliderGrp(
                    self.bendWhole, q=True,
                    value=True
                )
            self.parm_bendWhole = curvature_Whole
            scale = cmds.floatSliderGrp(
                    self.scale, q=True,
                    value=True
                )
            self.parm_scale = scale
            self.approach.createLashesTemplate(amount, minlength, maxlength, curvature_Up, curvature_Whole, randomRot,randomLength, color, scale)

    # process user commands
    def reversePath(self, *args):
        self.approach.reversePath()

    def changeLength(self, *args):
        min = cmds.floatSliderGrp(
                self.lengthMin, q=True,
                value=True
            )
        self.parm_minLength = min
        max = cmds.floatSliderGrp(
                self.lengthMax, q=True,
                value=True
            )
        self.parm_maxLength = max
        self.approach.adjustlength(self.parm_minLength, self.parm_maxLength, self.parm_randLength)

    def changeBendUp(self, *args):
        bendUp = cmds.intSliderGrp(
                self.bendUp, q=True,
                value=True
            )
        self.approach.adjustbend_Up(bendUp)

    def changeBendWhole(self, *args):
        bendWhole = cmds.intSliderGrp(
                self.bendWhole, q=True,
                value=True
            )
        self.approach.adjustbend_Whole(bendWhole)

    def changeScale(self, *args):
        scale = cmds.floatSliderGrp(
                self.scale, q=True,
                value=True
            )
        self.approach.adjustscale(scale)

    def changeRandRot(self, *args):
        random = cmds.floatSliderGrp(
                self.randRot, q=True,
                value=True
            )
        self.approach.adjustrandomRot(random)

    def changeRandLength(self, *args):
        random = cmds.floatSliderGrp(
                self.randLength, q=True,
                value=True
            )
        self.parm_randLength = random
        self.approach.adjustlength(self.parm_minLength, self.parm_maxLength, self.parm_randLength)

    def changeAmount(self, *args):
        if self.pathSelected and self.approach.getName() == "deformer":
            amount = cmds.intSliderGrp(
                self.amount, q=True,
                value=True
            )
            self.approach.adjustAmount(amount)
        else:
            self.approach.deleteLashes()
            self.generateLashesTemplate()

    def changeSpacing(self, *args):
        spacing = cmds.floatSliderGrp(
                self.spacing, q=True,
                value=True
            )
        self.parm_spacing = spacing
        self.approach.adjustspacing(self.parm_spacing)

    def changeColor(self, *args):
        color = cmds.colorSliderGrp(
            self.color, q=True,
            rgbValue=True
        )
        self.approach.adjustcolor(color)

    def changePoly(self, *args):
        quality = cmds.radioButtonGrp(
            self.polyGrp, q=True,
            select=True
        )
        self.approach.adjustPoly(quality)

    def changeSmoothness(self, *args):
        smoothness = cmds.checkBox(
                self.smoothness, q=True,
                value=True
            )
        self.approach.adjustSmoothness(smoothness)

    def changeDistribution(self, *args):
        distribution = cmds.radioButtonGrp(
            self.distributionGrp, q=True,
            select=True
        )
        self.approach.adjustDistribution(distribution)

    def changeAnimation(self, *args):
        speed = cmds.floatSliderGrp(
                self.speedGrp, q=True,
                value=True
        )
        amplitude = cmds.intSliderGrp(
                self.amplitudeGrp, q=True,
                value=True
        )
        self.approach.adjustAnimation(speed, amplitude)

    def applyCmd(self, *args):
        if self.pathSelected:
            self.approach.applyLashes()
        self.closeBtnCmd()

    def deleteLashesCmd(self, *args):
        # TODO
        self.closeBtnCmd()
        self.approach.deleteLashes()

    def closeBtnCmd(self, *args):
        self.interfaceWindowExists = False
        cmds.deleteUI(self.UIwindow, window=True)

    def selectAllCmd(self, *args):
        self.approach.selectall()


