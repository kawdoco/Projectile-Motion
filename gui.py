import math
from abc import ABC, abstractmethod

import pygame

from projectile_physics_engine import (
    ProjectilePhysics, BasketballDrag, GolfBallDrag, CannonballDrag,
)

BG = (11, 15, 25)
PANEL_BG = (20, 26, 41)
PANEL_BORDER = (35, 43, 64)
CARD_BG = (26, 33, 54)
CARD_SHADOW = (7, 10, 18)
FG = (230, 235, 245)
FG_MUTED = (139, 147, 167)
ACCENT = (34, 211, 238)
ACCENT_DARK = (5, 34, 41)
POINT_COLOR = (239, 68, 68)
GRID_COLOR = (42, 51, 80)
BUTTON_BG = (30, 39, 64)
BUTTON_BG_HOVER = (38, 49, 79)
PATH_DIM = (36, 84, 96)

BALL_RADIUS = 9
BALL_COLOR = (151, 160, 181)
BALL_HIGHLIGHT = (226, 232, 242)
BALL_SEAM = (58, 64, 82)
BALL_OUTLINE = (10, 12, 18)

DESIGN_WIDTH, DESIGN_HEIGHT = 1500, 940
MIN_WIDTH, MIN_HEIGHT = 1180, 720


def _get_window_size():

    info = pygame.display.Info()
    margin_w, margin_h = 80, 110
    avail_w = max(info.current_w - margin_w, MIN_WIDTH)
    avail_h = max(info.current_h - margin_h, MIN_HEIGHT)
    width = min(DESIGN_WIDTH, avail_w)
    height = min(DESIGN_HEIGHT, avail_h)
    return int(width), int(height)
FRAME_INTERVAL_MS = 20


def _fmt(value):
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def _icon_preset(surface, rect, color):
    cx, cy = rect.center
    r = min(rect.width, rect.height) // 2 - 2
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surface, color, pts, width=2)


def _icon_speed(surface, rect, color):
    cx, cy = rect.center
    r = min(rect.width, rect.height) // 2 - 2
    gauge_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
    pygame.draw.arc(surface, color, gauge_rect, math.radians(200), math.radians(340), 2)
    needle = math.radians(-25)
    pygame.draw.line(surface, color, (cx, cy), (cx + r * 0.6 * math.cos(needle), cy + r * 0.6 * math.sin(needle)), 2)
    pygame.draw.circle(surface, color, (cx, cy), 2)


def _icon_angle(surface, rect, color):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    base_y = y + h - 3
    pygame.draw.line(surface, color, (x + 2, base_y), (x + w - 2, base_y), 2)
    pygame.draw.line(surface, color, (x + 2, base_y), (x + w - 4, y + 2), 2)
    arc_rect = pygame.Rect(x + 2, base_y - 12, 20, 20)
    pygame.draw.arc(surface, color, arc_rect, math.radians(-35), 0, 1)


def _icon_height(surface, rect, color):
    cx = rect.centerx
    top, bottom = rect.y + 2, rect.y + rect.height - 2
    pygame.draw.line(surface, color, (cx, bottom), (cx, top), 2)
    pygame.draw.line(surface, color, (cx, top), (cx - 4, top + 6), 2)
    pygame.draw.line(surface, color, (cx, top), (cx + 4, top + 6), 2)


def _icon_gravity(surface, rect, color):
    cx = rect.centerx
    top, bottom = rect.y + 2, rect.y + rect.height - 2
    pygame.draw.line(surface, color, (cx, top), (cx, bottom), 2)
    pygame.draw.line(surface, color, (cx, bottom), (cx - 4, bottom - 6), 2)
    pygame.draw.line(surface, color, (cx, bottom), (cx + 4, bottom - 6), 2)


def _icon_mass(surface, rect, color):
    pygame.draw.circle(surface, color, rect.center, min(rect.width, rect.height) // 2 - 2, width=2)


def _icon_drag(surface, rect, color):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    for i, frac in enumerate((0.35, 0.6, 0.85)):
        yy = int(y + h * frac)
        length = w - 4 - i * 3
        pygame.draw.line(surface, color, (x + 2, yy), (x + 2 + length, yy), 2)


def _icon_play(surface, rect, color):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    pts = [(x + w * 0.32, y + h * 0.2), (x + w * 0.32, y + h * 0.8), (x + w * 0.78, y + h * 0.5)]
    pygame.draw.polygon(surface, color, pts)


def _icon_pause(surface, rect, color):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    bar_w = max(2, int(w * 0.2))
    pygame.draw.rect(surface, color, pygame.Rect(int(x + w * 0.28), int(y + h * 0.2), bar_w, int(h * 0.6)))
    pygame.draw.rect(surface, color, pygame.Rect(int(x + w * 0.58), int(y + h * 0.2), bar_w, int(h * 0.6)))


def _icon_restart(surface, rect, color):
    cx, cy = rect.center
    r = min(rect.width, rect.height) // 2 - 3
    arc_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
    pygame.draw.arc(surface, color, arc_rect, math.radians(30), math.radians(320), 2)
    ax = cx + r * math.cos(math.radians(30))
    ay = cy - r * math.sin(math.radians(30))
    pygame.draw.polygon(surface, color, [(ax - 5, ay - 2), (ax + 2, ay - 6), (ax + 4, ay + 3)])


def _icon_stopwatch(surface, rect, color):
    cx, cy = rect.center
    r = min(rect.width, rect.height) // 2 - 3
    pygame.draw.circle(surface, color, (cx, cy), r, width=2)
    pygame.draw.line(surface, color, (cx, cy), (cx, cy - r + 3), 2)
    pygame.draw.line(surface, color, (cx - 3, rect.y), (cx + 3, rect.y), 2)


def _icon_distance(surface, rect, color):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    yy = rect.centery
    pygame.draw.line(surface, color, (x + 2, yy), (x + w - 2, yy), 2)
    pygame.draw.line(surface, color, (x + 2, yy), (x + 7, yy - 4), 2)
    pygame.draw.line(surface, color, (x + 2, yy), (x + 7, yy + 4), 2)
    pygame.draw.line(surface, color, (x + w - 2, yy), (x + w - 7, yy - 4), 2)
    pygame.draw.line(surface, color, (x + w - 2, yy), (x + w - 7, yy + 4), 2)


def _icon_peak(surface, rect, color):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    base_y = y + h - 2
    pts = [(x + 2, base_y), (x + w // 2, y + 2), (x + w - 2, base_y)]
    pygame.draw.lines(surface, color, False, pts, 2)


_ICONS = {
    "preset": _icon_preset, "v0": _icon_speed, "angle_deg": _icon_angle,
    "height": _icon_height, "gravity": _icon_gravity, "mass": _icon_mass,
    "drag_coefficient": _icon_drag, "play": _icon_play, "pause": _icon_pause,
    "restart": _icon_restart, "stopwatch": _icon_stopwatch,
    "distance": _icon_distance, "peak": _icon_peak,
}


def draw_icon(key, surface, rect, color):
    fn = _ICONS.get(key)
    if fn:
        fn(surface, rect, color)


def _draw_glow_rect(surface, rect, color, border_radius=10, layers=4, max_pad=10, base_alpha=70):
    pad_surface = pygame.Rect(rect).inflate(max_pad * 2, max_pad * 2)
    glow = pygame.Surface(pad_surface.size, pygame.SRCALPHA)
    for i in range(layers, 0, -1):
        pad = int(max_pad * i / layers)
        alpha = int(base_alpha * (1 - i / (layers + 1)))
        r = pygame.Rect(max_pad - pad, max_pad - pad,
                         rect.width + pad * 2, rect.height + pad * 2)
        pygame.draw.rect(glow, (*color, alpha), r, border_radius=border_radius + pad)
    surface.blit(glow, pad_surface.topleft)


def _draw_glow_circle(surface, center, radius, color, layers=4, max_pad=12, base_alpha=80):
    size = (radius + max_pad) * 2
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    gc = size // 2
    for i in range(layers, 0, -1):
        pad = int(max_pad * i / layers)
        alpha = int(base_alpha * (1 - i / (layers + 1)))
        pygame.draw.circle(glow, (*color, alpha), (gc, gc), radius + pad)
    surface.blit(glow, (center[0] - gc, center[1] - gc))


def _build_background_overlay(width, height):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)

    spacing = 42
    for gx in range(spacing // 2, width, spacing):
        for gy in range(spacing // 2, height, spacing):
            pygame.draw.circle(overlay, (255, 255, 255, 7), (gx, gy), 1)

    diag = math.hypot(width, height)
    corners = [(0, 0), (width, 0), (0, height), (width, height)]
    rings = [(0.42 * diag, 10), (0.30 * diag, 12), (0.18 * diag, 14)]
    for cx, cy in corners:
        for r, alpha in rings:
            pygame.draw.circle(overlay, (0, 0, 0, alpha), (cx, cy), int(r))

    return overlay


def _draw_card_bg(surface, rect, fonts=None, title=None, icon_key=None, radius=14):
    shadow_rect = pygame.Rect(rect.x, rect.y + 3, rect.width, rect.height)
    pygame.draw.rect(surface, CARD_SHADOW, shadow_rect, border_radius=radius)
    pygame.draw.rect(surface, CARD_BG, rect, border_radius=radius)
    pygame.draw.rect(surface, PANEL_BORDER, rect, width=1, border_radius=radius)

    if title and fonts:
        pad = 16
        header_size = 18
        text_x = rect.x + pad
        if icon_key:
            icon_rect = pygame.Rect(rect.x + pad, rect.y + pad - 2, header_size, header_size)
            draw_icon(icon_key, surface, icon_rect, ACCENT)
            text_x = icon_rect.right + 8
        label = fonts["bold"].render(title.upper(), True, FG)
        surface.blit(label, (text_x, rect.y + pad - 3))


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

    def __init__(self, rect, text="", on_click=None, accent=False,
                 icon_key=None, icon_fn=None, text_fn=None):
        super().__init__(rect)
        self.text = text
        self.on_click = on_click
        self.accent = accent
        self.icon_key = icon_key
        self.icon_fn = icon_fn
        self.text_fn = text_fn
        self._hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

    def draw(self, surface, fonts):
        if self.accent:
            _draw_glow_rect(surface, self.rect, ACCENT, border_radius=10)
            color = ACCENT
            text_color = ACCENT_DARK
        else:
            color = BUTTON_BG_HOVER if self._hovered else BUTTON_BG
            text_color = FG
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        key = self.icon_fn() if self.icon_fn else self.icon_key
        label_text = self.text_fn() if self.text_fn else self.text
        if key and not label_text:
            size = 18
            icon_rect = pygame.Rect(0, 0, size, size)
            icon_rect.center = self.rect.center
            draw_icon(key, surface, icon_rect, text_color)
            return

        label = fonts["bold" if self.accent else "normal"].render(label_text, True, text_color)
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
        pygame.draw.line(surface, ACCENT, (self.rect.x, track_y), (handle_x, track_y), 4)
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
        pygame.draw.rect(surface, BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=6)
        label = fonts["normal"].render(self.text, True, FG)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def as_float(self):
        return float(self.text)


class SegmentedControl(Widget):

    def __init__(self, rect, options, selected, on_select):
        super().__init__(rect)
        self.options = options
        self.selected = selected
        self.on_select = on_select
        self._hover = None

    def _option_rect(self, i):
        w = self.rect.width // len(self.options)
        return pygame.Rect(self.rect.x + i * w, self.rect.y, w - 4, self.rect.height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hover = next(
                (i for i in range(len(self.options)) if self._option_rect(i).collidepoint(event.pos)),
                None,
            )
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, opt in enumerate(self.options):
                if self._option_rect(i).collidepoint(event.pos):
                    self.selected = opt
                    self.on_select(opt)

    def draw(self, surface, fonts):
        for i, opt in enumerate(self.options):
            r = self._option_rect(i)
            if opt == self.selected:
                color, text_color = ACCENT, ACCENT_DARK
            else:
                color = BUTTON_BG_HOVER if self._hover == i else BUTTON_BG
                text_color = FG
            pygame.draw.rect(surface, color, r, border_radius=8)
            label = fonts["small"].render(opt, True, text_color)
            surface.blit(label, label.get_rect(center=r.center))


class ParamRow:

    def __init__(self, x, y, width, key, label, default, lo, hi, step, with_slider):
        self.key = key
        self.label = label
        self.lo, self.hi, self.step = lo, hi, step
        self.textbox = TextBox((x + width - 72, y, 72, 26), _fmt(default))
        self.slider = None
        if with_slider:
            self.slider = Slider((x, y + 32, width, 20), lo, hi, default, step,
                                  on_change=self._sync_from_slider)
        self.label_pos = (x + 26, y + 4)
        self.icon_rect = pygame.Rect(x, y, 20, 20)

    def _sync_from_slider(self, value):
        self.textbox.text = _fmt(value)

    def handle_event(self, event):
        self.textbox.handle_event(event)
        if self.slider:
            self.slider.handle_event(event)
        if self.slider and not self.textbox.active:
            try:
                self.slider.value = max(self.lo, min(self.hi, self.textbox.as_float()))
            except ValueError:
                pass

    def draw(self, surface, fonts):
        draw_icon(self.key, surface, self.icon_rect, FG_MUTED)
        label = fonts["normal"].render(self.label, True, FG)
        surface.blit(label, self.label_pos)
        self.textbox.draw(surface, fonts)
        if self.slider:
            self.slider.draw(surface, fonts)

    def height(self):
        return 60 if self.slider else 30

    def value(self):
        return max(self.lo, min(self.hi, self.textbox.as_float()))


class Sidebar:

    MOTION_FIELDS = [
        ("v0", "Initial Speed (m/s)", 30, 0, 100, 1, True),
        ("angle_deg", "Launch Angle (deg)", 45, 0, 90, 1, True),
        ("height", "Launch Height (m)", 0, 0, 100, 1, False),
    ]
    PHYSICS_FIELDS = [
        ("gravity", "Gravity (m/s^2)", 9.81, 0.1, 25, 0.01, False),
        ("mass", "Mass (kg)", 1.0, 0.01, 20, 0.01, False),
        ("drag_coefficient", "Drag Coefficient", 0.02, 0, 1, 0.001, False),
    ]

    PRESETS = {
        "Custom": None,
        "Basketball": BasketballDrag,
        "Golf Ball": GolfBallDrag,
        "Cannonball": CannonballDrag,
    }

    CARD_PAD = 16
    HEADER_H = 24
    HEADER_GAP = 12
    ROW_GAP = 12
    CARD_GAP = 14

    def __init__(self, rect, on_simulate, on_save_image, on_save_gif):
        self.rect = pygame.Rect(rect)
        self._status = ""
        self._preset = "Custom"
        self.cards = []

        outer_pad = 20
        x = self.rect.x + outer_pad
        width = self.rect.width - 2 * outer_pad
        inner_x = x + self.CARD_PAD
        inner_w = width - 2 * self.CARD_PAD
        y = self.rect.y + outer_pad

        card_top = y
        y += self.CARD_PAD + self.HEADER_H + self.HEADER_GAP
        self.preset_selector = SegmentedControl(
            (inner_x, y, inner_w, 30), list(self.PRESETS.keys()), "Custom", self._on_preset_selected
        )
        y += 30
        self.cards.append((pygame.Rect(x, card_top, width, y + self.CARD_PAD - card_top),
                            "Preset", "preset"))
        y += self.CARD_PAD + self.CARD_GAP

        card_top = y
        y += self.CARD_PAD + self.HEADER_H + self.HEADER_GAP
        self.rows = []
        for spec in self.MOTION_FIELDS:
            row = ParamRow(inner_x, y, inner_w, *spec)
            self.rows.append(row)
            y += row.height() + self.ROW_GAP
        y -= self.ROW_GAP
        self.cards.append((pygame.Rect(x, card_top, width, y + self.CARD_PAD - card_top),
                            "Motion", "v0"))
        y += self.CARD_PAD + self.CARD_GAP

        card_top = y
        y += self.CARD_PAD + self.HEADER_H + self.HEADER_GAP
        for spec in self.PHYSICS_FIELDS:
            row = ParamRow(inner_x, y, inner_w, *spec)
            self.rows.append(row)
            y += row.height() + self.ROW_GAP
        y -= self.ROW_GAP
        self.cards.append((pygame.Rect(x, card_top, width, y + self.CARD_PAD - card_top),
                            "Physics", "gravity"))
        y += self.CARD_PAD + self.CARD_GAP

        y += 4
        btn_h = 42
        self.buttons = [
            Button((x, y, width, btn_h), "\u25B6  SIMULATE", on_simulate, accent=True),
            Button((x, y + btn_h + 10, width, btn_h), "Save Image (PNG)", on_save_image),
            Button((x, y + 2 * (btn_h + 10), width, btn_h), "Save Animation (GIF)", on_save_gif),
        ]
        self._status_pos = (x, y + 3 * (btn_h + 10) + 8)
        self._content_bottom = self._status_pos[1] + 20
        self._scroll_offset = 0

    def _shift_content(self, dy):
        for card_rect, _, _ in self.cards:
            card_rect.y += dy
        self.preset_selector.rect.y += dy
        for row in self.rows:
            row.textbox.rect.y += dy
            row.icon_rect.y += dy
            row.label_pos = (row.label_pos[0], row.label_pos[1] + dy)
            if row.slider:
                row.slider.rect.y += dy
        for button in self.buttons:
            button.rect.y += dy
        self._status_pos = (self._status_pos[0], self._status_pos[1] + dy)

    def _row_by_key(self, key):
        return next((row for row in self.rows if row.key == key), None)

    def _on_preset_selected(self, name):
        self._preset = name
        preset_cls = self.PRESETS[name]
        if preset_cls is None:
            return
        model = preset_cls()
        for key, value in (("mass", model.mass), ("drag_coefficient", model.drag_coefficient)):
            row = self._row_by_key(key)
            row.textbox.text = _fmt(value)
            if row.slider:
                row.slider.value = max(row.lo, min(row.hi, value))

    def selected_drag_model(self):
        preset_cls = self.PRESETS[self._preset]
        return preset_cls() if preset_cls else None

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_x, mouse_y):
                max_scroll = max(0, self._content_bottom - self.rect.bottom + 12)
                self._scroll_offset = max(0, min(max_scroll, self._scroll_offset - event.y * 36))
            return

        self._shift_content(-self._scroll_offset)
        mass_row, drag_row = self._row_by_key("mass"), self._row_by_key("drag_coefficient")
        before_preset = self._preset
        before = (mass_row.textbox.text, drag_row.textbox.text)

        self.preset_selector.handle_event(event)
        for row in self.rows:
            row.handle_event(event)
        for button in self.buttons:
            button.handle_event(event)

        preset_changed_this_event = self._preset != before_preset
        if (not preset_changed_this_event and self._preset != "Custom"
                and (mass_row.textbox.text, drag_row.textbox.text) != before):
            self._preset = "Custom"
            self.preset_selector.selected = "Custom"
        self._shift_content(self._scroll_offset)

    def draw(self, surface, fonts):
        old_clip = surface.get_clip()
        surface.set_clip(self.rect.clip(old_clip))
        self._shift_content(-self._scroll_offset)
        for card_rect, title, icon_key in self.cards:
            _draw_card_bg(surface, card_rect, fonts, title, icon_key)

        self.preset_selector.draw(surface, fonts)
        for row in self.rows:
            row.draw(surface, fonts)
        for button in self.buttons:
            button.draw(surface, fonts)

        if self._status:
            status_label = fonts["small"].render(self._status, True, FG_MUTED)
            surface.blit(status_label, self._status_pos)
        self._shift_content(self._scroll_offset)
        surface.set_clip(old_clip)

    def read_inputs(self):
        try:
            values = {row.key: row.textbox.as_float() for row in self.rows}
        except ValueError:
            self.set_status("Please enter valid numbers in every field.")
            return None
        if any(not math.isfinite(value) for value in values.values()):
            self.set_status("Values must be finite numbers.")
            return None
        for row in self.rows:
            value = values[row.key]
            if not row.lo <= value <= row.hi:
                self.set_status(f"{row.label} must be between {row.lo:g} and {row.hi:g}.")
                return None
        return {
            "launchSpeed": values["v0"],
            "launchAngle": values["angle_deg"],
            "startHeight": values["height"],
            "gravity": values["gravity"],
            "dragCoefficient": values["drag_coefficient"],
            "mass": values["mass"],
        }

    def set_status(self, text):
        self._status = text

    def any_field_active(self):
        return any(row.textbox.active for row in self.rows)


class PlotPanel:

    MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 55, 20, 44, 40
    TRAIL_LENGTH = 24
    OVERLAY_LINE_H = 17

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.surface = pygame.Surface(self.rect.size)
        self.ts = self.xs = self.ys = self.vxs = self.vys = None
        self.results = None
        self.frame = 0
        self._frame_timer = 0
        self.finished = False
        self.paused = False
        self.speed_mult = 1.0
        self._glow_cache = None

    def start_animation(self, ts, xs, ys, vxs, vys, results):
        self.ts, self.xs, self.ys, self.vxs, self.vys = ts, xs, ys, vxs, vys
        self.results = results
        self.frame = 0
        self._frame_timer = 0
        self.finished = False
        self.paused = False
        self._glow_cache = None

    def restart(self):
        if self.xs is None:
            return
        self.frame = 0
        self._frame_timer = 0
        self.finished = False
        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

    def set_speed(self, multiplier):
        self.speed_mult = multiplier

    def frac(self):
        if not self.xs or len(self.xs) <= 1:
            return 0.0
        return self.frame / (len(self.xs) - 1)

    def seek_frac(self, frac):
        if not self.xs:
            return
        frac = min(1.0, max(0.0, frac))
        self.frame = int(round(frac * (len(self.xs) - 1)))
        self._frame_timer = 0
        self.finished = self.frame >= len(self.xs) - 1

    def update(self, dt_ms):
        if self.xs is None or self.finished or self.paused:
            return
        self._frame_timer += dt_ms * self.speed_mult
        while self._frame_timer >= FRAME_INTERVAL_MS and self.frame < len(self.xs) - 1:
            self.frame += 1
            self._frame_timer -= FRAME_INTERVAL_MS
        if self.frame >= len(self.xs) - 1:
            self.finished = True

    def live_stats(self):
        if self.xs is None:
            return None
        vx, vy = self.vxs[self.frame], self.vys[self.frame]
        return {
            "flight_time": round(self.ts[self.frame], 3),
            "max_height": round(max(self.ys[:self.frame + 1]), 3),
            "range": round(self.results["range"], 3) if self.finished else None,
            "height": round(self.ys[self.frame], 3),
            "vx": round(vx, 2),
            "vy": round(vy, 2),
            "speed": round(math.hypot(vx, vy), 2),
        }

    def _plot_rect(self):
        w, h = self.surface.get_size()
        return pygame.Rect(self.MARGIN_L, self.MARGIN_T,
                            w - self.MARGIN_L - self.MARGIN_R,
                            h - self.MARGIN_T - self.MARGIN_B)

    def _to_px(self, x, y, plot_rect, x_max, y_max):
        px = plot_rect.x + (x / x_max) * plot_rect.width if x_max else plot_rect.x
        py = plot_rect.bottom - (y / y_max) * plot_rect.height if y_max else plot_rect.bottom
        return int(px), int(py)

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

    def _draw_path(self, plot_rect, x_max, y_max):
        points = [self._to_px(x, y, plot_rect, x_max, y_max)
                  for x, y in zip(self.xs[:self.frame + 1], self.ys[:self.frame + 1])]
        if len(points) > 1:
            pygame.draw.lines(self.surface, PATH_DIM, False, points, 2)

    def _draw_trail(self, plot_rect, x_max, y_max):
        n = min(self.frame, self.TRAIL_LENGTH)
        if n <= 0:
            return
        for i in range(self.frame - n, self.frame):
            age = self.frame - i
            fade = 1 - age / n
            alpha = max(0, int(170 * fade))
            radius = max(1, int(BALL_RADIUS * 0.55 * fade))
            px, py = self._to_px(self.xs[i], self.ys[i], plot_rect, x_max, y_max)
            size = radius * 2 + 2
            dot = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*ACCENT, alpha), (radius + 1, radius + 1), radius)
            self.surface.blit(dot, (px - radius - 1, py - radius - 1))

    def _draw_shadow(self, plot_rect, bx, height_frac):
        ground_y = plot_rect.bottom
        scale = max(0.35, 1 - height_frac * 0.75)
        w = max(4, int(BALL_RADIUS * 2.4 * scale))
        h = max(2, int(BALL_RADIUS * 0.7 * scale))
        alpha = int(130 * scale) + 20
        shadow = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, alpha), pygame.Rect(1, 1, w, h))
        self.surface.blit(shadow, (bx - w // 2 - 1, ground_y - h // 2 - 1))

    def _draw_ball(self, plot_rect, x_max, y_max):
        bx, by = self._to_px(self.xs[self.frame], self.ys[self.frame], plot_rect, x_max, y_max)
        height_frac = max(0.0, min(1.0, self.ys[self.frame] / y_max)) if y_max else 0.0
        self._draw_shadow(plot_rect, bx, height_frac)

        _draw_glow_circle(self.surface, (bx, by), BALL_RADIUS, ACCENT, max_pad=14, base_alpha=65)

        r = BALL_RADIUS
        pygame.draw.circle(self.surface, BALL_COLOR, (bx, by), r)
        hl_r = max(1, int(r * 0.4))
        pygame.draw.circle(self.surface, BALL_HIGHLIGHT, (bx - int(r * 0.3), by - int(r * 0.3)), hl_r)

        rotation_deg = (self.xs[self.frame] * 35) % 360
        for a in (rotation_deg, rotation_deg + 180):
            rad = math.radians(a)
            ex = bx + int(r * 0.8 * math.cos(rad))
            ey = by + int(r * 0.8 * math.sin(rad))
            pygame.draw.line(self.surface, BALL_SEAM, (bx, by), (ex, ey), 1)
        pygame.draw.circle(self.surface, BALL_OUTLINE, (bx, by), r, width=1)
        return bx, by

    def _draw_overlay(self, plot_rect, bx, by, fonts):
        stats = self.live_stats()
        if not stats:
            return
        lines = [
            f"Speed   {stats['speed']:.1f} m/s",
            f"Height   {stats['height']:.1f} m",
            f"Elapsed   {stats['flight_time']:.2f} s",
            f"Vx/Vy   {stats['vx']:.1f} / {stats['vy']:.1f}",
        ]
        rendered = [fonts["small"].render(t, True, FG) for t in lines]
        panel_w = max(s.get_width() for s in rendered) + 20
        panel_h = len(lines) * self.OVERLAY_LINE_H + 14

        anchor_x, anchor_y = bx + 16, by - panel_h - 16
        if anchor_x + panel_w > plot_rect.right:
            anchor_x = bx - 16 - panel_w
        if anchor_y < plot_rect.y:
            anchor_y = by + 16
        anchor_x = max(plot_rect.x, min(anchor_x, plot_rect.right - panel_w))
        anchor_y = max(plot_rect.y, min(anchor_y, plot_rect.bottom - panel_h))

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*CARD_BG, 225), pygame.Rect(0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, (*ACCENT, 110), pygame.Rect(0, 0, panel_w, panel_h), width=1, border_radius=8)
        for i, surf in enumerate(rendered):
            panel.blit(surf, (10, 7 + i * self.OVERLAY_LINE_H))
        self.surface.blit(panel, (anchor_x, anchor_y))

        leader_x = max(anchor_x, min(bx, anchor_x + panel_w))
        leader_y = max(anchor_y, min(by, anchor_y + panel_h))
        pygame.draw.line(self.surface, ACCENT, (bx, by), (leader_x, leader_y), 1)

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
        title = fonts["bold"].render("LIVE TRAJECTORY", True, FG)
        self.surface.blit(title, title.get_rect(centerx=self.surface.get_width() // 2, y=6))

        if self.xs is None:
            target_surface.blit(self.surface, self.rect.topleft)
            return

        x_max = max(self.xs) * 1.08 + 1
        y_max = max(self.ys) * 1.25 + 1
        plot_rect = self._plot_rect()
        self._draw_axes(fonts, x_max, y_max)
        self._draw_path(plot_rect, x_max, y_max)

        if self.finished:
            if self._glow_cache is None:
                self._glow_cache = self._build_glow_cache(plot_rect, x_max, y_max)
            self.surface.blit(self._glow_cache, (0, 0))

        self._draw_trail(plot_rect, x_max, y_max)
        bx, by = self._draw_ball(plot_rect, x_max, y_max)

        if not self.finished:
            self._draw_overlay(plot_rect, bx, by, fonts)

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


class PlaybackBar:

    SPEED_OPTIONS = ["0.25x", "1x", "2x", "4x"]
    SPEED_VALUES = {"0.25x": 0.25, "1x": 1.0, "2x": 2.0, "4x": 4.0}

    def __init__(self, rect, plot_panel):
        self.rect = pygame.Rect(rect)
        self.plot_panel = plot_panel

        pad = 18
        x = self.rect.x + pad
        width = self.rect.width - 2 * pad
        y = self.rect.y + pad

        btn_w, btn_h = 56, 36
        self.restart_button = Button((x, y, btn_w, btn_h), on_click=self._on_restart, icon_key="restart")
        self.play_button = Button((x + btn_w + 10, y, btn_w, btn_h), on_click=self._on_toggle_pause,
                                   accent=True, icon_fn=self._play_icon)

        seg_x = x + 2 * (btn_w + 10) + 6
        seg_w = width - 2 * (btn_w + 10) - 6
        self.speed_control = SegmentedControl((seg_x, y, seg_w, btn_h), self.SPEED_OPTIONS, "1x", self._on_speed)

        y2 = y + btn_h + 26
        self.timeline = Slider((x, y2, width, 20), 0.0, 1.0, 0.0, 0.001, self._on_seek)
        self._time_label_pos = (x, y2 - 18)

    def _on_restart(self):
        self.plot_panel.restart()

    def _on_toggle_pause(self):
        if self.plot_panel.xs is not None:
            self.plot_panel.toggle_pause()

    def _play_icon(self):
        if self.plot_panel.xs is None or self.plot_panel.paused or self.plot_panel.finished:
            return "play"
        return "pause"

    def _on_speed(self, label):
        self.plot_panel.set_speed(self.SPEED_VALUES[label])

    def _on_seek(self, value):
        self.plot_panel.paused = True
        self.plot_panel.seek_frac(value)

    def sync(self):
        if not self.timeline._dragging:
            self.timeline.value = self.plot_panel.frac()

    def handle_event(self, event):
        self.restart_button.handle_event(event)
        self.play_button.handle_event(event)
        self.speed_control.handle_event(event)
        self.timeline.handle_event(event)

    def draw(self, surface, fonts):
        _draw_card_bg(surface, self.rect)
        self.restart_button.draw(surface, fonts)
        self.play_button.draw(surface, fonts)
        self.speed_control.draw(surface, fonts)
        self.timeline.draw(surface, fonts)

        stats = self.plot_panel.live_stats()
        elapsed = stats["flight_time"] if stats else 0.0
        total = self.plot_panel.ts[-1] if self.plot_panel.ts else 0.0
        label = fonts["small"].render(f"{elapsed:.2f}s / {total:.2f}s", True, FG_MUTED)
        surface.blit(label, (self.timeline.rect.right - label.get_width(), self._time_label_pos[1]))


class SummaryBar:

    SPECS = [
        ("max_height", "Max Height", " m", "peak"),
        ("range", "Range", " m", "distance"),
        ("flight_time", "Flight Time", " s", "stopwatch"),
    ]

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.live = None
        gap = 14
        n = len(self.SPECS)
        cell_w = (self.rect.width - (n - 1) * gap) // n
        self.cell_rects = [
            pygame.Rect(self.rect.x + i * (cell_w + gap), self.rect.y, cell_w, self.rect.height)
            for i in range(n)
        ]

    def set_live(self, live):
        self.live = live

    def draw(self, surface, fonts):
        for (key, label, unit, icon_key), rect in zip(self.SPECS, self.cell_rects):
            _draw_card_bg(surface, rect)
            raw = self.live.get(key) if self.live else None
            value = f"{raw}{unit}" if raw is not None else "\u2013"

            icon_rect = pygame.Rect(rect.x + 18, rect.centery - 22, 26, 26)
            draw_icon(icon_key, surface, icon_rect, ACCENT)
            text_x = icon_rect.right + 10

            label_surf = fonts["small"].render(label.upper(), True, FG_MUTED)
            surface.blit(label_surf, (text_x, rect.centery - 20))
            value_surf = fonts["bold"].render(value, True, FG)
            surface.blit(value_surf, (text_x, rect.centery - 1))


class ProjectileGUI:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Projectile Motion Simulator")
        width, height = _get_window_size()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fonts = {
            "normal": pygame.font.SysFont("segoeui", 16),
            "bold": pygame.font.SysFont("segoeui", 18, bold=True),
            "small": pygame.font.SysFont("segoeui", 13),
        }

        self.projectile = None
        self.running = True
        self._bg_overlay = _build_background_overlay(width, height)

        pad = 16
        gap = 14
        sidebar_w = 340
        playback_h = 124
        summary_h = 84

        top_area_h = height - 2 * pad - gap - summary_h
        right_x = pad + sidebar_w + gap
        right_w = width - right_x - pad
        plot_h = top_area_h - gap - playback_h

        self.sidebar = Sidebar(
            (pad, pad, sidebar_w, top_area_h),
            on_simulate=self.run_simulation,
            on_save_image=self.save_image,
            on_save_gif=self.save_gif,
        )
        self.plot_panel = PlotPanel((right_x, pad, right_w, plot_h))
        self.playback_bar = PlaybackBar((right_x, pad + plot_h + gap, right_w, playback_h), self.plot_panel)
        self.summary_bar = SummaryBar((pad, pad + top_area_h + gap, width - 2 * pad, summary_h))

    def run_simulation(self):
        inputs = self.sidebar.read_inputs()
        if inputs is None:
            return
        self.projectile = ProjectilePhysics(drag_model=self.sidebar.selected_drag_model(), **inputs)
        traj = self.projectile.full_trajectory()[::5]
        ts = [p[0] for p in traj]
        xs = [p[1] for p in traj]
        ys = [p[2] for p in traj]
        vxs = [p[3] for p in traj]
        vys = [p[4] for p in traj]
        results = self.projectile.results()

        self.plot_panel.start_animation(ts, xs, ys, vxs, vys, results)
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
        vxs = [p[3] for p in traj]
        vys = [p[4] for p in traj]
        results = self.projectile.results()

        capture_panel = PlotPanel(self.plot_panel.rect)
        capture_panel.start_animation(ts, xs, ys, vxs, vys, results)

        frames = []
        for _ in range(len(xs)):
            capture_panel.update(FRAME_INTERVAL_MS)
            capture_panel.draw(pygame.Surface(self.screen.get_size()), self.fonts)
            raw = pygame.image.tostring(capture_panel.surface, "RGB")
            size = capture_panel.surface.get_size()
            frames.append(Image.frombytes("RGB", size, raw))

        for _ in range(15):
            frames.append(frames[-1])

        frames[0].save(
            "trajectory.gif", save_all=True, append_images=frames[1:],
            duration=FRAME_INTERVAL_MS, loop=0,
        )
        self.sidebar.set_status("Saved animation as trajectory.gif")

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and not self.sidebar.any_field_active():
                    if event.key == pygame.K_SPACE and self.plot_panel.xs is not None:
                        self.plot_panel.toggle_pause()
                    elif event.key == pygame.K_r:
                        self.plot_panel.restart()
                self.sidebar.handle_event(event)
                self.playback_bar.handle_event(event)

            was_finished = self.plot_panel.finished
            if not self.playback_bar.timeline._dragging:
                self.plot_panel.update(dt)
            self.playback_bar.sync()

            if self.plot_panel.xs is not None:
                self.summary_bar.set_live(self.plot_panel.live_stats())
                if self.plot_panel.finished and not was_finished:
                    self.sidebar.set_status("Simulation complete.")

            self.screen.fill(BG)
            self.screen.blit(self._bg_overlay, (0, 0))
            self.sidebar.draw(self.screen, self.fonts)
            self.plot_panel.draw(self.screen, self.fonts)
            self.playback_bar.draw(self.screen, self.fonts)
            self.summary_bar.draw(self.screen, self.fonts)
            pygame.display.flip()

        pygame.quit()


def run():
    ProjectileGUI().run()


if __name__ == "__main__":
    run()
