from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple, Optional

import pygame

from tools import ToolState


Color = Tuple[int, int, int]


def get_color_swatch_rect(overlay_rect: pygame.Rect, swatch_size: int) -> pygame.Rect:
    x = overlay_rect.x + (overlay_rect.width - swatch_size) // 2
    y = overlay_rect.bottom - (swatch_size + 110)
    return pygame.Rect(x, y, swatch_size, swatch_size)


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    hotkey: str
    on_click: Callable[[], None]
    # Optional callable that returns whether this button is currently active
    is_active: Optional[Callable[[], bool]] = None

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, active: bool = False) -> None:
        base = (253, 211, 127)
        highlight = (245, 195, 110) if active else base
        pygame.draw.rect(screen, highlight, self.rect, border_radius=8)
        pygame.draw.rect(screen, (228, 130, 1), self.rect, 2, border_radius=8)
        text = f"{self.label} ({self.hotkey})"
        surface = font.render(text, True, (40, 40, 45))
        screen.blit(surface, surface.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False


@dataclass
class Knob:
    center: Tuple[int, int]
    radius: int
    label: str
    value_text: Callable[[], str]
    on_click: Optional[Callable[[], None]] = None
    knob_image: Optional[pygame.Surface] = None
    angle: float = 0.0

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        if self.knob_image:
            img = pygame.transform.smoothscale(
                self.knob_image, (self.radius * 2, self.radius * 2))
            # rotate the knob image by angle
            rotated = pygame.transform.rotozoom(img, self.angle, 1.0)
            rect = rotated.get_rect(center=self.center)
            screen.blit(rotated, rect)
            pygame.draw.circle(screen, (120, 120, 130),
                               self.center, self.radius, 2)
        else:
            pygame.draw.circle(screen, (240, 240, 245),
                               self.center, self.radius)
            pygame.draw.circle(screen, (120, 120, 130),
                               self.center, self.radius, 2)
        label_surface = font.render(self.label, True, (40, 40, 45))
        value_surface = font.render(self.value_text(), True, (40, 40, 45))
        label_rect = label_surface.get_rect(
            center=(self.center[0], self.center[1] - self.radius - 14))
        value_rect = value_surface.get_rect(
            center=(self.center[0], self.center[1] + self.radius + 10))
        screen.blit(label_surface, label_rect)
        screen.blit(value_surface, value_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            dx = x - self.center[0]
            dy = y - self.center[1]
            if dx * dx + dy * dy <= self.radius * self.radius:
                if self.on_click:
                    self.on_click()
                return True
        return False

    def is_point_over(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        dx = x - self.center[0]
        dy = y - self.center[1]
        return dx * dx + dy * dy <= self.radius * self.radius


def draw_overlay(
        screen: pygame.Surface,
        font: pygame.font.Font,
        title_font: Optional[pygame.font.Font],
        tool_state: ToolState,
        buttons: List[Button],
        knobs: List[Knob],
        info_lines: List[str],
        overlay_rect: pygame.Rect,
        title_text: Optional[str] = None,
) -> None:
    def wrap_text(text: str, max_width: int, max_lines: int = 2) -> List[str]:
        if not text:
            return []
        words = text.split()
        if not words:
            return []
        lines: List[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
                if len(lines) >= max_lines - 1:
                    break
        lines.append(current)
        return lines[:max_lines]

    overlay = pygame.Surface(
        (overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
    overlay.fill((245, 245, 250, 200))
    screen.blit(overlay, overlay_rect.topleft)

    if title_text and title_font:
        title_surface = title_font.render(title_text, True, (40, 40, 45))
        title_rect = title_surface.get_rect(
            center=(overlay_rect.x + overlay_rect.width //
                    2, overlay_rect.y + 52)
        )
        screen.blit(title_surface, title_rect)

    for knob in knobs:
        knob.draw(screen, font)
    for button in buttons:
        active = False
        if getattr(button, "is_active", None):
            try:
                active = button.is_active()
            except Exception:
                active = False
        button.draw(screen, font, active=active)

    swatch_size = 56
    color_swatch = get_color_swatch_rect(overlay_rect, swatch_size)
    # Always show current tool swatch (color or background when erasing)
    pygame.draw.rect(screen, tool_state.color(), color_swatch, border_radius=6)
    pygame.draw.rect(screen, (60, 60, 70), color_swatch, 2, border_radius=6)
    label_surface = font.render("Current Color", True, (40, 40, 45))
    label_rect = label_surface.get_rect(
        center=(color_swatch.centerx, color_swatch.top - 14))
    screen.blit(label_surface, label_rect)

    info_y = color_swatch.bottom + 10
    max_text_width = overlay_rect.width - 44
    line_index = 0
    for line in info_lines:
        for wrapped in wrap_text(line, max_text_width):
            text_surface = font.render(wrapped, True, (40, 40, 45))
            text_rect = text_surface.get_rect(
                midtop=(overlay_rect.centerx, info_y + line_index * 20)
            )
            screen.blit(text_surface, text_rect)
