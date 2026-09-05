import math
from abc import ABC, abstractmethod


class DragModel(ABC):
    """Something that can compute the acceleration acting on a
    projectile, given its current velocity components."""

    @abstractmethod
    def acceleration(self, vx, vy, gravity):
        """Return (ax, ay) for the given velocity and gravity."""
        raise NotImplementedError


class NoDrag(DragModel):
    """Gravity only - the classic textbook case."""

    def acceleration(self, vx, vy, gravity):
        return 0.0, -gravity


class QuadraticDrag(DragModel):
    """Gravity plus quadratic (speed-squared) air resistance:
    F_drag = -k * v * |v|, split into its x and y components."""

    def __init__(self, drag_coefficient, mass):
        self._k = drag_coefficient
        self._mass = mass

    def acceleration(self, vx, vy, gravity):
        speed = math.hypot(vx, vy)
        if speed == 0:
            return 0.0, -gravity
        factor = (self._k / self._mass) * speed
        return -factor * vx, -gravity - factor * vy


class ProjectilePhysics:
    """Simulates a projectile's flight using semi-implicit Euler
    integration, optionally with quadratic air resistance."""

    def __init__(self, launchSpeed, launchAngle, startHeight=0.0,
                 gravity=9.81, dragCoefficient=0.0, mass=1.0, dt=0.001):
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

        # Pick a drag model up front; ProjectilePhysics itself never
        # needs to know which one it is holding (polymorphism).
        self._drag_model = (
            QuadraticDrag(dragCoefficient, mass) if dragCoefficient > 0 else NoDrag()
        )

        self.__trajectory = []  # private: (t, x, y, vx, vy) samples
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

            # Semi-implicit (symplectic) Euler: update velocity first,
            # then use the new velocity to update position. More stable
            # than plain Euler for this kind of motion.
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
        """Shared lookup helper for position_lookup() and velocity_at()."""
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
        """Find where the object was at a given time."""
        return self._sample_at(t, 1), self._sample_at(t, 2)

    def velocity_at(self, t):
        """Find how fast the object was moving at a given time."""
        return self._sample_at(t, 3), self._sample_at(t, 4)

    def max_height(self):
        """Maximum height reached by the object."""
        return max(point[2] for point in self.__trajectory)

    def range(self):
        """How far the object travelled from launch to landing."""
        return self.__trajectory[-1][1]

    def flight_time(self):
        """Total time from launch to landing."""
        return self.__trajectory[-1][0]

    def full_trajectory(self):
        """Returns the full list of (t, x, y, vx, vy) samples."""
        return self.__trajectory

    def results(self):
        """Key results, ready to display or plot."""
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