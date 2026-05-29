import os

import pygame


class Track:
	def __init__(self, width, height):
		assets_root = os.path.abspath(
			os.path.join(os.path.dirname(__file__), "..", "assets", "images")
		)
		self.water_tile = pygame.image.load(
			os.path.join(assets_root, "water.png")
		).convert_alpha()

		margin = max(60, int(min(width, height) * 0.12))
		track_width = width
		track_height = max(160, height - margin * 2)
		track_height = min(track_height, height - 40)
		track_left = 0
		track_top = (height - track_height) // 2
		self.track_rect = pygame.Rect(track_left, track_top, track_width, track_height)
		self.center_line_y = self.track_rect.centery

		self.gate_radius = 42
		gate_count = 7
		left_edge = self.track_rect.left + 180
		right_edge = self.track_rect.right - 120
		step = (right_edge - left_edge) / (gate_count - 1)
		self.gates = [pygame.Vector2(left_edge + step * idx, self.center_line_y) for idx in range(gate_count)]
		self.finish_x = self.track_rect.right - 60

		lane_offset = max(40, int(track_height * 0.25))
		lane_limit = max(10, track_height // 2 - 10)
		lane_offset = min(lane_offset, lane_limit)
		self.start_positions = [
			(self.track_rect.left + 120, self.center_line_y - lane_offset),
			(self.track_rect.left + 120, self.center_line_y + lane_offset),
		]
		self.start_angle = -90.0

	def is_on_track(self, pos):
		return self.track_rect.collidepoint(pos.x, pos.y)

	def resolve_collision(self, boat):
		if self.is_on_track(boat.pos):
			return
		boat.pos = boat.prev_pos.copy()
		boat.vel *= 0.45
		boat.hit_wall_timer = max(boat.hit_wall_timer, 0.6)

	def get_gate_count(self):
		return len(self.gates)

	def get_gate_position(self, gate_index):
		if not self.gates:
			return pygame.Vector2(self.track_rect.center)
		return self.gates[gate_index % len(self.gates)]

	def get_track_pressure(self, pos):
		return 0.0, 0.0

	def crossed_gate(self, boat):
		gate_pos = self.get_gate_position(boat.gate_index)
		was_outside = boat.prev_pos.distance_to(gate_pos) > self.gate_radius
		is_inside = boat.pos.distance_to(gate_pos) <= self.gate_radius
		return was_outside and is_inside

	def _tile_texture(self, surface, image, rect):
		img_w, img_h = image.get_width(), image.get_height()
		if img_w <= 0 or img_h <= 0:
			return
		previous_clip = surface.get_clip()
		surface.set_clip(rect)
		start_x = rect.left - (rect.left % img_w)
		start_y = rect.top - (rect.top % img_h)
		for y in range(start_y, rect.bottom, img_h):
			for x in range(start_x, rect.right, img_w):
				surface.blit(image, (x, y))
		surface.set_clip(previous_clip)

	def draw(self, surface):
		# Green surroundings with water texture only inside the track rectangle.
		surface.fill((18, 64, 26))
		self._tile_texture(surface, self.water_tile, self.track_rect)
		pygame.draw.rect(surface, (220, 235, 220), self.track_rect, 3)

		lane_color = (220, 230, 240)
		start = (self.track_rect.left + 30, self.center_line_y)
		end = (self.track_rect.right - 30, self.center_line_y)
		pygame.draw.line(surface, lane_color, start, end, 2)

		finish_x = self.finish_x
		pygame.draw.line(
			surface,
			(250, 250, 250),
			(finish_x, self.track_rect.top + 20),
			(finish_x, self.track_rect.bottom - 20),
			5,
		)

		flag_width = 36
		flag_height = 24
		flag_x = finish_x + 8
		flag_y = self.track_rect.top + 18
		pole_top = (finish_x, flag_y - 4)
		pole_bottom = (finish_x, flag_y + flag_height + 6)
		pygame.draw.line(surface, (20, 20, 20), pole_top, pole_bottom, 3)

		cell_w = flag_width // 4
		cell_h = flag_height // 3
		for row in range(3):
			for col in range(4):
				color = (15, 15, 15) if (row + col) % 2 == 0 else (245, 245, 245)
				rect = pygame.Rect(
					flag_x + col * cell_w,
					flag_y + row * cell_h,
					cell_w,
					cell_h,
				)
				pygame.draw.rect(surface, color, rect)
		pygame.draw.rect(
			surface,
			(10, 10, 10),
			pygame.Rect(flag_x, flag_y, flag_width, flag_height),
			1,
		)

		# Gates remain for logic, but visuals are removed per request.

