# OC-Blender-Helper-Addon
A helper addon for Octane Blender edition

## Versions

* OctaneRender™ for Blender 2019 and later
* Current version **v1.0.0**
  * Tested on Blender_Octane_Edition_2020.1.RC3_21.5_beta (latest)

## Features

* In the object mode, we can assign octane materials to all selected objects

  ![image-20200421175448704](README.assets/image-20200421175448704.png)

* In the edit mode, we can assign octane materials to all selected faces of selected objects

  * If an object has no base material, it will create one

  ![image-20200421175938477](README.assets/image-20200421175938477.png)

* Setup the texture environment in one click

  * Modify Blender display device settings to get a correct response
  * Overwrites settings of Octane Camera Imager (recommended)
  * Add a 3D transform node to the environment texture

  ![image-20200421180047638](README.assets/image-20200421180047638.png)

  ![image-20200421180353848](README.assets/image-20200421180353848.png)

* Set specific render layer id to all selected objects

  ![image-20200421180502940](README.assets/image-20200421180502940.png)

  ![image-20200421180539851](README.assets/image-20200421180539851.png)

## Installation

* Preferences > Add-ons > Install
* Select Octane_Helper.zip to install
* Activate it

## How to use

* Pretty simple, just **right click** in the 3D viewport
* Make sure the Octane render is enabled, otherwise the menu will not show up
* It works in either object mode or edit mode, but provides different functions

## WIP

* Toggle clay mode rendering
* Popup dialog for users to change some settings when adding materials
  * e.g. RGB color and emission power of the lights
* Menu to create octane-related objects 
  * e.g. Directional light, backdrops