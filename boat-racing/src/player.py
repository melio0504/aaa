import random

import pygame


class Player:
	def __init__(self, boat, controls):
		self.boat = boat
		self.controls = controls
		self.paddle_power = 0.0
		self._last_left = False
		self._last_right = False

	def reset_input(self):
		self.paddle_power = 0.0
		self._last_left = False
		self._last_right = False

	def _is_pressed(self, keys, mapping):
		if isinstance(mapping, (list, tuple, set)):
			return any(keys[key] for key in mapping)
		return keys[mapping]

	def update(self, dt, keys, track):
		left_pressed = self._is_pressed(keys, self.controls["paddle_left"])
		right_pressed = self._is_pressed(keys, self.controls["paddle_right"])

		if left_pressed and not self._last_left:
			self.paddle_power += 0.22
		if right_pressed and not self._last_right:
			self.paddle_power += 0.22

		self._last_left = left_pressed
		self._last_right = right_pressed

		decay = 2.5 if not (left_pressed or right_pressed) else 0.8
		self.paddle_power = max(0.0, self.paddle_power - decay * dt)
		throttle = min(1.0, self.paddle_power)
		self.boat.update(dt, throttle, 0.0)

	def draw(self, surface):
		self.boat.draw(surface)


class AIPlayer:
	def __init__(self, boat):
		self.boat = boat
		self.base_throttle = random.uniform(0.7, 1.0)

	def reset_speed(self):
		self.base_throttle = random.uniform(0.7, 1.0)

	def update(self, dt, keys, track):
		jitter = random.uniform(-0.08, 0.08)
		throttle = max(0.2, min(1.0, self.base_throttle + jitter))
		self.boat.update(dt, throttle, 0.0)

	def draw(self, surface):
		self.boat.draw(surface)
