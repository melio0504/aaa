import math
from pathlib import Path

import pygame


class Boat:
	def __init__(self, pos, color, name=""):
		self.pos = pygame.Vector2(pos)
		self.prev_pos = pygame.Vector2(pos)
		self.vel = pygame.Vector2(0, 0)
		self.angle = 0.0
		self.color = color
		self.name = name

		self.max_speed = 320.0
		self.accel = 260.0
		self.drag = 1.6
		self.turn_rate = 160.0
		self.lateral_drag = 4.0

		self.size = 18
		self.laps = 0
		self.gate_index = 0
		self.hit_wall_timer = 0.0

		asset_path = Path(__file__).resolve().parent.parent / "assets" / "images" / "boat.png"
		self.sprite = None
		if asset_path.exists():
			try:
				image = pygame.image.load(str(asset_path)).convert_alpha()
				image = pygame.transform.flip(image, False, True)
				self.sprite = pygame.transform.smoothscale(image, (72, 72))
			except pygame.error:
				self.sprite = None

	def update(self, dt, throttle, steer):
		self.prev_pos = self.pos.copy()

		forward = pygame.Vector2(0, -1).rotate(-self.angle)
		speed = self.vel.length()
		speed_ratio = 0.0 if self.max_speed == 0 else min(1.0, speed / self.max_speed)

		if abs(steer) > 0.001 and speed > 5.0:
			self.angle -= steer * self.turn_rate * (0.4 + 0.6 * speed_ratio) * dt

		if abs(throttle) > 0.001:
			self.vel += forward * (throttle * self.accel * dt)

		if self.drag > 0:
			self.vel *= max(0.0, 1.0 - self.drag * dt)

		right = forward.rotate(90)
		lateral_speed = self.vel.dot(right)
		self.vel -= right * lateral_speed * min(1.0, self.lateral_drag * dt)

		if self.vel.length() > self.max_speed:
			self.vel.scale_to_length(self.max_speed)

		self.pos += self.vel * dt

	def draw(self, surface):
		if self.sprite is not None:
			rotated = pygame.transform.rotozoom(self.sprite, -self.angle, 1.0)
			rect = rotated.get_rect(center=(int(self.pos.x), int(self.pos.y)))
			surface.blit(rotated, rect)
			return

		nose = pygame.Vector2(0, -self.size)
		rear_left = pygame.Vector2(-self.size * 0.55, self.size * 0.6)
		rear_right = pygame.Vector2(self.size * 0.55, self.size * 0.6)
		points = [nose, rear_left, rear_right]
		rotated = [p.rotate(-self.angle) + self.pos for p in points]
		pygame.draw.polygon(surface, self.color, rotated)
		pygame.draw.polygon(surface, (20, 20, 30), rotated, 2)

	def get_speed(self):
		return self.vel.length()
