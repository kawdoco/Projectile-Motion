import math

class UI:

    @staticmethod
    def get_float(prompt, default=None, min_value=None, max_value=None):

        while True:

            if default is not None:
    
                if min_value is not None and max_value is not None:
                    message = f"{prompt} ({min_value}-{max_value})"
                elif min_value is not None:
                    message = f"{prompt} (minimum: {min_value})"
                elif max_value is not None:
                    message = f"{prompt} (maximum: {max_value})"
                else:
                    message = prompt

                user_input = input(
                    f"{message} [{default}]: "
                ).strip() 

                
                if user_input == "":
                    return default

            else:
                user_input = input(f"{prompt}: ").strip()

            try:
                value = float(user_input)

                if not math.isfinite(value):
                    print(
                        "Invalid input. Please enter a valid number."
                    )
                    continue
                
                if min_value is not None and value < min_value:
                    print(
                        f"Invalid input. "
                        f"Value must be at least {min_value}."
                    )
                    continue

                

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
        

        print("\n" + "=" * 45)
        print("       PROJECTILE MOTION SIMULATION")
        print("=" * 45)

        print("\nEnter the following values.")
        print("Press Enter to use the default value.\n")

        
        launch_speed = cls.get_float(
            "Initial speed (m/s)",
            default=30.0,
            min_value=0.0
        )

        
        launch_angle = cls.get_float(
            "Launch angle (degrees)",
            default=45.0,
            min_value=0.0,
            max_value=90.0
        )

        
        start_height = cls.get_float(
            "Launch height (m)",
            default=0.0,
            min_value=0.0
        )

        
        gravity = cls.get_float(
            "Gravity (m/s²)",
            default=9.81,
            min_value=0.1
        )

        
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