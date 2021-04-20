# File: newtons_cradle.py
# Auth: Joe Broesele
# Mod.: Joe Broesele
# Date: 17 Apr 2021
# Rev.: 21 Apr 2021
#
# Blender add-on to create a Newton's cradle model.
#
# This code is based on the Harmonograph addon:
# https://blenderartists.org/t/harmonograph-addon/696171
# Thanks a lot to the author!
#
#
#
# Copyright (C) 2021 Joe Broesele
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#



bl_info = {
    "name": "Newton's Cradle",
    "description": "Creates a Newton's cradle model.",
    "author": "Joe Broesele",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Object"
}



import bpy
import math
import mathutils



class NewtonsCradle(bpy.types.Operator):
    """Newton's Cradle"""                   # Tooltip.
    bl_idname = "object.newtons_cradle"     # Unique identifier for buttons and menu items to reference.
    bl_label = "Newton's Cradle"            # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}

    ballCount                           = bpy.props.IntProperty(name="Ball Count", default=5, min=3, max=10)
    ballStartAngle                      = bpy.props.FloatProperty(name="Ball Angle at Start", default=45.00, min=0.00, max=180.00)
    # Ball body properties.
    ballBodyPrefix                      = bpy.props.StringProperty(name="Ball Prefix", default="BallBody")
    ballBodyDiameter                    = bpy.props.FloatProperty(name="Ball Diameter", default=1.00, min=0.01, max=10.00)
    ballBodyMass                        = bpy.props.FloatProperty(name="Ball Mass", default=50.00, min=0.01, max=100.00)
    ballBodyFriction                    = bpy.props.FloatProperty(name="Ball Friction", default=1.00, min=0.01, max=2.00)
    ballBodyBounciness                  = bpy.props.FloatProperty(name="Ball Bounciness", default=0.98, min=0.01, max=1.00)
    ballBodySegments                    = 32
    ballBodyRingCount                   = 16
    ballBodySubdivisionSurfaceViewport  = bpy.props.IntProperty(name="Ball Subdivision Surface Viewport", default=1, min=0, max=5)
    ballBodySubdivisionSurfaceRender    = bpy.props.IntProperty(name="Ball Subdivision Surface Render", default=2, min=0, max=5)
    ballBodyIndividualMaterial          = bpy.props.BoolProperty(name="Individual Material for Balls", default=False)
    # Ball suspension properties.
    ballSuspensionPrefix                = bpy.props.StringProperty(name="Ball Suspension Prefix", default="BallSuspension")
    ballSuspensionDiameter              = bpy.props.FloatProperty(name="Ball Suspension Diameter", default=0.05, min=0.01, max=1.00)
    ballSuspensionLength                = bpy.props.FloatProperty(name="Ball Suspension Length", default=0.10, min=0.01, max=1.00)
    ballSuspensionVertices              = 32
    ballSuspensionIndividualMaterial    = bpy.props.BoolProperty(name="Individual Material for Ball Suspensions", default=False)
    # Ball wire properties.
    ballWirePrefix                      = bpy.props.StringProperty(name="Ball Wire Prefix", default="BallWire")
    ballWireThickness                   = bpy.props.FloatProperty(name="Ball Wire Thickness", default=0.025, min=0.001, max=1.000)
    ballWireIndividualMaterial          = bpy.props.BoolProperty(name="Individual Material for Ball Wires", default=False)
    # Ball hinge properties.
    ballHingePrefix                     = bpy.props.StringProperty(name="Ball Hinge Prefix", default="BallHinge")
    # Frame properties.
    framePrefix                         = bpy.props.StringProperty(name="Frame Prefix", default="Frame")
    frameThickness                      = bpy.props.FloatProperty(name="Frame Thickness", default=0.20, min=0.01, max=1.00)
    frameLengthExtra                    = bpy.props.FloatProperty(name="Frame Extra Length", default=0.50, min=0.01, max=10.00)
    frameWidth                          = bpy.props.FloatProperty(name="Frame Width", default=5.00, min=0.01, max=10.00)
    frameHeigtBelowBalls                = bpy.props.FloatProperty(name="Frame Height BelowBalls", default=1.00, min=0.01, max=10.00)
    frameHeigtAboveBalls                = bpy.props.FloatProperty(name="Frame Height Above Balls", default=3.00, min=0.01, max=10.00)
    frameCornerRadius                   = bpy.props.FloatProperty(name="Frame Corner Radius", default=0.50, min=0.01, max=5.00)



    def execute(self, context):
        # Create a new collaction.
        collection = bpy.data.collections.new('Newton\'s Cardle')   # Create a new collection.
        bpy.context.scene.collection.children.link(collection)      # Add the collection to the scene collection.
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]  # Set the new collection as active.

        # Create the support frame.
        self.create_frame()

        # Create the balls.
        for ballNum in range(self.ballCount):
            self.create_ball(ballNum, ((ballNum - float((self.ballCount - 1) / 2)) * self.ballBodyDiameter, 0, self.frameHeigtBelowBalls))

        # Define the materials.
        self.materials_define()

        # Set the initial condition.
        bpy.ops.object.select_all(action='DESELECT')
        ballHingeArrowsName = self.ballHingePrefix + 'Arrow_{0:02d}'.format(1)
        self.rotate_object(bpy.data.objects[ballHingeArrowsName], self.ballStartAngle, 'Z')

        return {'FINISHED'}



    def create_frame(self):
        '''Create the frame for hanging the balls.'''
        bpy.ops.curve.primitive_nurbs_path_add()            # Create default path.
        bpy.ops.object.editmode_toggle()                    # Switch to edit mode.
        bpy.ops.curve.select_all(action='SELECT')           # Select the entire path.
        bpy.ops.curve.delete()                              # Delete the path.
        # Calculate corner coordinates.
        ballRowLength = self.ballCount * self.ballBodyDiameter
        frameCornerFrontLowerLeft1 = (((ballRowLength + self.frameLengthExtra) / 2) + self.frameCornerRadius, self.frameWidth / 2 - self.frameCornerRadius, 0)
        frameCornerFrontLowerLeft2 = (((ballRowLength + self.frameLengthExtra) / 2) + self.frameCornerRadius, self.frameWidth / 2, self.frameCornerRadius)
        frameCornerFrontUpperLeft1 = (((ballRowLength + self.frameLengthExtra) / 2) + self.frameCornerRadius, self.frameWidth / 2, self.frameHeigtBelowBalls + self.frameHeigtAboveBalls - self.frameCornerRadius)
        frameCornerFrontUpperLeft2 = (((ballRowLength + self.frameLengthExtra) / 2), self.frameWidth / 2, self.frameHeigtBelowBalls + self.frameHeigtAboveBalls)
        frameCornerFrontUpperRight1 = (-frameCornerFrontUpperLeft2[0], frameCornerFrontUpperLeft2[1], frameCornerFrontUpperLeft2[2])
        frameCornerFrontUpperRight2 = (-frameCornerFrontUpperLeft1[0], frameCornerFrontUpperLeft1[1], frameCornerFrontUpperLeft1[2])
        frameCornerFrontLowerRight1 = (-frameCornerFrontLowerLeft2[0], frameCornerFrontLowerLeft2[1], frameCornerFrontLowerLeft2[2])
        frameCornerFrontLowerRight2 = (-frameCornerFrontLowerLeft1[0], frameCornerFrontLowerLeft1[1], frameCornerFrontLowerLeft1[2])
        frameCornerBackLowerRight1 = (frameCornerFrontLowerRight2[0], -frameCornerFrontLowerRight2[1], frameCornerFrontLowerRight2[2])
        frameCornerBackLowerRight2 = (frameCornerFrontLowerRight1[0], -frameCornerFrontLowerRight1[1], frameCornerFrontLowerRight1[2])
        frameCornerBackUpperRight1 = (frameCornerFrontUpperRight2[0], -frameCornerFrontUpperRight2[1], frameCornerFrontUpperRight2[2])
        frameCornerBackUpperRight2 = (frameCornerFrontUpperRight1[0], -frameCornerFrontUpperRight1[1], frameCornerFrontUpperRight1[2])
        frameCornerBackUpperLeft1 = (frameCornerFrontUpperLeft2[0], -frameCornerFrontUpperLeft2[1], frameCornerFrontUpperLeft2[2])
        frameCornerBackUpperLeft2 = (frameCornerFrontUpperLeft1[0], -frameCornerFrontUpperLeft1[1], frameCornerFrontUpperLeft1[2])
        frameCornerBackLowerLeft1 = (frameCornerFrontLowerLeft2[0], -frameCornerFrontLowerLeft2[1], frameCornerFrontLowerLeft2[2])
        frameCornerBackLowerLeft2 = (frameCornerFrontLowerLeft1[0], -frameCornerFrontLowerLeft1[1], frameCornerFrontLowerLeft1[2])
        # Add the frame points.
        bpy.ops.curve.vertex_add(location = frameCornerFrontLowerLeft1)
        bpy.ops.curve.vertex_add(location = frameCornerFrontLowerLeft2)
        bpy.ops.curve.vertex_add(location = frameCornerFrontUpperLeft1)
        bpy.ops.curve.vertex_add(location = frameCornerFrontUpperLeft2)
        bpy.ops.curve.vertex_add(location = frameCornerFrontUpperRight1)
        bpy.ops.curve.vertex_add(location = frameCornerFrontUpperRight2)
        bpy.ops.curve.vertex_add(location = frameCornerFrontLowerRight1)
        bpy.ops.curve.vertex_add(location = frameCornerFrontLowerRight2)
        bpy.ops.curve.vertex_add(location = frameCornerBackLowerRight1)
        bpy.ops.curve.vertex_add(location = frameCornerBackLowerRight2)
        bpy.ops.curve.vertex_add(location = frameCornerBackUpperRight1)
        bpy.ops.curve.vertex_add(location = frameCornerBackUpperRight2)
        bpy.ops.curve.vertex_add(location = frameCornerBackUpperLeft1)
        bpy.ops.curve.vertex_add(location = frameCornerBackUpperLeft2)
        bpy.ops.curve.vertex_add(location = frameCornerBackLowerLeft1)
        bpy.ops.curve.vertex_add(location = frameCornerBackLowerLeft2)
        # Set properties of the curve representing the frame.
        bpy.ops.curve.select_all(action='SELECT')           # Select all vertices.
        bpy.ops.curve.cyclic_toggle()                       # Make active spline closed loop.
        bpy.ops.curve.spline_type_set(type='BEZIER')        # Set the curve type to bezier.
        bpy.ops.object.editmode_toggle()                    # Return the scene to object mode.
        frameName = self.framePrefix
        bpy.context.active_object.name = frameName
        # Fix handles.
        # For the formula of the handle length see here:
        # https://stackoverflow.com/questions/1734745/how-to-create-circle-with-b%C3%A9zier-curves
        handleVectorLength = (4 / 3) * math.tan(math.pi / (2 * 4)) * self.frameCornerRadius
        # Loop over all vertices.
        for bezierPoint in bpy.data.objects[frameName].data.splines[0].bezier_points:
            bezierPoint.handle_left_type = 'FREE'
            bezierPoint.handle_right_type = 'FREE'
            # Lower vertices. => Set their handles parallel to the y-axis.
            if bezierPoint.co[2] == frameCornerFrontLowerLeft1[2]:
                if bezierPoint.co[1] < bezierPoint.handle_left[1]:
                    bezierPoint.handle_left  = bezierPoint.co + mathutils.Vector((0,  handleVectorLength, 0))
                    bezierPoint.handle_right = bezierPoint.co + mathutils.Vector((0, -handleVectorLength, 0))
                else:
                    bezierPoint.handle_left  = bezierPoint.co + mathutils.Vector((0, -handleVectorLength, 0))
                    bezierPoint.handle_right = bezierPoint.co + mathutils.Vector((0,  handleVectorLength, 0))
            # Middle vertices. => Set their handles parallel to the z-axis.
            elif bezierPoint.co[2] == frameCornerFrontLowerLeft2[2] or bezierPoint.co[2] == frameCornerFrontUpperLeft1[2]:
                if bezierPoint.co[2] < bezierPoint.handle_left[2]:
                    bezierPoint.handle_left  = bezierPoint.co + mathutils.Vector((0, 0,  handleVectorLength))
                    bezierPoint.handle_right = bezierPoint.co + mathutils.Vector((0, 0, -handleVectorLength))
                else:
                    bezierPoint.handle_left  = bezierPoint.co + mathutils.Vector((0, 0, -handleVectorLength))
                    bezierPoint.handle_right = bezierPoint.co + mathutils.Vector((0, 0,  handleVectorLength))
            # Upper vertices. => Set their handles parallel to the x-axis.
            elif bezierPoint.co[2] == frameCornerFrontUpperLeft2[2]:
                if bezierPoint.co[0] < bezierPoint.handle_left[0]:
                    bezierPoint.handle_left  = bezierPoint.co + mathutils.Vector(( handleVectorLength, 0, 0))
                    bezierPoint.handle_right = bezierPoint.co + mathutils.Vector((-handleVectorLength, 0, 0))
                else:
                    bezierPoint.handle_left  = bezierPoint.co + mathutils.Vector((-handleVectorLength, 0, 0))
                    bezierPoint.handle_right = bezierPoint.co + mathutils.Vector(( handleVectorLength, 0, 0))
            # All other vertices. There should be none of them! => In case there are some, set their handles to zero.
            else:
                bezierPoint.handle_left = bezierPoint.co + mathutils.Vector((0, 0, 0))
                bezierPoint.handle_right = bezierPoint.co + mathutils.Vector((0, 0, 0))
        # Set frame properties.
        bpy.data.objects[frameName].data.bevel_depth = self.frameThickness / 2
        # Add material to the frame.
        frameMaterialName = 'Material_' + self.framePrefix
        frameMaterial = bpy.data.materials.get(frameMaterialName)
        if frameMaterial is None:
            frameMaterial = bpy.data.materials.new(name=frameMaterialName)
        bpy.data.objects[frameName].data.materials.append(frameMaterial)



    def create_ball(self, ballNum, ballLocation):
        '''Create a ball with suspension, wires and a hinge.'''
        # Create ball body.
        bpy.ops.mesh.primitive_uv_sphere_add(location   = ballLocation,
                                             segments   = self.ballBodySegments,
                                             ring_count = self.ballBodyRingCount,
                                             radius     = float(self.ballBodyDiameter / 2))
        ballBodyName = self.ballBodyPrefix + '_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballBodyName
        ballBodyModifier = bpy.data.objects[ballBodyName].modifiers.new(name='{0:s} - Subdivision Surface'.format(ballBodyName), type='SUBSURF')
        ballBodyModifier.levels =self.ballBodySubdivisionSurfaceViewport
        ballBodyModifier.render_levels = self.ballBodySubdivisionSurfaceRender
        # Set smooth shading mode for the ball body.
        bpy.data.objects[ballBodyName].data.polygons.foreach_set('use_smooth',  [True] * len(bpy.data.objects[ballBodyName].data.polygons))
        bpy.data.objects[ballBodyName].data.update()
        # Add material to the ball body.
        ballBodyMaterialName = 'Material_' + self.ballBodyPrefix
        if self.ballBodyIndividualMaterial:
            ballBodyMaterialName += '_{0:02d}'.format(ballNum + 1)
        ballBodyMaterial = bpy.data.materials.get(ballBodyMaterialName)
        if ballBodyMaterial is None:
            ballBodyMaterial = bpy.data.materials.new(name=ballBodyMaterialName)
        bpy.data.objects[ballBodyName].data.materials.append(ballBodyMaterial)
        # Add rigid body constraints to the ball body.
        bpy.ops.object.select_all(action='DESELECT')        # Deselect all objects.
        bpy.data.objects[ballBodyName].select_set(True)     # Select to ball body.
        bpy.ops.rigidbody.objects_add()                     # Add the rigid body constraint to the ball body.
        bpy.data.objects[ballBodyName].rigid_body.friction          = self.ballBodyFriction
        bpy.data.objects[ballBodyName].rigid_body.restitution       = self.ballBodyBounciness   # Bounciness.
        bpy.data.objects[ballBodyName].rigid_body.mass              = self.ballBodyMass
        bpy.data.objects[ballBodyName].rigid_body.collision_margin  = 0.0
        bpy.data.objects[ballBodyName].rigid_body.collision_shape   = 'MESH'
        bpy.data.objects[ballBodyName].rigid_body.mesh_source       = 'FINAL'
        bpy.data.objects[ballBodyName].rigid_body.type              = 'ACTIVE'

        # Create the ball suspension.
        ballSuspensionLocation = (ballLocation[0], ballLocation[1], ballLocation[2] + float(self.ballBodyDiameter / 2 + self.ballSuspensionDiameter / 2 * 0.7))
        bpy.ops.mesh.primitive_cylinder_add(location    = ballSuspensionLocation,
                                            rotation    = (math.radians(90), 0, 0),
                                            vertices    = self.ballSuspensionVertices,
                                            radius      = float(self.ballSuspensionDiameter / 2),
                                            depth       = self.ballSuspensionLength)
        ballSuspensionName = self.ballSuspensionPrefix + '_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballSuspensionName
        # Set smooth shading mode for the ball suspension.
        for ballSuspensionFace in bpy.data.objects[ballSuspensionName].data.polygons:
            # Exclude the cylinder covers.
            print(ballSuspensionFace.center)
            if ballSuspensionFace.center[2] == 0:
                ballSuspensionFace.use_smooth = True
        bpy.data.objects[ballSuspensionName].data.update()
        # Add material to the ball suspension.
        ballSuspensionMaterialName = 'Material_' + self.ballSuspensionPrefix
        if self.ballSuspensionIndividualMaterial:
            ballSuspensionMaterialName += '_{0:02d}'.format(ballNum + 1)
        ballSuspensionMaterial = bpy.data.materials.get(ballSuspensionMaterialName)
        if ballSuspensionMaterial is None:
            ballSuspensionMaterial = bpy.data.materials.new(name=ballSuspensionMaterialName)
        bpy.data.objects[ballSuspensionName].data.materials.append(ballSuspensionMaterial)
        # Parent the ball suspension to the ball body.
        bpy.data.objects[ballSuspensionName].parent = bpy.data.objects[ballBodyName]
        bpy.data.objects[ballSuspensionName].matrix_parent_inverse = bpy.data.objects[ballBodyName].matrix_world.inverted()

        # Create hinge for the ball.
        # Set the hinge in the middle of the torus body of the wire fixation .
        frameCenterToBallSupportY = self.frameWidth / 2 - (ballSuspensionLocation[1] + self.ballSuspensionLength / 2)
        frameCenterToBallSupportZ = self.frameHeigtBelowBalls + self.frameHeigtAboveBalls - ballSuspensionLocation[2]
        frameCenterToBallSupportLength = math.sqrt((frameCenterToBallSupportY ** 2) + (frameCenterToBallSupportZ ** 2))
        frameCenterToBallSupportDeltaLength = self.frameThickness / 2 + self.ballWireThickness / 2
        frameCenterToBallSupportDeltaY = (frameCenterToBallSupportDeltaLength / frameCenterToBallSupportLength) * frameCenterToBallSupportY
        frameCenterToBallSupportDeltaZ = (frameCenterToBallSupportDeltaLength / frameCenterToBallSupportLength) * frameCenterToBallSupportZ
        ballHingeLocation = (ballLocation[0],
                             ballLocation[1] + self.frameWidth / 2 - frameCenterToBallSupportDeltaY,
                             ballLocation[2] + self.frameHeigtAboveBalls - frameCenterToBallSupportDeltaZ)
        # Cube for fixing the ball.
        bpy.ops.mesh.primitive_cube_add(location    = ballHingeLocation,
                                        size        = 0.1 * self.frameThickness)
        ballHingeCubeName = self.ballHingePrefix + 'Cube_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballHingeCubeName
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[ballHingeCubeName].select_set(True)
        bpy.ops.rigidbody.objects_add()
        bpy.data.objects[ballHingeCubeName].rigid_body.type = 'PASSIVE'
        bpy.data.objects[ballHingeCubeName].hide_viewport = True
        bpy.data.objects[ballHingeCubeName].hide_render = True
        # Arrows as hinge for the ball.
        bpy.ops.object.empty_add(type       ='ARROWS',
                                 location   = ballHingeLocation,
                                 rotation   = (0, math.radians(90), math.radians(90)))
        ballHingeArrowsName = self.ballHingePrefix + 'Arrow_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballHingeArrowsName
        bpy.ops.rigidbody.constraint_add(type='HINGE')      # Add rigid body constraint of type 'HINGE'.
        bpy.data.objects[ballHingeArrowsName].rigid_body_constraint.object1 = bpy.data.objects[ballBodyName]
        bpy.data.objects[ballHingeArrowsName].rigid_body_constraint.object2 = bpy.data.objects[ballHingeCubeName]
#        bpy.data.objects[ballHingeArrowsName].hide_viewport = True
        bpy.data.objects[ballHingeArrowsName].hide_render = True
        # Parent the ball body to the hinge arrows.
        bpy.data.objects[ballBodyName].parent = bpy.data.objects[ballHingeArrowsName]
        bpy.data.objects[ballBodyName].matrix_parent_inverse = bpy.data.objects[ballHingeArrowsName].matrix_world.inverted()

        # Create wires to hang the ball.
        # Wire.
        ballWireVertex1 = ballHingeLocation
        ballWireVertex2 = (ballSuspensionLocation[0], ballSuspensionLocation[1] + 0.6 * self.ballSuspensionLength, ballSuspensionLocation[2] + 0.1 * self.ballSuspensionDiameter)
        ballWireVertex3 = ballSuspensionLocation
        ballWireVertex4 = (ballWireVertex2[0], -ballWireVertex2[1], ballWireVertex2[2])
        ballWireVertex5 = (ballWireVertex1[0], -ballWireVertex1[1], ballWireVertex1[2])
        bpy.ops.curve.primitive_nurbs_path_add(location = ballLocation) # Create default path.
        bpy.ops.object.editmode_toggle()                    # Switch to edit mode.
        bpy.ops.curve.select_all(action='SELECT')           # Select the entire path.
        bpy.ops.curve.delete()                              # Delete the path.
        bpy.ops.curve.vertex_add(location = ballWireVertex1)
        bpy.ops.curve.vertex_add(location = ballWireVertex2)
        bpy.ops.curve.vertex_add(location = ballWireVertex3)
        bpy.ops.curve.vertex_add(location = ballWireVertex4)
        bpy.ops.curve.vertex_add(location = ballWireVertex5)
        bpy.ops.object.editmode_toggle()                    # Return the scene to object mode.
        ballWireName = self.ballWirePrefix + 'Wire_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballWireName
        bpy.data.objects[ballWireName].data.bevel_depth      = self.ballWireThickness / 2
        bpy.data.objects[ballWireName].data.bevel_mode       = 'ROUND'
        bpy.data.objects[ballWireName].data.bevel_resolution = 20
        # Wire fixations at the frame.
        ballWireFixation1Location = (ballLocation[0], ballLocation[1] + self.frameWidth / 2, ballLocation[2] + self.frameHeigtAboveBalls)
        bpy.ops.mesh.primitive_torus_add(location     = ballWireFixation1Location,
                                         rotation     = (0, math.radians(90), 0),
                                         major_radius = self.frameThickness / 2 + self.ballWireThickness / 2,
                                         minor_radius = self.ballWireThickness / 2)
        ballWireFixation1Name = self.ballWirePrefix + 'WireFixation1_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballWireFixation1Name
        ballWireFixation2Location = (ballWireFixation1Location[0], -ballWireFixation1Location[1], ballWireFixation1Location[2])
        bpy.ops.mesh.primitive_torus_add(location     = ballWireFixation2Location,
                                         rotation     = (0, math.radians(90), 0),
                                         major_radius = self.frameThickness / 2 + self.ballWireThickness / 2,
                                         minor_radius = self.ballWireThickness / 2)
        ballWireFixation2Name = self.ballWirePrefix + 'WireFixation2_{0:02d}'.format(ballNum + 1)
        bpy.context.active_object.name = ballWireFixation2Name
        # Add material to the ball wire and the ball wire fixation.
        ballWireMaterialName = 'Material_' + self.ballWirePrefix
        if self.ballWireIndividualMaterial:
            ballWireMaterialName += '_{0:02d}'.format(ballNum + 1)
        ballWireMaterial = bpy.data.materials.get(ballWireMaterialName)
        if ballWireMaterial is None:
            ballWireMaterial = bpy.data.materials.new(name=ballWireMaterialName)
        bpy.data.objects[ballWireName].data.materials.append(ballWireMaterial)
        bpy.data.objects[ballWireFixation1Name].data.materials.append(ballWireMaterial)
        bpy.data.objects[ballWireFixation2Name].data.materials.append(ballWireMaterial)
        # Parent the ball wire to the ball body.
        bpy.data.objects[ballWireName].parent = bpy.data.objects[ballBodyName]
        bpy.data.objects[ballWireName].matrix_parent_inverse = bpy.data.objects[ballBodyName].matrix_world.inverted()



    def materials_define(self):
        '''Define the materials.'''
        for ballNum in range(self.ballCount):
            # Ball body material.
            ballBodyMaterialName = 'Material_' + self.ballBodyPrefix
            if self.ballBodyIndividualMaterial:
                ballBodyMaterialName += '_{0:02d}'.format(ballNum + 1)
            ballBodyMaterial = bpy.data.materials.get(ballBodyMaterialName)
            if ballBodyMaterial is not None:
                ballBodyMaterial.diffuse_color              = (0.00, 0.00, 1.00, 1.0)   # R, G, B, A
                ballBodyMaterial.roughness                  = 0.5
                ballBodyMaterial.specular_intensity         = 0.5
            # Ball suspension material.
            ballSuspensionMaterialName = 'Material_' + self.ballSuspensionPrefix
            if self.ballSuspensionIndividualMaterial:
                ballSuspensionMaterialName += '_{0:02d}'.format(ballNum + 1)
            ballSuspensionMaterial = bpy.data.materials.get(ballSuspensionMaterialName)
            if ballSuspensionMaterial is not None:
                ballSuspensionMaterial.diffuse_color        = (0.00, 1.00, 0.00, 1.0)   # R, G, B, A
                ballSuspensionMaterial.roughness            = 0.5
                ballSuspensionMaterial.specular_intensity   = 0.5
            # Ball wire material.
            ballWireMaterialName = 'Material_' + self.ballWirePrefix
            if self.ballWireIndividualMaterial:
                ballWireMaterialName += '_{0:02d}'.format(ballNum + 1)
            ballWireMaterial = bpy.data.materials.get(ballWireMaterialName)
            if ballWireMaterial is not None:
                ballWireMaterial.diffuse_color              = (1.00, 0.65, 0.00, 1.0)   # R, G, B, A
                ballWireMaterial.roughness                  = 0.5
                ballWireMaterial.specular_intensity         = 0.0
            # Ball body material.
            frameMaterialName = 'Material_' + self.framePrefix
            frameMaterial = bpy.data.materials.get(frameMaterialName)
            if frameMaterial is not None:
                frameMaterial.diffuse_color                 = (0.40, 0.40, 0.40, 1.0)   # R, G, B, A
                frameMaterial.roughness                     = 0.5
                frameMaterial.specular_intensity            = 0.5



    def rotate_object(self, obj, angleDegrees, axis='Z'):
        '''Rotates an object.'''
        # Found here: https://blender.stackexchange.com/questions/44760/rotate-objects-around-their-origin-along-a-global-axis-scripted-without-bpy-op
        import math
        import mathutils
        # Local rotation about axis.
        obj.rotation_euler = (obj.rotation_euler.to_matrix() @ mathutils.Matrix.Rotation(math.radians(angleDegrees), 3, axis)).to_euler()



# Store keymaps here to access after registration.
addon_keymaps = []



def menu_func(self, context):
    self.layout.operator(NewtonsCradle.bl_idname)



def register():
    bpy.utils.register_class(NewtonsCradle)
    bpy.types.VIEW3D_MT_object.append(menu_func)



def unregister():
    bpy.utils.unregister_class(NewtonsCradle)
    bpy.types.VIEW3D_MT_object.remove(menu_func)



if __name__ == "__main__":
    register()

