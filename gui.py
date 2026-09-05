from abc import ABC, abstractmethod

import pygame

from projectile_physics_engine import ProjectilePhysics

# ---- Dark "slate" theme, shared across the whole window ----
BG = (11, 15, 25)              # 0b0f19
PANEL_BG = (20, 26, 41)        # 141a29
PANEL_BORDER = (35, 43, 64)    # 232b40
CARD_BG = (26, 33, 54)         # 1a2136
FG = (230, 235, 245)           # e6ebf5
FG_MUTED = (139, 147, 167)     # 8b93a7
ACCENT = (34, 211, 238)        # 22d3ee
ACCENT_DARK = (5, 34, 41)      # button text on accent
POINT_COLOR = (239, 68, 68)    # ef4444
GRID_COLOR = (42, 51, 80)      # 2a3350
BUTTON_BG = (30, 39, 64)       # 1e2740
BUTTON_BG_HOVER = (38, 49, 79)  # 26314f

WIDTH, HEIGHT = 1200, 760
FRAME_INTERVAL_MS = 20  # matches the original matplotlib animation interval


def _fmt(value):
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


# ----------------------------------------------------------------------
# Hand-rolled widgets (Pygame has none built in)
# ----------------------------------------------------------------------
class Widget(ABC):
    
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

    @abstractmethod
    def handle_event(self, event):
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface, fonts):
        raise NotImplementedError


class Button(Widget):
    def __init__(self, rect, text, on_click, accent=False):
        super().__init__(rect)
        self.text = text
        self.on_click = on_click
        self.accent = accent
        self._hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface, fonts):
        if self.accent:
            color = ACCENT
            text_color = ACCENT_DARK
        else:
            color = BUTTON_BG_HOVER if self._hovered else BUTTON_BG
            text_color = FG
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        label = fonts["bold" if self.accent else "normal"].render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


class Slider(Widget):
    def __init__(self, rect, lo, hi, value, step, on_change):
        super().__init__(rect)
        self.lo, self.hi, self.step = lo, hi, step
        self.value = value
        self.on_change = on_change
        self._dragging = False

    def _value_from_mouse(self, mouse_x):
        frac = (mouse_x - self.rect.x) / max(1, self.rect.width)
        frac = min(1.0, max(0.0, frac))
        value = self.lo + frac * (self.hi - self.lo)
        return round(value / self.step) * self.step

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._dragging = True
                self.value = self._value_from_mouse(event.pos[0])
                self.on_change(self.value)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self.value = self._value_from_mouse(event.pos[0])
            self.on_change(self.value)

    def draw(self, surface, fonts):
        track_y = self.rect.centery
        pygame.draw.line(surface, (58, 66, 96), (self.rect.x, track_y),
                          (self.rect.right, track_y), 4)
        frac = (self.value - self.lo) / (self.hi - self.lo) if self.hi > self.lo else 0
        handle_x = self.rect.x + int(frac * self.rect.width)
        pygame.draw.circle(surface, ACCENT, (handle_x, track_y), 8)
        pygame.draw.circle(surface, FG, (handle_x, track_y), 8, width=1)


class TextBox(Widget):
    def __init__(self, rect, initial_text):
        super().__init__(rect)
        self.text = initial_text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and (event.unicode.isdigit() or event.unicode in ".-"):
                self.text += event.unicode

    def draw(self, surface, fonts):
        border = ACCENT if self.active else PANEL_BORDER
        pygame.draw.rect(surface, CARD_BG, self.rect, border_radius=4)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=4)
        label = fonts["normal"].render(self.text, True, FG)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def as_float(self):
        return float(self.text)


class ParamRow:
    
    def __init__(self, x, y, width, key, label, default, lo, hi, step, with_slider):
        self.key = key
        self.label = label
        self.lo, self.hi, self.step = lo, hi, step
        self.textbox = TextBox((x + width - 70, y, 70, 26), _fmt(default))
        self.slider = None
        if with_slider:
            self.slider = Slider((x, y + 30, width, 20), lo, hi, default, step,
                                  on_change=self._sync_from_slider)
        self.label_pos = (x, y)

    def _sync_from_slider(self, value):
        self.textbox.text = _fmt(value)

    def handle_event(self, event):
        self.textbox.handle_event(event)
        if self.slider:
            self.slider.handle_event(event)
        # If the user typed a value and pressed Enter, keep the slider in sync
        if self.slider and not self.textbox.active:
            try:
                self.slider.value = max(self.lo, min(self.hi, self.textbox.as_float()))
            except ValueError:
                pass

    def draw(self, surface, fonts):
        label = fonts["normal"].render(self.label, True, FG)
        surface.blit(label, self.label_pos)
        self.textbox.draw(surface, fonts)
        if self.slider:
            self.slider.draw(surface, fonts)

    def height(self):
        return 58 if self.slider else 34

    def value(self):
        return max(self.lo, min(self.hi, self.textbox.as_float()))


class Sidebar:
   
    FIELDS = [
        ("v0", "Initial Speed (m/s)", 30, 0, 100, 1, True),
        ("angle_deg", "Launch Angle (deg)", 45, 0, 90, 1, True),
        ("height", "Launch Height (m)", 0, 0, 100, 1, False),
        ("gravity", "Gravity (m/s^2)", 9.81, 0.1, 25, 0.01, False),
        ("drag_coefficient", "Drag Coefficient", 0.02, 0, 1, 0.001, False),
    ]

    def __init__(self, rect, on_simulate, on_save_image, on_save_gif):
        self.rect = pygame.Rect(rect)
        self._status = ""

        pad = 18
        x = self.rect.x + pad
        y = self.rect.y + 54
        width = self.rect.width - 2 * pad

        self.rows = []
        for key, label, default, lo, hi, step, with_slider in self.FIELDS:
            row = ParamRow(x, y, width, key, label, default, lo, hi, step, with_slider)
            self.rows.append(row)
            y += row.height() + 10

        y += 10
        btn_h = 40
        self.buttons = [
            Button((x, y, width, btn_h), "\u25B6  SIMULATE", on_simulate, accent=True),
            Button((x, y + btn_h + 8, width, btn_h), "Save Image (PNG)", on_save_image),
            Button((x, y + 2 * (btn_h + 8), width, btn_h), "Save Animation (GIF)", on_save_gif),
        ]
        self._status_pos = (x, y + 3 * (btn_h + 8) + 6)

    def handle_event(self, event):
        for row in self.rows:
            row.handle_event(event)
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface, fonts):
        pygame.draw.rect(surface, PANEL_BG, self.rect, border_radius=10)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, width=1, border_radius=10)

        title = fonts["bold"].render("SIMULATION PARAMETERS", True, FG)
        surface.blit(title, (self.rect.x + 18, self.rect.y + 18))

        for row in self.rows:
            row.draw(surface, fonts)
        for button in self.buttons:
            button.draw(surface, fonts)

        if self._status:
            status_label = fonts["small"].render(self._status, True, FG_MUTED)
            surface.blit(status_label, self._status_pos)

    def read_inputs(self):
        
        try:
            values = {row.key: row.value() for row in self.rows}
        except ValueError:
            self.set_status("Please enter valid numbers in every field.")
            return None
        return {
            "launchSpeed": values["v0"],
            "launchAngle": values["angle_deg"],
            "startHeight": values["height"],
            "gravity": values["gravity"],
            "dragCoefficient": values["drag_coefficient"],
        }

    def set_status(self, text):
        self._status = text


class PlotPanel:
   

    MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 55, 20, 40, 40

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size)
        self.ts = self.xs = self.ys = None
        self.results = None
        self.frame = 0
        self._frame_timer = 0
        self.finished = False
        self._glow_cache = None

    # ---------- animation lifecycle ----------
    def start_animation(self, ts, xs, ys, results):
        self.ts, self.xs, self.ys = ts, xs, ys
        self.results = results
        self.frame = 0
        self._frame_timer = 0
        self.finished = False
        self._glow_cache = None

    def update(self, dt_ms):
        if self.xs is None or self.finished:
            return
        self._frame_timer += dt_ms
        while self._frame_timer >= FRAME_INTERVAL_MS and self.frame < len(self.xs) - 1:
            self.frame += 1
            self._frame_timer -= FRAME_INTERVAL_MS
        if self.frame >= len(self.xs) - 1:
            self.finished = True

    def live_stats(self):
       
        if self.xs is None:
            return None
        return {
            "flight_time": round(self.ts[self.frame], 3),
            "max_height": round(max(self.ys[:self.frame + 1]), 3),
            "range": round(self.results["range"], 3) if self.finished else None,
        }

    # ---------- coordinate transform ----------
    def _plot_rect(self):
        w, h = self.surface.get_size()
        return pygame.Rect(self.MARGIN_L, self.MARGIN_T,
                            w - self.MARGIN_L - self.MARGIN_R,
                            h - self.MARGIN_T - self.MARGIN_B)

    def _to_px(self, x, y, plot_rect, x_max, y_max):
        px = plot_rect.x + (x / x_max) * plot_rect.width if x_max else plot_rect.x
        py = plot_rect.bottom - (y / y_max) * plot_rect.height if y_max else plot_rect.bottom
        return int(px), int(py)

    # ---------- drawing ----------
    def _draw_axes(self, fonts, x_max, y_max):
        plot_rect = self._plot_rect()
        pygame.draw.rect(self.surface, (20, 26, 41), plot_rect)
        for i in range(6):
            gy = plot_rect.y + i * plot_rect.height // 5
            pygame.draw.line(self.surface, GRID_COLOR, (plot_rect.x, gy), (plot_rect.right, gy))
            label = fonts["small"].render(f"{y_max * (5 - i) / 5:.0f}", True, FG_MUTED)
            self.surface.blit(label, (2, gy - 6))
        for i in range(6):
            gx = plot_rect.x + i * plot_rect.width // 5
            pygame.draw.line(self.surface, GRID_COLOR, (gx, plot_rect.y), (gx, plot_rect.bottom))
            label = fonts["small"].render(f"{x_max * i / 5:.0f}", True, FG_MUTED)
            self.surface.blit(label, (gx - 8, plot_rect.bottom + 4))
        pygame.draw.rect(self.surface, PANEL_BORDER, plot_rect, width=1)

        x_label = fonts["small"].render("Horizontal Distance (m)", True, FG)
        self.surface.blit(x_label, x_label.get_rect(center=(plot_rect.centerx, self.surface.get_height() - 8)))
        y_label = fonts["small"].render("Height (m)", True, FG)
        self.surface.blit(pygame.transform.rotate(y_label, 90), (2, plot_rect.centery - 20))

    def _build_glow_cache(self, plot_rect, x_max, y_max):
        glow = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        points = [self._to_px(x, y, plot_rect, x_max, y_max) for x, y in zip(self.xs, self.ys)]
        for width, alpha in ((8, 14), (5, 20), (3, 30)):
            pygame.draw.lines(glow, (*ACCENT, alpha), False, points, width)
        base = plot_rect.bottom
        fill_points = points + [(points[-1][0], base), (points[0][0], base)]
        pygame.draw.polygon(glow, (*ACCENT, 25), fill_points)
        return glow

    def draw(self, target_surface, fonts):
        self.surface.fill(PANEL_BG)
        title = fonts["bold"].render("TRAJECTORY VISUALIZATION", True, FG)
        self.surface.blit(title, title.get_rect(centerx=self.surface.get_width() // 2, y=6))

        if self.xs is None:
            target_surface.blit(self.surface, self.rect.topleft)
            return

        x_max = max(self.xs) * 1.08 + 1
        y_max = max(self.ys) * 1.25 + 1
        plot_rect = self._plot_rect()
        self._draw_axes(fonts, x_max, y_max)

        if self.finished:
            if self._glow_cache is None:
                self._glow_cache = self._build_glow_cache(plot_rect, x_max, y_max)
            self.surface.blit(self._glow_cache, (0, 0))

        points = [self._to_px(x, y, plot_rect, x_max, y_max)
                  for x, y in zip(self.xs[:self.frame + 1], self.ys[:self.frame + 1])]
        if len(points) > 1:
            pygame.draw.lines(self.surface, ACCENT, False, points, 2)
        if points:
            pygame.draw.circle(self.surface, ACCENT, points[-1], 6)
            pygame.draw.circle(self.surface, FG, points[-1], 6, width=1)

        if self.finished and self.results:
            self._draw_annotations(fonts, plot_rect, x_max, y_max)

        target_surface.blit(self.surface, self.rect.topleft)

    def _draw_annotations(self, fonts, plot_rect, x_max, y_max):
        peak_idx = max(range(len(self.ys)), key=lambda i: self.ys[i])
        peak_px = self._to_px(self.xs[peak_idx], self.ys[peak_idx], plot_rect, x_max, y_max)
        pygame.draw.circle(self.surface, ACCENT, peak_px, 4)
        h_label = fonts["small"].render(f"Max Height: {self.results['max_height']} m", True, FG)
        self.surface.blit(h_label, h_label.get_rect(midbottom=(peak_px[0], peak_px[1] - 8)))

        end_px = self._to_px(self.xs[-1], max(0, self.ys[-1]), plot_rect, x_max, y_max)
        for radius, alpha in ((16, 40), (10, 60)):
            ring = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*POINT_COLOR, alpha), (radius, radius), radius, width=2)
            self.surface.blit(ring, (end_px[0] - radius, end_px[1] - radius))
        pygame.draw.circle(self.surface, POINT_COLOR, end_px, 5)
        pygame.draw.circle(self.surface, FG, end_px, 5, width=1)

        range_label = fonts["small"].render(f"Range: {self.results['range']} m", True, ACCENT)
        self.surface.blit(range_label, (end_px[0] - 60, end_px[1] - 30))

    def save_png(self, path):
        pygame.image.save(self.surface, path)


class SummaryBar:
    SPECS = [("max_height", "Max height", " m"), ("range", "Range", " m"),
             ("flight_time", "Flight time", " s")]

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.live = None

    def set_live(self, live):
        """`live` is the dict from PlotPanel.live_stats() - refreshed
        every frame so the numbers move in sync with the flight path."""
        self.live = live

    def draw(self, surface, fonts):
        pygame.draw.rect(surface, PANEL_BG, self.rect, border_radius=10)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, width=1, border_radius=10)

        cell_w = self.rect.width // 3
        for i, (key, label, unit) in enumerate(self.SPECS):
            raw = self.live.get(key) if self.live else None
            value = f"{raw}{unit}" if raw is not None else "\u2013"
            text = f"{label}: {value}"
            rendered = fonts["bold"].render(text, True, FG)
            cx = self.rect.x + cell_w * i + cell_w // 2
            surface.blit(rendered, rendered.get_rect(center=(cx, self.rect.centery)))


class ProjectileGUI:
    

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Projectile Motion Simulator")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {
            "normal": pygame.font.SysFont("segoeui", 16),
            "bold": pygame.font.SysFont("segoeui", 18, bold=True),
            "small": pygame.font.SysFont("segoeui", 13),
        }

        self.projectile = None
        self.running = True

        pad = 14
        sidebar_w = 330
        summary_h = 90
        self.sidebar = Sidebar(
            (pad, pad, sidebar_w, HEIGHT - 2 * pad - summary_h - pad),
            on_simulate=self.run_simulation,
            on_save_image=self.save_image,
            on_save_gif=self.save_gif,
        )
        self.plot_panel = PlotPanel(
            (pad + sidebar_w + pad, pad, WIDTH - sidebar_w - 3 * pad, HEIGHT - 2 * pad - summary_h - pad)
        )
        self.summary_bar = SummaryBar((pad, HEIGHT - pad - summary_h, WIDTH - 2 * pad, summary_h))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def run_simulation(self):
        inputs = self.sidebar.read_inputs()
        if inputs is None:
            return
        self.projectile = ProjectilePhysics(**inputs)
        traj = self.projectile.full_trajectory()[::5]
        ts = [p[0] for p in traj]
        xs = [p[1] for p in traj]
        ys = [p[2] for p in traj]
        results = self.projectile.results()

        self.plot_panel.start_animation(ts, xs, ys, results)
        self.summary_bar.set_live(self.plot_panel.live_stats())
        self.sidebar.set_status("Simulation running...")

    def save_image(self):
        if self.projectile is None:
            self.sidebar.set_status("Click Simulate first.")
            return
        self.plot_panel.save_png("trajectory.png")
        self.sidebar.set_status("Saved current view as trajectory.png")

    def save_gif(self):
        
        if self.projectile is None:
            self.sidebar.set_status("Click Simulate first.")
            return
        try:
            from PIL import Image
        except ImportError:
            self.sidebar.set_status("Saving GIFs requires Pillow (pip install pillow).")
            return

        traj = self.projectile.full_trajectory()[::5]
        ts = [p[0] for p in traj]
        xs = [p[1] for p in traj]
        ys = [p[2] for p in traj]
        results = self.projectile.results()

        capture_panel = PlotPanel(self.plot_panel.rect)
        capture_panel.start_animation(ts, xs, ys, results)

        frames = []
        for _ in range(len(xs)):
            capture_panel.update(FRAME_INTERVAL_MS)
            capture_panel.draw(pygame.Surface((WIDTH, HEIGHT)), self.fonts)
            raw = pygame.image.tostring(capture_panel.surface, "RGB")
            size = capture_panel.surface.get_size()
            frames.append(Image.frombytes("RGB", size, raw))

        # A few held frames on the completed, glowing path so the GIF
        # doesn't cut off the instant the projectile lands.
        for _ in range(15):
            frames.append(frames[-1])

        frames[0].save(
            "trajectory.gif", save_all=True, append_images=frames[1:],
            duration=FRAME_INTERVAL_MS, loop=0,
        )
        self.sidebar.set_status("Saved animation as trajectory.gif")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.sidebar.handle_event(event)

            was_finished = self.plot_panel.finished
            self.plot_panel.update(dt)
            if self.plot_panel.xs is not None:
                self.summary_bar.set_live(self.plot_panel.live_stats())
                if self.plot_panel.finished and not was_finished:
                    self.sidebar.set_status("Simulation complete.")

            self.screen.fill(BG)
            self.sidebar.draw(self.screen, self.fonts)
            self.plot_panel.draw(self.screen, self.fonts)
            self.summary_bar.draw(self.screen, self.fonts)
            pygame.display.flip()

        pygame.quit()


def run():
    ProjectileGUI().run()


if __name__ == "__main__":
    run()
