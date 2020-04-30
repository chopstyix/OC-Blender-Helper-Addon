# Octane Blender Helper Add-on
# Copyright (C) 2020 Yichen Dou
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

import bpy
from . icons import register_icons, unregister_icons
from . operators import register_operators, unregister_operators
from . menus import register_menus, unregister_menus

bl_info = {
    "name": "Octane Helper",
    "description": "A helper addon for Octane Blender edition",
    "author": "Yichen Dou",
    "version": (2, 0, 1),
    "blender": (2, 81, 0),
    "warning": "",
    "wiki_url": "https://github.com/Yichen-Dou/OC-Blender-Helper-Addon",
    "support": "COMMUNITY",
    "category": "3D View"
}

def register():
    register_icons()
    register_operators()
    register_menus()

def unregister():
    unregister_menus()
    unregister_operators()
    unregister_icons()

if __name__ == "__main__":
    register()