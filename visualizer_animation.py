"""
visualizer part
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec


DARK_BG = "#0d1117"
PANEL_BG = "#161b22"
TEXT_COLOR = "#c9d1d9"
GRID_COLOR = "#30363d"
ACCENT = "#ff8c42"          
CMAP_NAME = "plasma"        


class TrajectoryVisualizer:
    """Builds static and animated views of a projectile's flight."""

    def __init__(self, projectile):
        self.projectile = projectile
        data = np.array(projectile.full_trajectory())
        
        # Validate trajectory data
        if data.size == 0:
            raise ValueError("Trajectory data is empty")
        if data.shape[1] < 5:
            raise ValueError("Trajectory data must have at least 5 columns (t, x, y, vx, vy)")
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ValueError("Trajectory data contains NaN or infinite values")
        
        self.t = data[:, 0]
        self.x = data[:, 1]
        self.y = data[:, 2]
        self.vx = data[:, 3]
        self.vy = data[:, 4]
        self.speed = np.hypot(self.vx, self.vy)

    # ---------- shared setup helpers ----------

    def _new_figure(self, with_height_panel=True):
        fig = plt.figure(figsize=(11, 5.5))
        fig.patch.set_facecolor(DARK_BG)

        if with_height_panel:
            gs = GridSpec(1, 2, width_ratios=[2.2, 1], wspace=0.28)
            ax_main = fig.add_subplot(gs[0])
            ax_height = fig.add_subplot(gs[1])
            self._style_axes(ax_height, "Time (s)", "Height (m)", "Height vs Time")
        else:
            ax_main = fig.add_subplot(1, 1, 1)
            ax_height = None

        self._style_axes(ax_main, "Horizontal distance (m)", "Height (m)", "Trajectory")
        return fig, ax_main, ax_height

    def _style_axes(self, ax, xlabel, ylabel, title):
        ax.set_facecolor(PANEL_BG)
        ax.set_xlabel(xlabel, color=TEXT_COLOR)
        ax.set_ylabel(ylabel, color=TEXT_COLOR)
        ax.set_title(title, color=TEXT_COLOR, fontsize=11)
        ax.tick_params(colors=TEXT_COLOR)
        ax.grid(color=GRID_COLOR, alpha=0.6, linewidth=0.6)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

    def _stats_text(self):
        r = self.projectile.results()
        return (f"v\u2080 = {r['initial_speed']} m/s   \u03b8 = {r['launch_angle_deg']}\u00b0\n"
                f"range = {r['range']} m   max height = {r['max_height']} m   "
                f"flight time = {r['flight_time']} s")

    # ---------- public API ----------

    def render_static(self, save_path=None, points=400):
        """Draws the full flight path once, colored by instantaneous speed,
        plus a matching height-vs-time curve."""
        idx = np.linspace(0, len(self.x) - 1, min(points, len(self.x))).astype(int)
        xs, ys, ts, speeds = self.x[idx], self.y[idx], self.t[idx], self.speed[idx]

        fig, ax_main, ax_height = self._new_figure(with_height_panel=True)

        sc = ax_main.scatter(xs, ys, c=speeds, cmap=CMAP_NAME, s=10)
        cbar = fig.colorbar(sc, ax=ax_main, pad=0.02)
        cbar.set_label("speed (m/s)", color=TEXT_COLOR)
        cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
        plt.setp(cbar.ax.get_yticklabels(), color=TEXT_COLOR)

        ax_height.plot(ts, ys, color=ACCENT, linewidth=2)
        ax_height.fill_between(ts, ys, color=ACCENT, alpha=0.15)

        fig.text(0.02, 0.02, self._stats_text(), color=TEXT_COLOR, fontsize=9)

        if save_path:
            try:
                fig.savefig(save_path, facecolor=fig.get_facecolor())
                print(f"Saved static visualization to {save_path}")
            except Exception as e:
                print(f"Error saving static visualization: {e}")
        else:
            plt.show()
        return fig

    def render_animation(self, save_path=None, interval=20, frame_step=5):
        """Animates the flight: a gradient trail grows behind a moving marker,
        while the height-vs-time panel fills in alongside it."""
        idx = np.arange(0, len(self.x), frame_step)
        xs, ys, ts, speeds = self.x[idx], self.y[idx], self.t[idx], self.speed[idx]

        fig, ax_main, ax_height = self._new_figure(with_height_panel=True)
        ax_main.set_xlim(xs.min(), xs.max() * 1.05 + 1)
        ax_main.set_ylim(0, ys.max() * 1.2 + 1)
        ax_height.set_xlim(ts.min(), ts.max())
        ax_height.set_ylim(0, ys.max() * 1.2 + 1)

        trail = ax_main.scatter([], [], c=[], cmap=CMAP_NAME, vmin=speeds.min(),
                                 vmax=speeds.max(), s=10)
        marker, = ax_main.plot([], [], "o", color=ACCENT, markersize=9,
                                markeredgecolor="white", markeredgewidth=0.8)
        height_line, = ax_height.plot([], [], color=ACCENT, linewidth=2)

        def update(frame):
            # Ensure frame index is within bounds
            frame_idx = min(frame, len(xs) - 1)
            trail.set_offsets(np.column_stack([xs[:frame_idx + 1], ys[:frame_idx + 1]]))
            trail.set_array(speeds[:frame_idx + 1])
            marker.set_data([xs[frame_idx]], [ys[frame_idx]])
            height_line.set_data(ts[:frame_idx + 1], ys[:frame_idx + 1])
            return trail, marker, height_line

        anim = animation.FuncAnimation(
            fig, update, frames=len(xs), interval=interval, blit=True
        )

        if save_path:
            try:
                anim.save(save_path, writer="pillow")
                print(f"Saved animation to {save_path}")
            except Exception as e:
                print(f"Error saving animation: {e}")
        else:
            plt.show()
        return anim


if __name__ == "__main__":
    # quick manual smoke test using the physics module directly
    try:
        from projectile_physics_engine import ProjectilePhysics

        p = ProjectilePhysics(launchSpeed=35, launchAngle=50, dragCoefficient=0.015)
        viz = TrajectoryVisualizer(p)
        
        # Test static visualization
        print("Generating static visualization...")
        viz.render_static(save_path="static_preview.png")
        
        # Test animated visualization
        print("Generating animated visualization...")
        viz.render_animation(save_path="animation_preview.gif", interval=20, frame_step=5)
        print("Animation saved to animation_preview.gif")
        
    except Exception as e:
        print(f"Error during visualization test: {e}")
        import traceback
        traceback.print_exc()
