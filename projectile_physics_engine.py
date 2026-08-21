#physics functions that need for the projectile motion
import math

class ProjectilePhysics:
    def __init__(self, launchSpeed, launchAngle, startHeight = 0.0, gravity = 9.81, dragCoefficient= 0.0, mass = 1.0, dt = 0.001):

        self.launchSpeed = launchSpeed # speed of the launched object in m/s
        self.launchAngle = launchAngle  #The launching angle of the object
        self.startHeight = startHeight  # The starting height above the ground in meters
        self.gravity = gravity #Gravitational acceleration in m/s^2
        self.dragCoefficient = dragCoefficient  #How strongly air resistance is slow down the object
        self.mass = mass  #Mass of the projectile in kg
        self.dt = dt #integration timesteps(s)
        self.angleRadius = math.radians(launchAngle)

        self.horizontalVelocity = launchAngle * math.cos(self.angleRadius) #vx0
        self.verticalVelocity = launchAngle * math.sin(self.angleRadius)  #vy0

        self._trajectory = None
        self._simulate()


    #Calculate the flight path of the projectile
    def _simulate(self):
        t = 0.0
        x, y = 0.0, self.startHeight
        vx, vy = self.horizontalVelocity, self.verticalVelocity

        trajectory = [(t, x, y, vx, vy)]

        while y >= 0:
            speed = math.hypot(vx, vy)

            # Quadratic drag: F_drag = -k * v * |v|, split into components.
            if self.drag_coefficient > 0 and speed > 0:
                ax = -(self.dragCoefficient / self.mass) * speed * vx
                ay = -self.gravity - (self.dragCoefficient / self.mass) * speed * vy
            else:
                ax = 0.0
                ay = -self.gravity

            # Semi-implicit (symplectic) Euler: update velocity first,
            # then use the new velocity to update position. More stable
            # than plain Euler for this kind of motion.
            vx += ax * self.dt
            vy += ay * self.dt
            x += vx * self.dt
            y += vy * self.dt
            t += self.dt

            trajectory.append((t, x, y, vx, vy))

            if t > 1000:  # safety cutoff against infinite loops
                break

        self._trajectory = trajectory

    #This method is used to find where the object was at a that time
    def position_lookup(self, t): 

        for i in range(len(self._trajectory) - 1):
            t0 = self._trajectory[i][0]
            t1 = self._trajectory[i + 1][0]

            if t0 <= t <= t1:
                return self._trajectory[i][1], self._trajectory[i][2]
        last = self._trajectory[-1]
        return last[1], last[2]

    #This method is used to find how much fast the object was forwarding at the given moment
    def velocity_at(self, t):
        for i in range(len(self._trajectory) - 1):
            t0 = self._trajectory[i][0]
            t1 = self._trajectory[i + 1][0]
            if t0 <= t <= t1:
                return self._trajectory[i][3], self._trajectory[i][4]
        last = self._trajectory[-1]
        return last[3], last[4]

    #To find maximum height reached by the object
    def max_height(self):
        return max(point[2] for point in self._trajectory)

    #To find how far the object go from it started point to end point
    def range(self):
        return self._trajectory[-1][1]

    #Total time it takes from start to end point
    def flight_time(self):
        return self._trajectory[-1][0]

    #Show the entire recorded flight path
    def full_trajectory(self):
        """Returns the full list of (t, x, y, vx, vy) samples."""
        return self._trajectory

    #Key results
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
    p = ProjectilePhysics(v0=30, angle_deg=45, height=0, drag_coefficient=0.02)
    for k, v in p.results().items():
        print(f"{k}: {v}")      
        


