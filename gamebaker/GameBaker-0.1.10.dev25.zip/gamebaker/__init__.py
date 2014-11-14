"""
Introduction
============

GameBaker is a high level framework for making games and simulations based on Pygame.

These are the main features that have so far been implemented:

- creation of classes for game objects
- drawing of objects
- tick event
- some keyboard event detection
- script to create a new project
- classes to represent levels of a game
- classes to represent views of areas of a level
    
These are the features that will be implemented shortly:

- mouse events
- collision detection
- sound effects
- complete keyboard event detection
- developer defined events
- building games into single files
    
These are the features that will be implemented eventually:

- library functions for GUIs, physics and other areas
- networked games
    
Other features (for instance, building games to target platforms such as javascript) may also be added.


Structure of a game project
===========================

To begin creating a game, create a directory you want the project to be, navigate to that directory in the command line, and run the command ``newproject``.
For example::
    
    $ mkdir my_first_game
    $ cd my_first_game
    $ newproject
    
This will create a structure as below::

    my_first_game/
        images/
        blueprints.py
        levels.py
        settings.py
        game.py
        
The ``images`` folder should contain images you want to use in the game.
Subdirectories can be used to organise it.

The file ``blueprints.py`` contains the classes that represent game objects.
For instance, in a platform game, it might look like this::

    from gamebaker.classes import Blueprint, Sprite
    
    class Block(Blueprint):
        sprite = Sprite("objects/block.png")
    
    class Entity(Blueprint):
        def __init__(self, x, y):
            self.health = 100
            super().__init__(x, y)
            
        def tick(self):
            self.apply_gravity()
            self.apply_friction()
            if self.health <= 0:
                self.die()
                
    class Enemy(Entity):
        sprite = Sprite("characters/enemy.png")
        
        def collision(self, other):
            if isinstance(other, Player):
                other.health -= 10
                
    ...
    

The file ``levels.py`` contains the levels in the game.
It could look like this::

    from random import randint
    from gamebaker.classes import Level, View
    from blueprints import *

    levels = [Level([Block(x, y) for x in range(100) for y in range(80, 100)] + [Player(20, 80)],
                    [View(0, 0, 640, 480, 160, 0, 0)]),
              Level([Block(x, y) for x in range(100) for y in range(80, 100)] + [Player(20, 80)] + [Enemy(randint(0, 100) for _ in range(5)],
                    [View(0, 0, 640, 480, 160, 0, 0)]),
              Level([Block(x, y) for x in range(100) for y in range(80, 100)] + [Player(20, 80)] + [Enemy(randint(0, 100) for _ in range(50)],
                    [View(0, 0, 640, 480, 160, 0, 0)]),]

It must contain a list of ``Level`` objects assigned to the global variable ``levels``. 
            
            
The file ``settings.py`` contains game settings, such as the dimensions of the window, and the maximum FPS (frames per second).
It could look like this::

    from gamebaker.classes import Settings, Version
    settings = Settings(game_name="My platform game",
                        game_version=Version(0, 9, 9, "b", 78),
                        window_width=640, window_height=480)
                        
It must contain a ``Settings`` object assigned to the global variable ``settings``.

                        
The file ``game.py`` contains the actual game.
It imports the other files in the project, and then sets up the game using the levels and blueprints.
It is the file that should be run to run the game.
Normally, you shouldn't have to edit this file.
It should look like this::

    from gamebaker import game
    import blueprints
    from settings import settings
    from levels import levels

    views, objects = game.load_level(levels, 0)
    events = game.get_events(blueprints)
    game.main(events, views, objects, settings)


Creating a game
===============

After creating the project directory, you can begin programming the game.
This should be done as so:

    1. Create some graphics (or placeholders) and put them in the ``images`` directory
    2. Write some logic in subclasses of ``Blueprint`` in ``blueprints.py``
    3. Edit levels in ``levels.py`` to include the new objects
    4. Test the game
    5. Repeat the above steps until the game is finished
"""