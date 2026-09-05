"""
ui.py
Input and User Interface for the Projectile Motion Simulation.

Responsibilities:
- Collect projectile information from the user
- Validate user input
- Provide default values
- Display simulation results
- Allow the user to run multiple simulations
"""


class UI:

    @staticmethod
    def get_float(prompt, default=None, min_value=None, max_value=None):
        """
        Get a valid floating-point number from the user.

        Parameters:
            prompt: Message displayed to the user
            default: Value used when the user presses Enter
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            float: Validated user input
        """

        while True:

            if default is not None:
                user_input = input(
                    f"{prompt} [{default}]: "
                ).strip()

                # Use default if user presses Enter
                if user_input == "":
                    return default

            else:
                user_input = input(f"{prompt}: ").strip()

            try:
                value = float(user_input)

                # Check minimum value
                if min_value is not None and value < min_value:
                    print(
                        f"Invalid input. "
                        f"Value must be at least {min_value}."
                    )
                    continue

                # Check maximum value
                if max_value is not None and value > max_value:
                    print(
                        f"Invalid input. "
                        f"Value must not be greater than {max_value}."
                    )
                    continue

                return value

            except ValueError:
                print(
                    "Invalid input. Please enter a number."
                )

    @classmethod
    def collect_inputs(cls):
        """
        Collect all projectile simulation inputs.

        Returns:
            dict: Input values required by ProjectilePhysics.
        """

        print("\n" + "=" * 45)
        print("       PROJECTILE MOTION SIMULATION")
        print("=" * 45)

        print("\nEnter the following values.")
        print("Press Enter to use the default value.\n")

        # Initial velocity
        launch_speed = cls.get_float(
            "Initial speed (m/s)",
            default=30.0,
            min_value=0.0
        )

        # Launch angle
        launch_angle = cls.get_float(
            "Launch angle (degrees)",
            default=45.0,
            min_value=0.0,
            max_value=90.0
        )

        # Initial height
        start_height = cls.get_float(
            "Launch height (m)",
            default=0.0,
            min_value=0.0
        )

        # Gravity
        gravity = cls.get_float(
            "Gravity (m/s²)",
            default=9.81,
            min_value=0.1
        )

        # Air resistance
        drag_coefficient = cls.get_float(
            "Drag coefficient (0 = no air resistance)",
            default=0.0,
            min_value=0.0
        )

        print("\nInput accepted successfully.")

        return {
            "launchSpeed": launch_speed,
            "launchAngle": launch_angle,
            "startHeight": start_height,
            "gravity": gravity,
            "dragCoefficient": drag_coefficient
        }

    @staticmethod
    def display_summary(summary):
        """
        Display the results returned by ProjectilePhysics.
        """

        print("\n" + "=" * 45)
        print("             SIMULATION RESULTS")
        print("=" * 45)

        print(
            f"Initial speed : "
            f"{summary['initial_speed']:.3f} m/s"
        )

        print(
            f"Launch angle  : "
            f"{summary['launch_angle_deg']:.3f}°"
        )

        print(
            f"Launch height : "
            f"{summary['launch_height']:.3f} m"
        )

        print(
            f"Maximum height: "
            f"{summary['max_height']:.3f} m"
        )

        print(
            f"Range         : "
            f"{summary['range']:.3f} m"
        )

        print(
            f"Flight time   : "
            f"{summary['flight_time']:.3f} s"
        )

        print("=" * 45)

    @staticmethod
    def ask_again():
        """
        Ask the user if another simulation should be performed.

        Returns:
            bool: True if the user wants another simulation.
        """

        while True:

            choice = input(
                "\nRun another simulation? (y/n): "
            ).strip().lower()

            if choice in ("y", "yes"):
                return True

            if choice in ("n", "no"):
                return False

            print(
                "Invalid choice. Please enter 'y' or 'n'."
            )