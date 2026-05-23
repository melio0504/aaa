from __future__ import annotations
import pygame

from dataclasses import dataclass
from typing import Tuple, Union

Color = Union[Tuple[int, int, int], Tuple[int, int, int, int]]


@dataclass
class CanvasConfig:
    width: int
    height: int
    background: Color
    display_size: Tuple[int, int]


class Canvas:
    def __init__(self, config: CanvasConfig) -> None:
        self.config = config
        self.surface = pygame.Surface(
            (config.width, config.height), pygame.SRCALPHA)
        self.clear()
        self.display_size = config.display_size

    def clear(self) -> None:
        self.surface.fill(self.config.background)

    def draw_line(
            self,
            start: Tuple[int, int],
            end: Tuple[int, int],
            color: Color,
            thickness: int,
    ) -> None:
        if start == end:
            size = max(1, thickness)
            half = size // 2
            rect = pygame.Rect(start[0] - half, start[1] - half, size, size)
            pygame.draw.rect(self.surface, color, rect)
            return
        pygame.draw.line(self.surface, color, start, end, max(1, thickness))

    def blit_to(self, screen: pygame.Surface, offset: Tuple[int, int]) -> None:
        scaled = pygame.transform.scale(self.surface, self.display_size)
        screen.blit(scaled, offset)

    def save(self, path: str) -> None:
        scaled = pygame.transform.scale(self.surface, self.display_size)
        pygame.image.save(scaled, path)

    def load(self, path: str) -> bool:
        try:
            loaded = pygame.image.load(path).convert_alpha()
        except pygame.error:
            return False
        if loaded.get_size() != self.surface.get_size():
            loaded = pygame.transform.scale(loaded, self.surface.get_size())
        self.surface.blit(loaded, (0, 0))
        return True
