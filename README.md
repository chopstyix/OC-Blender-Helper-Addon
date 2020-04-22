# OC-Blender-Helper-Addon
A helper addon for Octane Blender edition

## Versions

* OctaneRender™ for Blender 2019 and later
* Current version **v1.2.1**
  * Tested on Blender_Octane_Edition_2020.1.RC3_21.5_beta (latest)

## Features

* In object mode, we can assign octane materials to all selected objects

  ![image-20200422132030146](README.assets/image-20200422132030146.png)

* In edit mode, we can assign octane materials to all selected faces of selected objects

  * If an object has no base material, it will create one

  ![image-20200422131952257](README.assets/image-20200422131952257.png)

* In either object or edit mode, we can copy an active material from one object, and paste it to all other selected objects

  ![image-20200422132118537](README.assets/image-20200422132118537.png)

* We can search a material and assign it to all selected objects or faces

  ![image-20200422132420426](README.assets/image-20200422132420426.png)

* Support emissive material

  ![image-20200421222947085](README.assets/image-20200421222947085.png)

* Setup texture environment in one click

  * Overwrite option
    * Modifies Blender display device settings to get a correct response
    * Set hdri image's gamma to 1.0
    * Overwrites settings of Octane Camera Imager
    * Adds a 3D transform node to the environment texture
  * Backplate and backplate color option
    * Replace visible environment with a RGB color

  ![image-20200422132605979](README.assets/image-20200422132605979.png)

  ![image-20200421222231259](README.assets/image-20200421222231259.png)

* Transform existing texture environment dynamically

  * Make sure you have a 3D transform node connected to the graph

  ![image-20200422132740312](README.assets/image-20200422132740312.png)
  
  ![image-20200422132833253](README.assets/image-20200422132833253.png)
  
* Set specific render layer id to all selected objects

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
* Menu to create octane-related objects 
  * e.g. Directional light, backdrops