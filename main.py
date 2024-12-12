# Snake Game with Grappling Hook

import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game Variables
snake_pos = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = (0, -1)  # Start moving upwards
hook_length = 1
max_hook_length = 10
points = [(random.randint(2, GRID_WIDTH - 3),
           random.randint(2, GRID_HEIGHT - 3))]
score = 0

# Game Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Self-Playing Snake with Grappling Hook')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def get_closest_point(head, points):
    closest = None
    min_dist = float('inf')
    for point in points:
        dist = distance(head, point)
        if dist < min_dist:
            closest = point
            min_dist = dist
    return closest, min_dist


def is_safe_move(new_pos, snake_pos):
    # Check if move would hit wall
    if (new_pos[0] < 1 or new_pos[0] >= GRID_WIDTH - 1 or
            new_pos[1] < 1 or new_pos[1] >= GRID_HEIGHT - 1):
        return False
    # Check if move would hit snake
    if new_pos in snake_pos:
        return False
    return True


def get_best_direction(head, target, current_direction, snake_pos, hook_length):
    if not target:
        return current_direction

    # Calculate distances
    dx = target[0] - head[0]
    dy = target[1] - head[1]
    dist_to_target = math.sqrt(dx*dx + dy*dy)

    # If target is within hook range, move directly towards it
    if dist_to_target <= hook_length:
        possible_moves = []

        # Try horizontal movement
        if dx != 0:
            dir_x = (1 if dx > 0 else -1, 0)
            if is_safe_move((head[0] + dir_x[0], head[1] + dir_x[1]), snake_pos):
                possible_moves.append(dir_x)

        # Try vertical movement
        if dy != 0:
            dir_y = (0, 1 if dy > 0 else -1)
            if is_safe_move((head[0] + dir_y[0], head[1] + dir_y[1]), snake_pos):
                possible_moves.append(dir_y)

        # If we have possible moves, choose the one that gets us closer
        if possible_moves:
            best_move = min(possible_moves,
                            key=lambda m: distance((head[0] + m[0], head[1] + m[1]), target))
            return best_move

    # If target is not in range or we can't move directly towards it,
    # try to get closer while avoiding obstacles
    possible_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    best_direction = current_direction
    min_distance = float('inf')

    for direction in possible_directions:
        new_pos = (head[0] + direction[0], head[1] + direction[1])
        if is_safe_move(new_pos, snake_pos):
            dist = distance(new_pos, target)
            if dist < min_distance:
                min_distance = dist
                best_direction = direction

    return best_direction


def draw_hook_range(screen, head, hook_length):
    # Draw semi-transparent circle showing hook range
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(surface, (0, 0, 255, 50),
                       (head[0] * GRID_SIZE + GRID_SIZE // 2,
                       head[1] * GRID_SIZE + GRID_SIZE // 2),
                       hook_length * GRID_SIZE)
    screen.blit(surface, (0, 0))


# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get current state
    head = snake_pos[0]
    closest_point, dist_to_closest = get_closest_point(head, points)
    target = closest_point if dist_to_closest <= hook_length else None

    # Determine direction using improved AI
    snake_direction = get_best_direction(
        head, closest_point, snake_direction, snake_pos, hook_length)

    # Move Snake
    new_head = (head[0] + snake_direction[0], head[1] + snake_direction[1])

    # Check for Wall Collision
    if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
        print(f"Game Over! Final Score: {score}")
        running = False
    else:
        # Check for self-collision
        if new_head in snake_pos:
            print(f"Game Over! Final Score: {score}")
            running = False
        else:
            snake_pos = [new_head] + snake_pos[:-1]

            # Check for Point Collection with Grappling Hook
            if target:
                points.remove(target)
                hook_length = min(hook_length + 1, max_hook_length)
                score += 1
                # Spawn new point away from walls and current snake position
                while True:
                    new_point = (random.randint(2, GRID_WIDTH - 3),
                                 random.randint(2, GRID_HEIGHT - 3))
                    if new_point not in snake_pos:
                        points.append(new_point)
                        break

    # Draw Everything
    screen.fill(BLACK)

    # Draw hook range
    draw_hook_range(screen, head, hook_length)

    # Draw border
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 2)

    # Draw Snake
    for pos in snake_pos:
        pygame.draw.rect(
            screen, GREEN, (pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2))

    # Draw Points
    for point in points:
        pygame.draw.circle(
            screen, RED, (point[0] * GRID_SIZE + GRID_SIZE // 2,
                          point[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)

    # Draw Grappling Hook
    if target:
        # Draw retracting animation
        hook_progress = 0.0
        while hook_progress <= 1.0:
            screen.fill(BLACK)
            draw_hook_range(screen, head, hook_length)

            # Draw border
            pygame.draw.rect(
                screen, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 2)

            # Redraw snake and points
            for pos in snake_pos:
                pygame.draw.rect(
                    screen, GREEN, (pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2))
            for p in points:
                pygame.draw.circle(
                    screen, RED, (p[0] * GRID_SIZE + GRID_SIZE // 2,
                                  p[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)

            # Calculate hook position
            start_pos = (head[0] * GRID_SIZE + GRID_SIZE // 2,
                         head[1] * GRID_SIZE + GRID_SIZE // 2)
            end_pos = (target[0] * GRID_SIZE + GRID_SIZE // 2,
                       target[1] * GRID_SIZE + GRID_SIZE // 2)
            current_x = start_pos[0] + \
                (end_pos[0] - start_pos[0]) * hook_progress
            current_y = start_pos[1] + \
                (end_pos[1] - start_pos[1]) * hook_progress

            # Draw hook line
            pygame.draw.line(screen, BLUE, start_pos,
                             (current_x, current_y), 3)

            # Draw hook head
            pygame.draw.circle(
                screen, YELLOW, (int(current_x), int(current_y)), 5)

            # Draw Score and Hook Length
            score_text = font.render(f'Score: {score}', True, WHITE)
            hook_text = font.render(f'Hook Length: {hook_length}', True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(hook_text, (10, 50))

            hook_progress += 0.2
            pygame.display.flip()
            pygame.time.delay(30)

    # Draw Score and Hook Length
    score_text = font.render(f'Score: {score}', True, WHITE)
    hook_text = font.render(f'Hook Length: {hook_length}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(hook_text, (10, 50))

    pygame.display.flip()

    # Control Game Speed
    clock.tick(5)

pygame.quit()
