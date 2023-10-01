"""
FreeCAD Python script for generating a PCB bracket.

https://github.com/traintastic/pcb-bracket-generator

Copyright (C) 2023 Reinder Feenstra

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os
import Mesh


def generate_pcb_bracket(filename, pcb_width, pcb_length, pcb_thickness = 1.6, pcb_mounthole_offset = 3.81, pcb_mounthole_diameter = 3):

    CORNER_WIDTH = 1
    CORNER_HEIGHT = 5
    CORNER_LENGTH = 2 * pcb_mounthole_offset + CORNER_WIDTH

    FLOOR_THICKNESS = 1

    doc = FreeCAD.newDocument(os.path.basename(filename))

    objects = []
    cuts = []

    box = doc.addObject('Part::Box', 'floor')
    box.Height = FLOOR_THICKNESS
    box.Length = pcb_length + CORNER_WIDTH + CORNER_WIDTH
    box.Width = pcb_width + CORNER_WIDTH + CORNER_WIDTH
    objects.append(box)

    box = doc.addObject('Part::Box', 'floor_cut')
    box.Height = FLOOR_THICKNESS
    box.Length = pcb_length - 2 * (CORNER_LENGTH - CORNER_WIDTH)
    box.Width = pcb_width - 2 * (CORNER_LENGTH - CORNER_WIDTH)
    box.Placement.Base.x = CORNER_LENGTH
    box.Placement.Base.y = CORNER_LENGTH
    cuts.append(box)

    pcb = doc.addObject('Part::Box', 'pcb')
    pcb.Height = pcb_thickness
    pcb.Length = pcb_length
    pcb.Width = pcb_width
    pcb.Placement.Base.x = CORNER_WIDTH
    pcb.Placement.Base.y = CORNER_WIDTH
    pcb.Placement.Base.z = CORNER_HEIGHT - pcb_thickness
    cuts.append(pcb)

    for i in range(4):
        box = doc.addObject('Part::Box', 'block_{:d}'.format(i))
        box.Height = CORNER_HEIGHT # - pcb_thickness
        box.Length = CORNER_LENGTH
        box.Width = CORNER_LENGTH

        if i // 2 == 1:
            box.Placement.Base.x += pcb_length - CORNER_LENGTH + 2 * CORNER_WIDTH
        if i % 2 == 1:
            box.Placement.Base.y += pcb_width - CORNER_LENGTH + 2 * CORNER_WIDTH

        objects.append(box)

        cyl = doc.addObject('Part::Cylinder', 'hole_{:d}'.format(i))
        cyl.Height = box.Height
        cyl.Radius = pcb_mounthole_diameter / 2
        cyl.Placement.Base.x = CORNER_WIDTH + pcb_mounthole_offset
        cyl.Placement.Base.y = CORNER_WIDTH + pcb_mounthole_offset

        if i // 2 == 1:
            cyl.Placement.Base.x += pcb_length - 2 * pcb_mounthole_offset
        if i % 2 == 1:
            cyl.Placement.Base.y += pcb_width - 2 * pcb_mounthole_offset

        cuts.append(cyl)

    base = doc.addObject('Part::MultiFuse', 'base')
    base.Shapes = objects

    tool = doc.addObject('Part::MultiFuse', 'tool')
    tool.Shapes = cuts

    final = doc.addObject('Part::Cut', 'final')
    final.Base = base
    final.Tool = tool

    doc.recompute()

    # save as FreeCAD file:
    if os.path.exists(filename):
        os.remove(filename)
    doc.saveAs(filename)

    # export STL:
    filename_stl = os.path.splitext(filename)[0] + '.stl'
    if os.path.exists(filename_stl):
        os.remove(filename_stl)
    Mesh.export([final], filename_stl)

    # esport PNG:
    filename_png = os.path.splitext(filename)[0] + '.png'
    if os.path.exists(filename_png):
        os.remove(filename_png)
    FreeCAD.setActiveDocument(doc.Name)
    Gui.activeDocument().activeView().viewIsometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.activeDocument().activeView().saveImage(filename_png, 400, 300, 'Current')


path = os.path.dirname(__file__)

generate_pcb_bracket(os.path.join(path, 'output', 'pcb_bracket_50x60'), 50, 60)
