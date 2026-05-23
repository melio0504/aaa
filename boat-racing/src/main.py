import sys

import pygame

from boat import Boat
from player import AIPlayer, Player
from track import Track


def draw_hud(surface, font, timer_font, players, elapsed, scores, target_wins):
	y = 10
	for idx, player in enumerate(players, start=1):
		boat = player.boat
		name = boat.name or f"P{idx}"
		text = f"{name} Speed {boat.get_speed():.0f}"
		label = font.render(text, True, boat.color)
		surface.blit(label, (12, y))
		y += 26

	timer_text = f"Time {elapsed:0.1f}s"
	timer_label = timer_font.render(timer_text, True, (230, 230, 230))
	surface.blit(timer_label, (12, y + 6))

	score_text = f"Score {scores['You']}-{scores['CPU']} (first to {target_wins})"
	score_label = font.render(score_text, True, (230, 230, 230))
	surface.blit(score_label, (surface.get_width() - score_label.get_width() - 12, 10))


def draw_button(surface, font, rect, text, is_hovered):
	fill = (70, 120, 160) if is_hovered else (50, 90, 130)
	border = (220, 230, 240)
	pygame.draw.rect(surface, fill, rect, border_radius=6)
	pygame.draw.rect(surface, border, rect, 2, border_radius=6)
	label = font.render(text, True, (240, 240, 240))
	surface.blit(
		label,
		(rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2),
	)


def draw_overlay(surface, title_font, body_font, message, buttons, mouse_pos):
	overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
	overlay.fill((5, 10, 20, 180))
	surface.blit(overlay, (0, 0))

	title_label = title_font.render(message, True, (250, 235, 170))
	surface.blit(
		title_label,
		(surface.get_width() // 2 - title_label.get_width() // 2, surface.get_height() // 2 - 140),
	)

	for rect, text in buttons:
		draw_button(surface, body_font, rect, text, rect.collidepoint(mouse_pos))


def main():
	pygame.init()
	pygame.display.set_caption("Boat Racing")

	width, height = 1280, 720
	screen = pygame.display.set_mode((width, height))
	clock = pygame.time.Clock()

	track = Track(width, height)
	boat1 = Boat(track.start_positions[0], (230, 80, 70), name="You")
	boat2 = Boat(track.start_positions[1], (80, 180, 230), name="CPU")
	boat1.angle = track.start_angle
	boat2.angle = track.start_angle

	players = [
		Player(
			boat1,
			{
				"paddle_left": pygame.K_a,
				"paddle_right": pygame.K_d,
			},
		),
		AIPlayer(boat2),
	]
	player1 = players[0]
	ai_player = players[1]

	def reset_round():
		boat1.pos = pygame.Vector2(track.start_positions[0])
		boat2.pos = pygame.Vector2(track.start_positions[1])
		boat1.prev_pos = boat1.pos.copy()
		boat2.prev_pos = boat2.pos.copy()
		boat1.vel.update(0, 0)
		boat2.vel.update(0, 0)
		boat1.angle = track.start_angle
		boat2.angle = track.start_angle
		boat1.laps = 0
		boat2.laps = 0
		boat1.gate_index = 0
		boat2.gate_index = 0
		boat1.hit_wall_timer = 0.0
		boat2.hit_wall_timer = 0.0
		player1.reset_input()
		ai_player.reset_speed()

	def reset_match():
		reset_round()
		return {"You": 0, "CPU": 0}

	def begin_round():
		nonlocal countdown_start, state
		reset_round()
		countdown_start = pygame.time.get_ticks()
		state = "countdown"

	font = pygame.font.SysFont("Arial", 20)
	timer_font = pygame.font.SysFont("Arial", 30)
	title_font = pygame.font.SysFont("Arial", 44)
	button_font = pygame.font.SysFont("Arial", 24)
	countdown_font = pygame.font.SysFont("Arial", 84)
	win_target = 3
	start_ticks = pygame.time.get_ticks()
	state = "menu"
	scores = {"You": 0, "CPU": 0}
	result_message = ""
	countdown_start = 0
	countdown_seconds = 3

	running = True
	while running:
		dt = clock.tick(60) / 1000.0
		if state in ("playing", "round_over"):
			elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
		else:
			elapsed = 0.0

		mouse_pos = pygame.mouse.get_pos()
		menu_buttons = [
			(pygame.Rect(width // 2 - 140, height // 2 - 10, 280, 52), "Start"),
			(pygame.Rect(width // 2 - 140, height // 2 + 58, 280, 52), "Quit"),
		]
		round_over_buttons = [
			(pygame.Rect(width // 2 - 160, height // 2 - 10, 320, 52), "Next Round"),
			(pygame.Rect(width // 2 - 160, height // 2 + 58, 320, 52), "Restart Match"),
			(pygame.Rect(width // 2 - 160, height // 2 + 126, 320, 52), "Main Menu"),
		]
		result_buttons = [
			(pygame.Rect(width // 2 - 160, height // 2 + 10, 320, 52), "Restart Match"),
			(pygame.Rect(width // 2 - 160, height // 2 + 78, 320, 52), "Main Menu"),
		]

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and state in ("playing", "round_over"):
				begin_round()
			elif event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
				if state == "round_over":
					begin_round()
				elif state == "menu":
					scores = reset_match()
					begin_round()
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if state == "menu":
					if menu_buttons[0][0].collidepoint(event.pos):
						scores = reset_match()
						begin_round()
					elif menu_buttons[1][0].collidepoint(event.pos):
						running = False
				elif state == "round_over":
					if round_over_buttons[0][0].collidepoint(event.pos):
						begin_round()
					elif round_over_buttons[1][0].collidepoint(event.pos):
						scores = reset_match()
						begin_round()
					elif round_over_buttons[2][0].collidepoint(event.pos):
						state = "menu"
				elif state == "match_over":
					if result_buttons[0][0].collidepoint(event.pos):
						scores = reset_match()
						begin_round()
					elif result_buttons[1][0].collidepoint(event.pos):
						state = "menu"

		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			running = False


		if state == "countdown":
			remaining = countdown_seconds - (pygame.time.get_ticks() - countdown_start) / 1000.0
			if remaining <= 0:
				start_ticks = pygame.time.get_ticks()
				state = "playing"
		elif state == "playing":
			for player in players:
				player.update(dt, keys, track)
				track.resolve_collision(player.boat)

			if boat1.pos.x >= track.finish_x:
				scores["You"] += 1
				result_message = "You win the round!"
				state = "match_over" if scores["You"] >= win_target else "round_over"
			elif boat2.pos.x >= track.finish_x:
				scores["CPU"] += 1
				result_message = "You lose the round!"
				state = "match_over" if scores["CPU"] >= win_target else "round_over"

		track.draw(screen)
		for player in players:
			player.draw(screen)
		draw_hud(screen, font, timer_font, players, elapsed, scores, win_target)

		if state == "menu":
			draw_overlay(screen, title_font, button_font, "Boat Racing", menu_buttons, mouse_pos)
		elif state == "countdown":
			remaining = max(0, countdown_seconds - (pygame.time.get_ticks() - countdown_start) / 1000.0)
			count_label = countdown_font.render(str(int(remaining) + 1), True, (250, 235, 170))
			screen.blit(
				count_label,
				(width // 2 - count_label.get_width() // 2, height // 2 - count_label.get_height() // 2),
			)
		elif state == "round_over":
			draw_overlay(screen, title_font, button_font, result_message, round_over_buttons, mouse_pos)
		elif state == "match_over":
			final_message = "You win the match!" if scores["You"] >= win_target else "You lose the match!"
			draw_overlay(screen, title_font, button_font, final_message, result_buttons, mouse_pos)

		pygame.display.flip()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	main()
