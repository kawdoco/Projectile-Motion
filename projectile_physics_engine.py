import math
from abc import ABC, abstractmethod

#Use Abstract in OOP to define a base class for drag models. 
class DragModel(ABC):
    
    @abstractmethod
    def acceleration(self, vx, vy, gravity):
        raise NotImplementedError

#Use inheritance in OOP to define a drag model with no air resistance
class NoDrag(DragModel):
    def acceleration(self, vx, vy, gravity):
        return 0.0, -gravity


class QuadraticDrag(DragModel):
    
    def __init__(self, drag_coefficient, mass):
        self._k = drag_coefficient   #Used Encapsulation in OOP to protect the drag_coefficient from being accessed directly
        self._mass = mass            #Used Ecapsulation in OOP to protect the mass attribute

    def acceleration(self, vx, vy, gravity):
        speed = math.hypot(vx, vy)
        if speed == 0:
            return 0.0, -gravity
        factor = (self._k / self._mass) * speed
        return -factor * vx, -gravity - factor * vy


class BaseketballModel(QuadraticDrag):
    def __init__(self):
        super().__init__(drag_coefficient=0.013, mass=0.624)  # unit of mass is kg

class GolfBallModel(QuadraticDrag):
    def __init__(self):
        super().__init__(drag_coefficient=0.000222, mass=0.0459)  # unit of mass is kg

class CannonBallModel(QuadraticDrag):
    def __init__(self):
        super().__init__(drag_coefficient=0.00047, mass=4.0)  # unit of mass is kg
                

class ProjectilePhysics:
    
    def __init__(self, launchSpeed, launchAngle, startHeight=0.0,
                 gravity=9.81, dragCoefficient=0.0, mass=1.0, dt=0.001):
        self.launchSpeed = launchSpeed          # speed of the launched object in m/s
        self.launchAngle = launchAngle          #The launching angle of the object
        self.startHeight = startHeight          # The starting height above the ground in meters
        self.gravity = gravity                  #Gravitational acceleration in m/s^2
        self.dragCoefficient = dragCoefficient  #How strongly air resistance is slow down the object
        self.mass = mass                        #Mass of the projectile in kg
        self.dt = dt                            #integration timesteps(s)
        
        angle_rad = math.radians(launchAngle)
        self.horizontalVelocity = launchSpeed * math.cos(angle_rad)  # vx0
        self.verticalVelocity = launchSpeed * math.sin(angle_rad)    # vy0

        # Pick a drag model up front; ProjectilePhysics itself never
        # needs to know which one it is holding (polymorphism).
        self._drag_model = (
            QuadraticDrag(dragCoefficient, mass) if dragCoefficient > 0 else NoDrag()
        )

        self.__trajectory = []  # Use Encapsulation to hide the trajectory data from internal access.
        self._simulate()

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def _simulate(self):
        t = 0.0
        x, y = 0.0, self.startHeight
        vx, vy = self.horizontalVelocity, self.verticalVelocity

        trajectory = [(t, x, y, vx, vy)]

        while y >= 0:
            ax, ay = self._drag_model.acceleration(vx, vy, self.gravity)

            vx += ax * self.dt
            vy += ay * self.dt
            x += vx * self.dt
            y += vy * self.dt
            t += self.dt

            trajectory.append((t, x, y, vx, vy))

            if t > 1000:  # safety cutoff against runaway loops
                break

        self.__trajectory = trajectory

    def _sample_at(self, t, index):
        
        for i in range(len(self.__trajectory) - 1):
            t0 = self.__trajectory[i][0]
            t1 = self.__trajectory[i + 1][0]
            if t0 <= t <= t1:
                return self.__trajectory[i][index]
        return self.__trajectory[-1][index]

    # ------------------------------------------------------------------
    # Public queries
    # ------------------------------------------------------------------
    def position_lookup(self, t):
        return self._sample_at(t, 1), self._sample_at(t, 2)

    def velocity_at(self, t):    
        return self._sample_at(t, 3), self._sample_at(t, 4)

    def max_height(self):   
        return max(point[2] for point in self.__trajectory)

    def range(self):    
        return self.__trajectory[-1][1]

    def flight_time(self):    
        return self.__trajectory[-1][0]

    def full_trajectory(self):    
        return self.__trajectory

    def results(self):
        
        return {
            "initial_speed": self.launchSpeed,
            "launch_angle_deg": self.launchAngle,
            "launch_height": self.startHeight,
            "max_height": round(self.max_height(), 3),
            "range": round(self.range(), 3),
            "flight_time": round(self.flight_time(), 3),
        }


if __name__ == "__main__":
    # Quick manual check when running this file directly
    p = ProjectilePhysics(launchSpeed=30, launchAngle=45, startHeight=0, dragCoefficient=0.02)
    for k, v in p.results().items():
        print(f"{k}: {v}")