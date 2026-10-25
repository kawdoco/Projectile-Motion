import math
from abc import ABC, abstractmethod

#Use abstract pillar of OOP
class DragModel(ABC):

    #Use abstraction method
    @abstractmethod
    def acceleration(self, vx, vy, gravity):
        raise NotImplementedError

#Use inheritance to access the data and methods in the parent class
class NoDrag(DragModel):

    #Use method overriding
    def acceleration(self, vx, vy, gravity):
        return 0.0, -gravity

#Use inheritance to access the data and methods in the parent class
class QuadraticDrag(DragModel):

    def __init__(self, drag_coefficient, mass):
        self._k = drag_coefficient
        self._mass = mass

    @property
    def drag_coefficient(self):
        return self._k

    @property
    def mass(self):
        return self._mass

    #use method overriding
    def acceleration(self, vx, vy, gravity):
        speed = math.hypot(vx, vy)
        if speed == 0:
            return 0.0, -gravity
        factor = (self._k / self._mass) * speed
        return -factor * vx, -gravity - factor * vy
    
#Use multi level inheritance to access the data and methods in the parent class
class BasketballDrag(QuadraticDrag):
    
    def __init__(self):
        super().__init__(drag_coefficient=0.013, mass=0.624)

#Use multi level inheritance to access the data and methods in the parent class
class GolfBallDrag(QuadraticDrag):
   
    def __init__(self):
        super().__init__(drag_coefficient=0.00022, mass=0.0459)

#Use Multilevel inheritance to access the data and methods in the parent class
class CannonballDrag(QuadraticDrag):
    
    def __init__(self):
        super().__init__(drag_coefficient=0.0033, mass=5.4)


class ProjectilePhysics:
  
    def __init__(self, launchSpeed, launchAngle, startHeight=0.0,
                 gravity=9.81, dragCoefficient=0.0, mass=1.0, dt=0.001,
                 drag_model=None):
        self.launchSpeed = launchSpeed          # m/s
        self.launchAngle = launchAngle          # degrees
        self.startHeight = startHeight          # m above the ground
        self.gravity = gravity                  # m/s^2
        self.dragCoefficient = dragCoefficient  # how strongly air slows the object
        self.mass = mass                        # kg
        self.dt = dt                            # integration timestep (s)

        angle_rad = math.radians(launchAngle)
        self.horizontalVelocity = launchSpeed * math.cos(angle_rad)  # vx0
        self.verticalVelocity = launchSpeed * math.sin(angle_rad)    # vy0

        self._drag_model = drag_model if drag_model is not None else (
            QuadraticDrag(dragCoefficient, mass) if dragCoefficient > 0 else NoDrag()
        )

        self.__trajectory = []  # private: (t, x, y, vx, vy) samples
        self._simulate() #use encapsulation to protect this method

    
    def _simulate(self):  #Accessing a protected method
        t = 0.0
        x, y = 0.0, self.startHeight
        vx, vy = self.horizontalVelocity, self.verticalVelocity

        trajectory = [(t, x, y, vx, vy)]

        #use to enter values for private list.
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

    #----Behaviors of the projectile physics class---
    
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