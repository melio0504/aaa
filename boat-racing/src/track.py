import pygame


class Track:
	def __init__(self, width, height):
		horizontal_margin = 70
		vertical_margin = 170
		self.track_rect = pygame.Rect(
			horizontal_margin,
			vertical_margin,
			width - horizontal_margin * 2,
			height - vertical_margin * 2,
		)
		self.center_line_y = self.track_rect.centery

		self.gate_radius = 42
		gate_count = 7
		left_edge = self.track_rect.left + 180
		right_edge = self.track_rect.right - 120
		step = (right_edge - left_edge) / (gate_count - 1)
		self.gates = [pygame.Vector2(left_edge + step * idx, self.center_line_y) for idx in range(gate_count)]
		self.finish_x = self.track_rect.right - 60

		self.start_positions = [
			(self.track_rect.left + 120, self.center_line_y - 90),
			(self.track_rect.left + 120, self.center_line_y + 90),
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

	def draw(self, surface):
		surface.fill((10, 40, 70))
		pygame.draw.rect(surface, (28, 100, 140), self.track_rect)
		pygame.draw.rect(surface, (225, 225, 230), self.track_rect, 4)

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

		for gate in self.gates:
			pygame.draw.circle(surface, (240, 200, 90), gate, self.gate_radius, 3)

