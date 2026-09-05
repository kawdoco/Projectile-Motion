from abc import ABC, abstractmethod

from projectile_physics_engine import ProjectilePhysics
from ui import UI

#Use Abstraction method of OOP
class SimulationRunner(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError

#Use Inheritance in OOP
class CLIRunner(SimulationRunner):
    """Runs the simulation loop in the terminal using ui.UI."""

    def __init__(self):
        self._ui = UI()

    def run(self):
        again = True
        while again:
            inputs = self._ui.collect_inputs()
            projectile = ProjectilePhysics(**inputs)
            self._ui.display_summary(projectile.results())
            again = self._ui.ask_again()


class GUIRunner(SimulationRunner):
    
    def run(self):
        from gui import run as run_gui

        run_gui()


def choose_runner() -> SimulationRunner:
    choice = input("Run as (1) GUI or (2) command line? [1]: ").strip()
    if choice == "2":
        return CLIRunner()
    return GUIRunner()


def main():
    runner = choose_runner()
    runner.run()


if __name__ == "__main__":
    main()
