from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Union

import pygame


Color = Tuple[int, int, int]
ColorWithAlpha = Tuple[int, int, int, int]
ColorLike = Union[Color, ColorWithAlpha]


DEFAULT_COLORS: List[Color] = [
    (0, 0, 0),
    (230, 230, 230),
    (250, 80, 70),
    (70, 170, 250),
    (110, 210, 120),
    (250, 210, 70),
    (200, 120, 240),
]


@dataclass
class ToolState:
    color_index: int = 0
    thickness: int = 4
    speed: int = 1
    # Eraser mode: when True, drawing uses the canvas background color
    eraser: bool = False
    # Canvas background color used for erasing (set by caller)
    background: Optional[ColorLike] = (252, 252, 252)

    def color(self) -> ColorLike:
        if self.eraser and self.background is not None:
            return self.background
        return DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]

    def next_color(self) -> None:
        self.color_index = (self.color_index + 1) % len(DEFAULT_COLORS)

    def prev_color(self) -> None:
        self.color_index = (self.color_index - 1) % len(DEFAULT_COLORS)

    def thicker(self) -> None:
        self.adjust_thickness(1)

    def thinner(self) -> None:
        self.adjust_thickness(-1)

    def adjust_thickness(self, delta: int) -> None:
        self.thickness = max(1, min(64, self.thickness + delta))

    def toggle_eraser(self) -> None:
        self.eraser = not self.eraser


def clamp_point(point: Tuple[int, int], bounds: Tuple[int, int]) -> Tuple[int, int]:
    x, y = point
    max_x, max_y = bounds
    return max(0, min(max_x - 1, x)), max(0, min(max_y - 1, y))


def update_position_from_keys(
        current: Tuple[int, int],
        keys: object,
        bounds: Tuple[int, int],
        speed: int,
) -> Tuple[Tuple[int, int], bool]:
    x, y = current
    moved = False
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        x -= speed
        moved = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        x += speed
        moved = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        y -= speed
        moved = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        y += speed
        moved = True
    new_pos = clamp_point((x, y), bounds)
    return new_pos, moved


def update_position_from_mouse(
        current: Tuple[int, int],
        mouse_pos: Tuple[int, int],
        mouse_down: bool,
        bounds: Tuple[int, int],
) -> Tuple[Tuple[int, int], bool]:
    if not mouse_down:
        return current, False
    new_pos = clamp_point(mouse_pos, bounds)
    return new_pos, new_pos != current
