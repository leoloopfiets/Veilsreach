from dataclasses import dataclass

from .world.world import World
from .window.worldwidget import WorldWidget
from .resources.stlloader import STLLoader

@dataclass
class AppState:
    world: World
    view: WorldWidget
    stlloader: STLLoader 

def newAppState() -> AppState:
    world: World = World()
    view: WorldWidget = WorldWidget(world)
    stlloader: STLLoader = STLLoader(world)

    return AppState(world, view, stlloader)