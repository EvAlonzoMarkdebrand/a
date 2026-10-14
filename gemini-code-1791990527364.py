import pygame
import sys
import math
import random

# ==============================================================================
# INICIALIZACIÓN Y CONFIGURACIÓN DEL SISTEMA
# ==============================================================================
pygame.init()
WIDTH, HEIGHT = 1240, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER SMASH ARENA - Advanced Fighting Engine")
clock = pygame.time.Clock()
FPS = 60

# Sistema de Audio Seguro (con respaldo silencioso si no hay dispositivo de audio)
AUDIO_ENABLED = False
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except Exception:
    AUDIO_ENABLED = False


# ==============================================================================
# FUENTES DEL SISTEMA (Sin advertencias y con respaldo seguro)
# ==============================================================================
AVAILABLE_FONTS = set(pygame.font.get_fonts()) if pygame.font.get_init() else set()


def create_font(size, bold=False):
    candidate_fonts = ["impact", "arial", "dejavusans", "liberationsans", "sans", "helvetica"]
    for name in candidate_fonts:
        if name in AVAILABLE_FONTS:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    return f
            except Exception:
                pass
    return pygame.font.Font(None, size)


FONT_TITLE = create_font(54, bold=True)
FONT_BIG = create_font(84, bold=True)
FONT_UI = create_font(40, bold=True)
FONT_MED = create_font(24, bold=True)
FONT_SMALL = create_font(17, bold=True)
FONT_TINY = create_font(13, bold=False)
FONT_DMG = create_font(26, bold=True)


# ==============================================================================
# PALETA DE COLORES NEÓN Y CYBERPUNK
# ==============================================================================
BG_TOP = (6, 8, 20)
BG_BOT = (22, 10, 42)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (140, 150, 180)
DARK_GRAY = (28, 32, 52)
YELLOW = (255, 235, 60)
ORANGE = (255, 140, 30)
RED_NEON = (255, 35, 75)
GREEN_NEON = (40, 255, 150)
CYAN_NEON = (0, 235, 255)
PURPLE_NEON = (180, 70, 255)
GOLD = (255, 205, 45)
STAGE_COLOR = (26, 30, 54)
STAGE_NEON = (110, 85, 250)

# Límites de muerte (Blast Zones en coordenadas del mundo)
BLAST_LEFT = -340
BLAST_RIGHT = WIDTH + 340
BLAST_TOP = -360
BLAST_BOTTOM = HEIGHT + 300


# ==============================================================================
# DATOS DE LOS PERSONAJES (4 Luchadores con Habilidades y Roles Únicos)
# ==============================================================================
CHARACTERS = {
    "NEXUS": {
        "name": "CYBER NEXUS",
        "tag": "NEXUS",
        "role": "ALL-ROUNDER (Táctico)",
        "color": (0, 230, 255),
        "accent": (255, 255, 255),
        "scarf": (0, 200, 255),
        "desc": "Equilibrado con corte cibernético de alta precisión, proyectiles rápidos y contraataque con parry.",
        "speed": 8.0,
        "accel": 1.45,
        "weight": 1.0,         # Peso medio estándar
        "jump_power": 14.8,
        "max_shield": 100.0,
        "specials": {
            "neutral": "Plasma Dart (Disparo láser veloz)",
            "side": "Cyber Dash (Corte deslizante penetrante)",
            "up": "Vector Thruster (Propulsión ascendente doble)",
            "down": "Matrix Parry (Postura de contraataque crítico)"
        },
        "stats": {"vel": 80, "pot": 78, "pes": 72, "rec": 84}
    },
    "VALKYRIE": {
        "name": "SOLAR VALKYRIE",
        "tag": "VALKYRIE",
        "role": "RUSHDOWN (Veloz e Ígnea)",
        "color": (255, 50, 110),
        "accent": (255, 220, 60),
        "scarf": (255, 120, 40),
        "desc": "Combatiente aérea ultra veloz con patadas en llamas, proyectiles solares y estallido supernova.",
        "speed": 9.4,
        "accel": 1.75,
        "weight": 0.86,        # Más ligera (vuela más lejos)
        "jump_power": 15.6,
        "max_shield": 92.0,
        "specials": {
            "neutral": "Solar Flare (Esfera ígnea ardiente)",
            "side": "Blazing Dive (Patada propulsada en picada)",
            "up": "Phoenix Spiral (Ascenso en torbellino solar)",
            "down": "Supernova Burst (Estallido radial repulsor)"
        },
        "stats": {"vel": 96, "pot": 82, "pes": 60, "rec": 92}
    },
    "GOLIATH": {
        "name": "TITAN GOLIATH",
        "tag": "GOLIATH",
        "role": "HEAVY BRUISER (Coloso)",
        "color": (170, 60, 255),
        "accent": (255, 150, 25),
        "scarf": (120, 35, 210),
        "desc": "Tanque pesado con armadura, orbes de gravedad densos, embestida imparable y terremoto sísmico.",
        "speed": 6.3,
        "accel": 1.15,
        "weight": 1.42,        # Muy pesado (resiste alto porcentaje)
        "jump_power": 13.8,
        "max_shield": 125.0,
        "specials": {
            "neutral": "Void Singularity (Orbe de gravedad pesado)",
            "side": "Colossus Charge (Embestida con hiperarmadura)",
            "up": "Graviton Leap (Salto titánico con impacto)",
            "down": "Seismic Slam (Terremoto con doble fisura)"
        },
        "stats": {"vel": 58, "pot": 98, "pes": 98, "rec": 64}
    },
    "PHANTOM": {
        "name": "PHANTOM VOID",
        "tag": "PHANTOM",
        "role": "TRICKSTER (Ninja Espectral)",
        "color": (0, 255, 160),
        "accent": (20, 200, 240),
        "scarf": (0, 180, 120),
        "desc": "Acróbata etéreo con shurikens de plasma, teletransporte instantáneo en 8 sentidos y señuelo evasivo.",
        "speed": 8.7,
        "accel": 1.55,
        "weight": 0.90,
        "jump_power": 15.2,
        "max_shield": 95.0,
        "specials": {
            "neutral": "Shadow Shurikens (Doble shuriken veloz)",
            "side": "Shadow Blink (Teletransporte horizontal cortante)",
            "up": "Dimensional Warp (Vuelo etéreo omnidireccional)",
            "down": "Decoy Vanish (Esquive con señuelo de humo)"
        },
        "stats": {"vel": 88, "pot": 74, "pes": 65, "rec": 98}
    }
}


# ==============================================================================
# CÁMARA DINÁMICA CON ZOOM, SHAKE Y SEGUIMIENTO CINEMÁTICO
# ==============================================================================
class Camera:
    def __init__(self):
        self.focus_x = WIDTH / 2.0
        self.focus_y = HEIGHT / 2.0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.shake = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.flash_frames = 0
        self.kill_pos = None

    def add_shake(self, amount):
        self.shake = max(self.shake, float(amount))

    def trigger_kill_flash(self, x, y):
        self.flash_frames = 15
        self.kill_pos = (x, y)
        self.add_shake(30)

    def update(self, fighters):
        alive_fighters = [f for f in fighters if f.stocks > 0]
        if not alive_fighters:
            return

        if self.flash_frames > 0:
            self.flash_frames -= 1
            if self.kill_pos:
                self.focus_x += (self.kill_pos[0] - self.focus_x) * 0.28
                self.focus_y += (self.kill_pos[1] - self.focus_y) * 0.28
                self.zoom += (1.32 - self.zoom) * 0.25
        else:
            xs = [f.rect.centerx for f in alive_fighters]
            ys = [f.rect.centery for f in alive_fighters]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            mid_x = (min_x + max_x) / 2.0
            mid_y = (min_y + max_y) / 2.0 - 25

            dist_x = max(260, max_x - min_x)
            dist_y = max(180, max_y - min_y)
            dist = math.hypot(dist_x, dist_y)

            # Zoom suave adaptado a la separación entre luchadores
            self.target_zoom = max(0.82, min(1.18, 1.25 - dist / 1380.0))

            self.focus_x += (mid_x - self.focus_x) * 0.11
            self.focus_y += (mid_y - self.focus_y) * 0.11
            self.zoom += (self.target_zoom - self.zoom) * 0.08

        if self.shake > 0.3:
            self.offset_x = random.uniform(-self.shake, self.shake)
            self.offset_y = random.uniform(-self.shake, self.shake)
            self.shake *= 0.85
        else:
            self.shake = 0.0
            self.offset_x = 0.0
            self.offset_y = 0.0

    def apply(self, x, y):
        sx = (x - self.focus_x) * self.zoom + (WIDTH / 2.0) + self.offset_x
        sy = (y - self.focus_y) * self.zoom + (HEIGHT / 2.0) + self.offset_y
        return int(sx), int(sy)

    def scale(self, val):
        return max(1, int(val * self.zoom))


# ==============================================================================
# SISTEMA DE EFECTOS VISUALES (Partículas, Arcos, Ondas, Textos, Hitsparks)
# ==============================================================================
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, gravity=0.0, spark=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.gravity = gravity
        self.spark = spark

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.94
        self.life -= 1

    def draw(self, surf, cam):
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.max_life)
        px, py = cam.apply(self.x, self.y)

        if self.spark:
            tx, ty = cam.apply(self.x - self.vx * 2.5, self.y - self.vy * 2.5)
            w = cam.scale(max(2, self.size * ratio))
            pygame.draw.line(surf, self.color, (px, py), (tx, ty), w)
            pygame.draw.line(surf, WHITE, (px, py), (tx, ty), max(1, w // 2))
        else:
            r = cam.scale(self.size * ratio)
            glow = pygame.Surface((r * 4 + 4, r * 4 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, int(140 * ratio)), (r * 2 + 2, r * 2 + 2), r * 2)
            pygame.draw.circle(glow, (255, 255, 255, int(220 * ratio)), (r * 2 + 2, r * 2 + 2), r)
            surf.blit(glow, (px - r * 2 - 2, py - r * 2 - 2))


class SlashArc:
    def __init__(self, cx, cy, radius, start_ang, end_ang, facing, color, duration=10, thickness=24):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.start_ang = start_ang
        self.end_ang = end_ang
        self.facing = facing
        self.color = color
        self.duration = duration
        self.life = duration
        self.thickness = thickness

    def update(self):
        self.life -= 1

    def draw(self, surf, cam):
        if self.life <= 0:
            return
        ratio = self.life / self.duration
        outer_pts, inner_pts = [], []
        steps = 14
        for i in range(steps + 1):
            t = i / steps
            ang = math.radians(self.start_ang + (self.end_ang - self.start_ang) * t)
            cur_th = math.sin(t * math.pi) * self.thickness * ratio
            ox = self.cx + math.cos(ang) * (self.radius + cur_th) * self.facing
            oy = self.cy - math.sin(ang) * (self.radius + cur_th)
            ix = self.cx + math.cos(ang) * (self.radius - cur_th * 0.4) * self.facing
            iy = self.cy - math.sin(ang) * (self.radius - cur_th * 0.4)
            outer_pts.append(cam.apply(ox, oy))
            inner_pts.append(cam.apply(ix, iy))

        poly = outer_pts + inner_pts[::-1]
        if len(poly) >= 3:
            arc_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(arc_surf, (*self.color, int(200 * ratio)), poly)
            pygame.draw.lines(arc_surf, (255, 255, 255, int(240 * ratio)), False, outer_pts, cam.scale(3))
            surf.blit(arc_surf, (0, 0))


class FloatingText:
    def __init__(self, x, y, text, color, size="med", duration=36):
        self.x = x
        self.y = y
        self.vy = -2.6
        self.text = text
        self.color = color
        self.font = FONT_UI if size == "big" else (FONT_DMG if size == "med" else FONT_SMALL)
        self.life = duration
        self.max_life = duration

    def update(self):
        self.y += self.vy
        self.vy *= 0.93
        self.life -= 1

    def draw(self, surf, cam):
        if self.life <= 0:
            return
        px, py = cam.apply(self.x, self.y)
        ratio = self.life / self.max_life
        txt = self.font.render(self.text, True, self.color)
        txt.set_alpha(int(255 * ratio))
        surf.blit(txt, (px - txt.get_width() // 2, py))


class Shockwave:
    def __init__(self, x, y, color, max_radius=90, speed=7, width=5):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 8.0
        self.max_radius = max_radius
        self.speed = speed
        self.width = width
        self.alive = True

    def update(self):
        self.radius += self.speed
        if self.radius >= self.max_radius:
            self.alive = False

    def draw(self, surf, cam):
        ratio = max(0.0, 1.0 - (self.radius / self.max_radius))
        r = cam.scale(self.radius)
        px, py = cam.apply(self.x, self.y)
        sw_surf = pygame.Surface((r * 2 + 14, r * 2 + 14), pygame.SRCALPHA)
        pygame.draw.circle(
            sw_surf, (*self.color, max(0, int(220 * ratio))),
            (r + 7, r + 7), r, max(1, cam.scale(self.width * ratio))
        )
        surf.blit(sw_surf, (px - r - 7, py - r - 7))


class HitSpark:
    def __init__(self, x, y, color, scale=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.life = 12
        self.max_life = 12
        self.scale = scale

    def update(self):
        self.life -= 1

    def draw(self, surf, cam):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        px, py = cam.apply(self.x, self.y)
        length = cam.scale(42 * self.scale * (1.0 + (1.0 - ratio)))
        width = cam.scale(max(2, 6 * ratio))

        spark_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Cruz destellante cinematográfica
        for angle in (0, math.pi / 2, math.pi / 4, -math.pi / 4):
            dx = math.cos(angle) * length
            dy = math.sin(angle) * length
            pygame.draw.line(spark_surf, (*self.color, int(220 * ratio)),
                             (px - dx, py - dy), (px + dx, py + dy), width)
            pygame.draw.line(spark_surf, (255, 255, 255, int(250 * ratio)),
                             (px - dx * 0.6, py - dy * 0.6), (px + dx * 0.6, py + dy * 0.6), max(1, width // 2))
        surf.blit(spark_surf, (0, 0))


class SkeletalAfterimage:
    def __init__(self, joints, color):
        self.joints = joints.copy()
        self.color = color
        self.life = 14
        self.max_life = 14

    def update(self):
        self.life -= 1

    def draw(self, surf, cam):
        ratio = self.life / self.max_life
        alpha = int(140 * ratio)
        ghost = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        c = (*self.color, alpha)

        def pt(name):
            return cam.apply(*self.joints[name])

        w_limb = cam.scale(6)
        for a, b in [("hip", "l_knee"), ("l_knee", "l_foot"), ("hip", "r_knee"), ("r_knee", "r_foot"),
                     ("shoulder", "l_elbow"), ("l_elbow", "l_hand"), ("shoulder", "r_elbow"), ("r_elbow", "r_hand")]:
            pygame.draw.line(ghost, c, pt(a), pt(b), w_limb)
        pygame.draw.line(ghost, c, pt("hip"), pt("shoulder"), cam.scale(12))
        pygame.draw.circle(ghost, c, pt("head"), cam.scale(10))
        surf.blit(ghost, (0, 0))


class KOBlast:
    def __init__(self, x, y, color):
        self.x = max(0, min(WIDTH, x))
        self.y = max(0, min(HEIGHT, y))
        self.color = color
        self.life = 36
        self.max_life = 36
        cx, cy = WIDTH // 2, HEIGHT // 2
        self.angle = math.atan2(cy - self.y, cx - self.x)

    def update(self):
        self.life -= 1

    def draw(self, surf, cam):
        ratio = self.life / self.max_life
        length = 1100 * math.sin(ratio * math.pi)
        spread = 160 * ratio
        nx, ny = math.cos(self.angle), math.sin(self.angle)
        px, py = -ny, nx
        end_x, end_y = self.x + nx * length, self.y + ny * length

        p1 = cam.apply(self.x + px * 25, self.y + py * 25)
        p2 = cam.apply(self.x - px * 25, self.y - py * 25)
        p3 = cam.apply(end_x - px * spread, end_y - py * spread)
        p4 = cam.apply(end_x + px * spread, end_y + py * spread)

        beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(beam, (*self.color, int(210 * ratio)), [p1, p2, p3, p4])
        pygame.draw.polygon(beam, (255, 255, 255, int(240 * ratio)), [p1, p2,
            cam.apply(end_x - px * spread * 0.35, end_y - py * spread * 0.35),
            cam.apply(end_x + px * spread * 0.35, end_y + py * spread * 0.35)])
        surf.blit(beam, (0, 0))


# ==============================================================================
# PROYECTILES DINÁMICOS
# ==============================================================================
class Projectile:
    def __init__(self, owner, x, y, vx, vy, damage, base_kb, kb_scale, angle, duration, radius, color, p_type="normal"):
        self.owner = owner
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.base_kb = base_kb
        self.kb_scale = kb_scale
        self.angle = angle
        self.duration = duration
        self.radius = radius
        self.color = color
        self.p_type = p_type
        self.alive = True

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), int(self.radius * 2), int(self.radius * 2))

    def update(self, particles):
        self.x += self.vx
        self.y += self.vy
        self.duration -= 1
        if self.duration <= 0:
            self.alive = False

        # Estela de partículas luminosas
        if random.random() < 0.7:
            particles.append(Particle(
                self.x, self.y,
                -self.vx * 0.2 + random.uniform(-1, 1), -self.vy * 0.2 + random.uniform(-1, 1),
                self.color, random.randint(3, 6), 14, spark=True
            ))

    def draw(self, surf, cam):
        px, py = cam.apply(self.x, self.y)
        r = cam.scale(self.radius)
        glow = pygame.Surface((r * 4 + 8, r * 4 + 8), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 160), (r * 2 + 4, r * 2 + 4), r * 2)
        pygame.draw.circle(glow, (255, 255, 255, 240), (r * 2 + 4, r * 2 + 4), r)
        surf.blit(glow, (px - r * 2 - 4, py - r * 2 - 4))


# ==============================================================================
# ESCENARIOS Y PLATAFORMAS CON REBOTES Y LEDGES
# ==============================================================================
class Platform:
    def __init__(self, x, y, w, h, passthrough=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.passthrough = passthrough

    def draw(self, surf, cam):
        x1, y1 = cam.apply(self.rect.left, self.rect.top)
        x2, y2 = cam.apply(self.rect.right, self.rect.bottom)
        w, h = max(1, x2 - x1), max(1, y2 - y1)

        if not self.passthrough:
            # Base cónica inferior del escenario principal
            bx1, by1 = cam.apply(self.rect.left + 90, self.rect.bottom + 110)
            bx2, by2 = cam.apply(self.rect.right - 90, self.rect.bottom + 110)
            pygame.draw.polygon(surf, (18, 20, 38), [(x1, y2), (x2, y2), (bx2, by2), (bx1, by1)])
            pygame.draw.lines(surf, STAGE_NEON, True, [(x1, y2), (x2, y2), (bx2, by2), (bx1, by1)], cam.scale(2))

            pygame.draw.rect(surf, STAGE_COLOR, (x1, y1, w, h), border_radius=cam.scale(8))
            pygame.draw.rect(surf, STAGE_NEON, (x1, y1, w, cam.scale(7)), border_radius=cam.scale(4))
            pygame.draw.rect(surf, (190, 180, 255), (x1, y1, w, h), cam.scale(2), border_radius=cam.scale(8))

            # Esferas luminosas de agarre en los bordes (Ledges)
            pygame.draw.circle(surf, YELLOW, (x1, y1 + cam.scale(4)), cam.scale(5))
            pygame.draw.circle(surf, YELLOW, (x2, y1 + cam.scale(4)), cam.scale(5))
        else:
            pygame.draw.rect(surf, (45, 52, 95), (x1, y1, w, h), border_radius=cam.scale(6))
            pygame.draw.line(surf, (130, 225, 255), (x1 + 4, y1 + 2), (x2 - 4, y1 + 2), cam.scale(3))


class Stage:
    def __init__(self, name, platforms):
        self.name = name
        self.platforms = platforms


def get_default_stage():
    return Stage("CYBER SKYPORT", [
        Platform(260, 490, 720, 44, passthrough=False),
        Platform(320, 360, 170, 14, passthrough=True),
        Platform(750, 360, 170, 14, passthrough=True),
        Platform(530, 245, 180, 14, passthrough=True),
    ])


# ==============================================================================
# HITBOX DE ATAQUE
# ==============================================================================
class AttackHitbox:
    def __init__(self, owner, offset_x, offset_y, w, h, damage, base_kb, kb_scale, angle_deg, duration, is_heavy=False, effect="normal"):
        self.owner = owner
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.w = w
        self.h = h
        self.damage = damage
        self.base_kb = base_kb
        self.kb_scale = kb_scale
        self.angle_deg = angle_deg
        self.duration = duration
        self.max_duration = duration
        self.is_heavy = is_heavy
        self.effect = effect
        self.hit_targets = set()

    def get_rect(self):
        cx = self.owner.rect.centerx + (self.offset_x * self.owner.facing)
        cy = self.owner.rect.centery + self.offset_y
        return pygame.Rect(int(cx - self.w // 2), int(cy - self.h // 2), self.w, self.h)


# ==============================================================================
# CLASE FIGHTER (Física de Combate, Rebotes, Teching, Animación y Habilidades)
# ==============================================================================
class Fighter:
    def __init__(self, player_num, char_id, x, y, is_cpu=False, cpu_difficulty="EQUILIBRADO"):
        self.player_num = player_num
        self.char_id = char_id
        self.data = CHARACTERS[char_id]

        self.spawn_x = x
        self.spawn_y = y
        self.rect = pygame.Rect(x, y, 40, 68)
        self.vx = 0.0
        self.vy = 0.0

        self.name = self.data["name"]
        self.tag = self.data["tag"]
        self.color = self.data["color"]
        self.accent = self.data["accent"]
        self.is_cpu = is_cpu
        self.cpu_difficulty = cpu_difficulty  # "FACIL", "EQUILIBRADO", "EXPERTO"

        self.facing = 1 if player_num == 1 else -1
        self.on_ground = False
        self.jumps_left = 2
        self.up_special_used = False
        self.drop_through_timer = 0
        self.short_hop_window = 0
        self.coyote_timer = 0

        # Ledge Grab (Agarre de borde)
        self.on_ledge = False
        self.ledge_timer = 0

        # Estados de Combate
        self.percentage = 0.0
        self.stocks = 3
        self.hitstun = 0
        self.invincible = 0
        self.attack_cooldown = 0
        self.attack_max_cd = 1
        self.attack_type = None
        self.active_hitbox = None

        # Escudo, Dash y Esquives
        self.shielding = False
        self.shield_hp = self.data["max_shield"]
        self.dash_timer = 0
        self.airdodge_timer = 0
        self.tech_window = 0       # Ventana de 10 frames para hacer Tech al chocar
        self.ui_shake = 0

        # Mecánicas Especiales de Personajes
        self.counter_active = False    # Nexus Down-B
        self.super_armor = False       # Goliath Side-B
        self.invisible_timer = 0       # Phantom Down-B

        # Animación Esquelética Humanoide y Bufanda Física
        self.anim_time = random.uniform(0, 10)
        self.spin_angle = 0.0
        self.squash_stretch = 1.0      # Efecto procedural al saltar o impactar
        self.scarf_nodes = [[float(x), float(y)] for _ in range(7)]
        self.joints = {}
        self.update_skeleton()

        # Input Buffer (Buffer de comandos para no perder pulsaciones)
        self.input_buffer = []

        # Memoria y temporizadores de la CPU
        self.ai_reaction_timer = 0
        self.ai_target_move = (0, 0)
        self.ai_state = "NEUTRAL"
        self.ai_shield_intent = False

    def respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y - 120
        self.vx = 0.0
        self.vy = 0.0
        self.percentage = 0.0
        self.hitstun = 0
        self.invincible = 120
        self.shield_hp = self.data["max_shield"]
        self.active_hitbox = None
        self.attack_type = None
        self.jumps_left = 2
        self.up_special_used = False
        self.on_ledge = False
        self.counter_active = False
        self.super_armor = False
        self.invisible_timer = 0
        self.scarf_nodes = [[float(self.rect.centerx), float(self.rect.centery)] for _ in range(7)]

    def jump(self, particles, shockwaves):
        if self.hitstun > 0 or self.shielding or self.airdodge_timer > 0:
            return

        if self.on_ledge:
            self.on_ledge = False
            self.vy = -14.5
            self.vx = self.facing * 4.2
            self.jumps_left = 1
            self.invincible = 15
            return

        can_jump = (self.jumps_left > 0) or (self.coyote_timer > 0)
        if can_jump:
            pwr = self.data["jump_power"]
            if self.on_ground or self.coyote_timer > 0:
                self.vy = -pwr
                self.short_hop_window = 5
                self.coyote_timer = 0
            else:
                self.vy = -pwr * 0.92
            self.on_ground = False
            self.jumps_left -= 1
            self.squash_stretch = 1.25

            shockwaves.append(Shockwave(self.rect.centerx, self.rect.bottom, self.color, max_radius=44, speed=5, width=3))
            for _ in range(8):
                particles.append(Particle(
                    self.rect.centerx + random.uniform(-15, 15), self.rect.bottom,
                    random.uniform(-4, 4), random.uniform(-1, 2), WHITE, random.randint(3, 6), 15
                ))

    def dash(self, move_dir, particles):
        if self.hitstun > 0 or self.dash_timer > 0 or self.attack_cooldown > 0 or self.on_ledge or self.shielding:
            return
        self.facing = move_dir if move_dir != 0 else self.facing
        speed = self.data["speed"] * 2.2
        self.vx = self.facing * speed
        self.vy *= 0.25
        self.dash_timer = 14
        self.invincible = max(self.invincible, 8)
        for _ in range(12):
            particles.append(Particle(
                self.rect.centerx, self.rect.centery + random.uniform(-18, 18),
                -self.facing * random.uniform(3, 8), random.uniform(-2, 2),
                self.color, 5, 16, spark=True
            ))

    def airdodge(self, dir_x, dir_y, particles):
        if self.on_ground or self.hitstun > 0 or self.airdodge_timer > 0 or self.on_ledge:
            return
        self.airdodge_timer = 22
        self.invincible = 18
        if dir_x != 0 or dir_y != 0:
            length = math.hypot(dir_x, dir_y)
            self.vx = (dir_x / length) * 11.5
            self.vy = (dir_y / length) * 11.5
        else:
            self.vx *= 0.2
            self.vy *= 0.2
        for _ in range(14):
            particles.append(Particle(
                self.rect.centerx, self.rect.centery,
                random.uniform(-4, 4), random.uniform(-4, 4),
                WHITE, 6, 16, spark=True
            ))

    def perform_attack(self, dir_x, dir_y, attack_mode, particles, shockwaves, slash_arcs, projectiles):
        """
        attack_mode:
          - "light": Ataque rápido / Jab / Tilts
          - "heavy": Ataque Fuerte / Smashes
          - "special": Habilidades Especiales únicas del personaje
        """
        if self.hitstun > 0 or self.attack_cooldown > 0 or self.shielding or self.on_ledge or self.airdodge_timer > 0:
            return
        if dir_x != 0:
            self.facing = dir_x

        cx, cy = self.rect.centerx, self.rect.centery

        # ----------------------------------------------------------------------
        # ATAQUES ESPECIALES (Neutral-B, Side-B, Up-B, Down-B)
        # ----------------------------------------------------------------------
        if attack_mode == "special":
            if dir_y < 0:
                # UP-SPECIAL: Recuperación Única de cada Luchador
                if not self.up_special_used:
                    self.attack_type = "uspecial"
                    self.up_special_used = True
                    self.on_ground = False
                    self.attack_cooldown = self.attack_max_cd = 34

                    if self.char_id == "NEXUS":
                        # Vector Thruster
                        self.vy = -18.2
                        self.vx = self.facing * 5.4
                        self.active_hitbox = AttackHitbox(self, 16, -30, 64, 82, damage=14.0, base_kb=10.5, kb_scale=1.38, angle_deg=78, duration=15, is_heavy=True)
                        slash_arcs.append(SlashArc(cx, cy - 14, 56, -45, 120, self.facing, CYAN_NEON, 15))
                        shockwaves.append(Shockwave(cx, self.rect.bottom, CYAN_NEON, 80, 8))

                    elif self.char_id == "VALKYRIE":
                        # Phoenix Spiral
                        self.vy = -19.5
                        self.vx = self.facing * 6.2
                        self.active_hitbox = AttackHitbox(self, 14, -36, 75, 95, damage=15.5, base_kb=11.2, kb_scale=1.45, angle_deg=82, duration=18, is_heavy=True, effect="fire")
                        slash_arcs.append(SlashArc(cx, cy - 20, 65, -60, 150, self.facing, GOLD, 18, thickness=30))
                        shockwaves.append(Shockwave(cx, self.rect.bottom, RED_NEON, 90, 9))

                    elif self.char_id == "GOLIATH":
                        # Graviton Leap (Gran Salto de Poder)
                        self.vy = -17.0
                        self.vx = self.facing * 3.8
                        self.active_hitbox = AttackHitbox(self, 20, -25, 78, 88, damage=16.5, base_kb=11.8, kb_scale=1.52, angle_deg=75, duration=16, is_heavy=True, effect="void")
                        slash_arcs.append(SlashArc(cx, cy - 10, 60, -30, 110, self.facing, PURPLE_NEON, 16, thickness=32))
                        shockwaves.append(Shockwave(cx, self.rect.bottom, PURPLE_NEON, 95, 9))

                    elif self.char_id == "PHANTOM":
                        # Dimensional Warp (Teletransporte Direccional)
                        dx = dir_x if dir_x != 0 else self.facing * 0.5
                        dy = -1.0
                        dist = 175
                        self.rect.centerx += int(dx * dist)
                        self.rect.centery += int(dy * dist)
                        self.vy = -4.0
                        self.vx = dx * 4.0
                        self.invincible = 16
                        self.active_hitbox = AttackHitbox(self, 0, 0, 70, 70, damage=11.0, base_kb=9.5, kb_scale=1.2, angle_deg=65, duration=10, is_heavy=True)
                        shockwaves.append(Shockwave(cx, cy, GREEN_NEON, 75, 9))
                        shockwaves.append(Shockwave(self.rect.centerx, self.rect.centery, GREEN_NEON, 75, 9))

            elif dir_y > 0:
                # DOWN-SPECIAL: Habilidad Táctica
                self.attack_type = "dspecial"
                self.attack_cooldown = self.attack_max_cd = 32

                if self.char_id == "NEXUS":
                    # Matrix Parry / Counter
                    self.counter_active = True
                    self.invincible = 22
                    shockwaves.append(Shockwave(cx, cy, CYAN_NEON, 60, 6, 4))

                elif self.char_id == "VALKYRIE":
                    # Supernova Flare (Explosión radial)
                    self.active_hitbox = AttackHitbox(self, 0, 0, 150, 110, damage=13.0, base_kb=10.8, kb_scale=1.45, angle_deg=35, duration=12, is_heavy=True, effect="fire")
                    shockwaves.append(Shockwave(cx, cy, GOLD, 130, 12, 8))
                    for _ in range(20):
                        ang = random.uniform(0, math.pi * 2)
                        spd = random.uniform(5, 12)
                        particles.append(Particle(cx, cy, math.cos(ang) * spd, math.sin(ang) * spd, RED_NEON, 6, 20, spark=True))

                elif self.char_id == "GOLIATH":
                    # Seismic Slam (Terremoto de doble fisura)
                    self.active_hitbox = AttackHitbox(self, 0, 24, 190, 52, damage=15.0, base_kb=11.4, kb_scale=1.55, angle_deg=85, duration=14, is_heavy=True, effect="void")
                    shockwaves.append(Shockwave(cx - 50, self.rect.bottom, PURPLE_NEON, 90, 9))
                    shockwaves.append(Shockwave(cx + 50, self.rect.bottom, PURPLE_NEON, 90, 9))

                elif self.char_id == "PHANTOM":
                    # Decoy Vanish (Señuelo y humo evasivo)
                    self.invisible_timer = 25
                    self.invincible = 20
                    self.vy = -8.5
                    self.vx = -self.facing * 6.0
                    for _ in range(25):
                        particles.append(Particle(cx, cy, random.uniform(-4, 4), random.uniform(-4, 4), GREEN_NEON, random.randint(5, 12), 24))

            elif dir_x != 0:
                # SIDE-SPECIAL: Embestida o ataque frontal característico
                self.attack_type = "sspecial"
                self.attack_cooldown = self.attack_max_cd = 30

                if self.char_id == "NEXUS":
                    # Cyber Dash Slash
                    self.vx = self.facing * 16.0
                    self.active_hitbox = AttackHitbox(self, 40, -4, 82, 54, damage=12.0, base_kb=9.8, kb_scale=1.3, angle_deg=38, duration=10, is_heavy=True)
                    slash_arcs.append(SlashArc(cx + self.facing * 20, cy, 58, -35, 35, self.facing, CYAN_NEON, 10))

                elif self.char_id == "VALKYRIE":
                    # Blazing Dive
                    self.vx = self.facing * 17.5
                    self.vy = 4.0 if not self.on_ground else 0.0
                    self.active_hitbox = AttackHitbox(self, 44, 4, 86, 55, damage=13.5, base_kb=10.2, kb_scale=1.38, angle_deg=30, duration=11, is_heavy=True, effect="fire")
                    slash_arcs.append(SlashArc(cx, cy, 60, -45, 45, self.facing, GOLD, 11, thickness=26))

                elif self.char_id == "GOLIATH":
                    # Colossus Charge (Super Armor)
                    self.super_armor = True
                    self.vx = self.facing * 13.5
                    self.active_hitbox = AttackHitbox(self, 50, -4, 94, 65, damage=16.0, base_kb=12.0, kb_scale=1.6, angle_deg=32, duration=14, is_heavy=True, effect="void")
                    shockwaves.append(Shockwave(cx + self.facing * 30, cy, PURPLE_NEON, 75, 8))

                elif self.char_id == "PHANTOM":
                    # Shadow Blink
                    self.rect.centerx += self.facing * 145
                    self.active_hitbox = AttackHitbox(self, 0, 0, 75, 60, damage=10.5, base_kb=9.2, kb_scale=1.22, angle_deg=40, duration=8, is_heavy=True)
                    slash_arcs.append(SlashArc(cx, cy, 50, -40, 40, self.facing, GREEN_NEON, 8))
                    shockwaves.append(Shockwave(self.rect.centerx, self.rect.centery, GREEN_NEON, 70, 8))

            else:
                # NEUTRAL-SPECIAL: Proyectiles
                self.attack_type = "nspecial"
                self.attack_cooldown = self.attack_max_cd = 24

                if self.char_id == "NEXUS":
                    # Plasma Dart
                    projectiles.append(Projectile(self, cx + self.facing * 32, cy - 6, self.facing * 16.5, 0,
                                                  damage=8.0, base_kb=7.2, kb_scale=0.85, angle=30, duration=55, radius=7, color=CYAN_NEON))

                elif self.char_id == "VALKYRIE":
                    # Solar Flare
                    projectiles.append(Projectile(self, cx + self.facing * 32, cy - 6, self.facing * 14.0, 0,
                                                  damage=10.5, base_kb=8.2, kb_scale=1.1, angle=35, duration=60, radius=10, color=GOLD, p_type="fire"))

                elif self.char_id == "GOLIATH":
                    # Void Singularity (Lento y denso)
                    projectiles.append(Projectile(self, cx + self.facing * 32, cy - 6, self.facing * 8.5, 0,
                                                  damage=14.0, base_kb=9.8, kb_scale=1.35, angle=45, duration=80, radius=14, color=PURPLE_NEON, p_type="void"))

                elif self.char_id == "PHANTOM":
                    # Double Shadow Shurikens
                    projectiles.append(Projectile(self, cx + self.facing * 32, cy - 12, self.facing * 17.0, -0.6,
                                                  damage=5.0, base_kb=6.0, kb_scale=0.7, angle=25, duration=50, radius=6, color=GREEN_NEON))
                    projectiles.append(Projectile(self, cx + self.facing * 32, cy + 6, self.facing * 17.0, 0.6,
                                                  damage=5.0, base_kb=6.0, kb_scale=0.7, angle=25, duration=50, radius=6, color=GREEN_NEON))

        # ----------------------------------------------------------------------
        # ATAQUES NORMALES LIGEROS (Jab, Up-Tilt, Down-Air, Forward-Tilt)
        # ----------------------------------------------------------------------
        elif attack_mode == "light":
            if dir_y < 0:
                # Up-Tilt / Gancho Antiaéreo
                self.attack_type = "utilt"
                self.attack_cooldown = self.attack_max_cd = 19
                self.active_hitbox = AttackHitbox(self, 8, -42, 74, 52, damage=8.5, base_kb=8.0, kb_scale=1.15, angle_deg=84, duration=9)
                slash_arcs.append(SlashArc(cx, cy - 10, 48, -10, 155, self.facing, self.color, 10))
            elif dir_y > 0 and not self.on_ground:
                # Down-Air: METEOR SMASH (Patada descendente)
                self.attack_type = "dair"
                self.attack_cooldown = self.attack_max_cd = 24
                self.active_hitbox = AttackHitbox(self, 0, 46, 56, 58, damage=13.0, base_kb=9.5, kb_scale=1.42, angle_deg=-90, duration=10, is_heavy=True)
                slash_arcs.append(SlashArc(cx, cy + 14, 46, -30, -150, self.facing, YELLOW, 11))
            elif dir_x != 0:
                # Side-Tilt: Patada lateral rápida
                self.attack_type = "ftilt"
                self.vx = self.facing * 7.2
                self.attack_cooldown = self.attack_max_cd = 18
                self.active_hitbox = AttackHitbox(self, 42, -2, 66, 44, damage=9.5, base_kb=8.4, kb_scale=1.2, angle_deg=34, duration=8)
                slash_arcs.append(SlashArc(cx, cy, 50, -45, 45, self.facing, self.color, 9))
            else:
                # Neutral Jab: Puñetazo relámpago
                self.attack_type = "jab"
                self.attack_cooldown = self.attack_max_cd = 12
                self.active_hitbox = AttackHitbox(self, 35, -6, 54, 36, damage=6.0, base_kb=5.4, kb_scale=0.75, angle_deg=40, duration=6)
                slash_arcs.append(SlashArc(cx + self.facing * 10, cy - 6, 38, -30, 35, self.facing, WHITE, 7))

        # ----------------------------------------------------------------------
        # ATAQUES FUERTES SMASH (Forward Smash, Up Smash, Down Smash)
        # ----------------------------------------------------------------------
        elif attack_mode == "heavy":
            if dir_y < 0:
                # UP SMASH: Uppercut explosivo
                self.attack_type = "usmash"
                self.attack_cooldown = self.attack_max_cd = 32
                self.active_hitbox = AttackHitbox(self, 14, -46, 76, 75, damage=16.0, base_kb=11.2, kb_scale=1.55, angle_deg=88, duration=12, is_heavy=True)
                slash_arcs.append(SlashArc(cx, cy - 18, 58, -30, 160, self.facing, YELLOW, 13, thickness=28))
                shockwaves.append(Shockwave(cx, self.rect.bottom, self.color, 85, 8))
            elif dir_y > 0:
                # DOWN SMASH: Barrido doble explosivo
                self.attack_type = "dsmash"
                self.attack_cooldown = self.attack_max_cd = 33
                self.active_hitbox = AttackHitbox(self, 0, 18, 140, 48, damage=15.0, base_kb=10.8, kb_scale=1.5, angle_deg=28, duration=11, is_heavy=True)
                slash_arcs.append(SlashArc(cx, cy + 16, 64, -15, -165, self.facing, YELLOW, 12, thickness=26))
                shockwaves.append(Shockwave(cx, self.rect.bottom, self.color, 98, 9))
            else:
                # FORWARD SMASH: Puño cargado devastador
                self.attack_type = "fsmash"
                self.vx = self.facing * 5.5
                self.attack_cooldown = self.attack_max_cd = 35
                self.active_hitbox = AttackHitbox(self, 50, -4, 84, 58, damage=18.5, base_kb=11.8, kb_scale=1.7, angle_deg=32, duration=11, is_heavy=True)
                slash_arcs.append(SlashArc(cx + self.facing * 8, cy - 4, 64, 65, -65, self.facing, YELLOW, 13, thickness=30))
                for _ in range(16):
                    particles.append(Particle(
                        cx + self.facing * 35, cy,
                        self.facing * random.uniform(5, 13), random.uniform(-4, 4),
                        YELLOW, 6, 18, spark=True
                    ))

    def update_ai(self, target, platforms, particles, shockwaves, slash_arcs, projectiles):
        """
        Inteligencia Artificial Equilibrada y Dinámica con tres niveles de dificultad.
        - FÁCIL: Tiempo de reacción lento, sin techs, ataques simples.
        - EQUILIBRADO: Espaciado inteligente, combos básicos, recuperación inteligente, techs ocasionales.
        - EXPERTO: DI avanzado, persecuciones aéreas, reflejos rápidos, techs casi perfectos.
        """
        main_stage = platforms[0].rect
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # 1. Influencia Direccional (DI) cuando está en Hitstun
        if self.hitstun > 0:
            di_x = 1 if self.rect.centerx < WIDTH // 2 else -1
            # Intento de Tech inteligente según la dificultad
            tech_chance = 0.20 if self.cpu_difficulty == "FACIL" else (0.65 if self.cpu_difficulty == "EQUILIBRADO" else 0.88)
            if self.vy > 6.0 and abs(self.rect.bottom - main_stage.top) < 35 and random.random() < tech_chance:
                self.tech_window = 10
            return di_x, -1, False, None

        # 2. Comportamiento en Ledge (Borde)
        if self.on_ledge:
            if self.ledge_timer > (30 if self.cpu_difficulty == "FACIL" else 16):
                r = random.random()
                if r < 0.45:
                    self.jump(particles, shockwaves)
                elif r < 0.75:
                    return self.facing, 0, False, None  # Roll onto stage
                else:
                    self.perform_attack(self.facing, 0, "light", particles, shockwaves, slash_arcs, projectiles)
            return 0, 0, False, None

        # 3. Lógica de Recuperación Fuera del Escenario
        is_offstage = (self.rect.right < main_stage.left + 20 or self.rect.left > main_stage.right - 20)
        if is_offstage:
            recover_dir = 1 if self.rect.centerx < main_stage.centerx else -1
            if self.rect.bottom > main_stage.top + 25:
                if self.jumps_left > 0 and self.vy > -3.0:
                    self.jump(particles, shockwaves)
                    return recover_dir, 0, False, None
                elif not self.up_special_used and self.vy > 1.0:
                    self.perform_attack(recover_dir, -1, "special", particles, shockwaves, slash_arcs, projectiles)
                    return recover_dir, -1, False, None
            return recover_dir, 0, False, None

        # 4. Temporizador de Reacción Humana
        reaction_delay = 18 if self.cpu_difficulty == "FACIL" else (8 if self.cpu_difficulty == "EQUILIBRADO" else 4)
        self.ai_reaction_timer += 1

        move_x = 0
        move_y = 0
        want_shield = False
        attack_cmd = None

        if self.ai_reaction_timer >= reaction_delay:
            self.ai_reaction_timer = 0

            # Decisión de Defensa / Escudo si el enemigo ataca de cerca
            if dist < 95 and target.attack_cooldown > 0 and self.shield_hp > 35:
                shield_chance = 0.30 if self.cpu_difficulty == "FACIL" else (0.68 if self.cpu_difficulty == "EQUILIBRADO" else 0.85)
                if random.random() < shield_chance:
                    self.ai_shield_intent = True
            else:
                self.ai_shield_intent = False

            # Espaciado y Aproximación según el Arquetipo
            ideal_dist = 60
            if self.char_id in ("NEXUS", "PHANTOM"):
                ideal_dist = 160 if random.random() < 0.45 else 70
            elif self.char_id == "GOLIATH":
                ideal_dist = 65

            if abs(dx) > ideal_dist:
                move_x = 1 if dx > 0 else -1
            elif abs(dx) < ideal_dist - 20:
                move_x = -1 if dx > 0 else 1

            # Salto para perseguir o esquivar
            if dy < -70 and self.on_ground and random.random() < 0.40:
                self.jump(particles, shockwaves)

            # Selección de Ataque
            if dist < 105 and self.attack_cooldown == 0 and not self.shielding:
                r = random.random()
                self.facing = 1 if dx >= 0 else -1
                if dy < -35:
                    attack_cmd = (0, -1, "light")  # Up-Tilt
                elif not self.on_ground and dy > 30:
                    attack_cmd = (0, 1, "light")   # Down-Air Meteor
                elif target.percentage > 85 and r < 0.55:
                    attack_cmd = (self.facing, 0, "heavy")  # Smash letal
                elif r < 0.35 and self.char_id != "GOLIATH":
                    attack_cmd = (self.facing, 0, "special")
                else:
                    attack_cmd = (self.facing, 0, "light")  # Jab / Ftilt

            # Uso de Proyectiles a Distancia
            elif 130 < dist < 380 and self.attack_cooldown == 0 and abs(dy) < 45:
                proj_chance = 0.25 if self.cpu_difficulty == "FACIL" else 0.50
                if random.random() < proj_chance:
                    attack_cmd = (self.facing, 0, "special")

            self.ai_target_move = (move_x, move_y)

        want_shield = self.ai_shield_intent
        move_x, move_y = self.ai_target_move

        if attack_cmd and not want_shield:
            ax, ay, amode = attack_cmd
            self.perform_attack(ax, ay, amode, particles, shockwaves, slash_arcs, projectiles)

        return move_x, move_y, want_shield, None

    def update(self, move_x, move_y, jump_held, want_shield, platforms, particles, afterimages, shockwaves, ko_blasts, cam, floating_texts):
        self.anim_time += 0.22
        if self.invincible > 0:
            self.invincible -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 0:
                self.attack_type = None
                self.counter_active = False
                self.super_armor = False
        if self.drop_through_timer > 0:
            self.drop_through_timer -= 1
        if self.ui_shake > 0:
            self.ui_shake -= 1
        if self.airdodge_timer > 0:
            self.airdodge_timer -= 1
        if self.tech_window > 0:
            self.tech_window -= 1
        if self.invisible_timer > 0:
            self.invisible_timer -= 1

        # Efecto squash & stretch regresando a la normalidad
        self.squash_stretch += (1.0 - self.squash_stretch) * 0.15

        # Short Hop (Salto Corto al soltar rápido la tecla)
        if self.short_hop_window > 0:
            self.short_hop_window -= 1
            if not jump_held and self.vy < -8.0:
                self.vy = -8.2
                self.short_hop_window = 0

        # Ledge Grab (Agarre en el borde del escenario)
        if self.on_ledge:
            self.vx = 0.0
            self.vy = 0.0
            self.ledge_timer += 1
            if move_y > 0 or self.ledge_timer > 160:
                self.on_ledge = False
                self.drop_through_timer = 16
            elif move_x == self.facing:
                # Subir rodando con invencibilidad
                self.on_ledge = False
                self.rect.bottom = platforms[0].rect.top
                self.rect.centerx += self.facing * 45
                self.invincible = 22
            self.update_skeleton()
            return

        # Escudo
        if want_shield and self.on_ground and self.hitstun == 0 and self.attack_cooldown == 0 and self.shield_hp > 15:
            self.shielding = True
            self.shield_hp = max(0.0, self.shield_hp - 0.36)
        else:
            self.shielding = False
            self.shield_hp = min(self.data["max_shield"], self.shield_hp + 0.22)

        # Física de Hitstun, Tumble e Influencia Direccional (DI)
        if self.hitstun > 0:
            self.hitstun -= 1
            # DI: El jugador desvía ligeramente su trayectoria
            self.vx += move_x * 0.18
            self.vy += move_y * 0.14 + 0.52
            self.vx *= 0.985
            self.spin_angle += self.vx * 0.07

            speed = math.hypot(self.vx, self.vy)
            if speed > 9.0 and self.hitstun % 2 == 0:
                particles.append(Particle(
                    self.rect.centerx, self.rect.centery,
                    random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                    self.color, random.randint(6, 11), 18
                ))
        else:
            self.spin_angle = 0.0
            if self.dash_timer > 0:
                self.dash_timer -= 1
                if self.dash_timer % 2 == 0:
                    afterimages.append(SkeletalAfterimage(self.joints, self.color))
            elif self.airdodge_timer > 0:
                if self.airdodge_timer % 2 == 0:
                    afterimages.append(SkeletalAfterimage(self.joints, WHITE))
            elif not self.shielding:
                accel = self.data["accel"] if self.on_ground else self.data["accel"] * 0.58
                max_spd = self.data["speed"]
                if move_x != 0:
                    self.vx += move_x * accel
                    self.vx = max(-max_spd, min(max_spd, self.vx))
                    if self.attack_cooldown == 0:
                        self.facing = move_x
                else:
                    self.vx *= 0.75 if self.on_ground else 0.94
            else:
                self.vx *= 0.55

            # Fast-Fall (Caída rápida hacia abajo en el aire)
            if move_y > 0 and not self.on_ground and self.vy > -1.5:
                if self.vy < 14.5:
                    particles.append(Particle(self.rect.centerx, self.rect.top, 0, -4, WHITE, 5, 10, spark=True))
                self.vy = max(self.vy, 15.0)

            # Bajar de plataformas atravesables
            if move_y > 0 and self.on_ground:
                self.drop_through_timer = 12
                self.on_ground = False

            self.vy = min(16.5, self.vy + 0.70)

        # Coyote Time (Margen de frames al dejar el suelo para poder saltar)
        if self.on_ground:
            self.coyote_timer = 6
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Movimiento en el mundo
        prev_bottom = self.rect.bottom
        prev_x = self.rect.x
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        self.on_ground = False

        main_plat = platforms[0].rect

        # ======================================================================
        # DETECCIÓN DE AGARRE DE BORDE (Ledge Grab)
        # ======================================================================
        if not self.on_ground and self.vy > 0 and self.hitstun == 0 and self.drop_through_timer == 0:
            if abs(self.rect.right - main_plat.left) < 28 and abs(self.rect.top - main_plat.top) < 35:
                self.on_ledge = True
                self.ledge_timer = 0
                self.facing = 1
                self.rect.right = main_plat.left + 4
                self.rect.top = main_plat.top + 6
                self.jumps_left = 2
                self.up_special_used = False
                self.invincible = max(self.invincible, 35)
                shockwaves.append(Shockwave(main_plat.left, main_plat.top, YELLOW, 34, 5, 3))
            elif abs(self.rect.left - main_plat.right) < 28 and abs(self.rect.top - main_plat.top) < 35:
                self.on_ledge = True
                self.ledge_timer = 0
                self.facing = -1
                self.rect.left = main_plat.right - 4
                self.rect.top = main_plat.top + 6
                self.jumps_left = 2
                self.up_special_used = False
                self.invincible = max(self.invincible, 35)
                shockwaves.append(Shockwave(main_plat.right, main_plat.top, YELLOW, 34, 5, 3))

        # ======================================================================
        # DETECCIÓN DE REBOTES EN PARED (Wall Bounce & Wall Teching)
        # ======================================================================
        if not self.on_ground and self.rect.bottom > main_plat.top and self.rect.top < main_plat.bottom:
            wall_hit = None
            if prev_x + self.rect.width <= main_plat.left and self.rect.right >= main_plat.left:
                wall_hit = "left"
            elif prev_x >= main_plat.right and self.rect.left <= main_plat.right:
                wall_hit = "right"

            if wall_hit and abs(self.vx) > 5.0:
                if self.tech_window > 0 or (want_shield and self.hitstun > 0):
                    # ¡TECH EXITOSO EN PARED!
                    self.hitstun = 0
                    self.tech_window = 0
                    self.invincible = 24
                    self.vy = -12.5
                    self.vx = 6.0 if wall_hit == "left" else -6.0
                    floating_texts.append(FloatingText(self.rect.centerx, self.rect.centery, "WALL TECH!", GREEN_NEON, size="big"))
                    shockwaves.append(Shockwave(self.rect.centerx, self.rect.centery, GREEN_NEON, 60, 8, 4))
                elif self.hitstun > 0:
                    # ¡WALL BOUNCE (Rebote violento contra la pared)!
                    self.vx = -self.vx * 0.72
                    self.vy *= 0.78
                    cam.add_shake(14)
                    floating_texts.append(FloatingText(self.rect.centerx, self.rect.centery, "WALL BOUNCE!", ORANGE, size="med"))
                    shockwaves.append(Shockwave(self.rect.centerx, self.rect.centery, WHITE, 65, 9, 5))
                    for _ in range(12):
                        particles.append(Particle(self.rect.centerx, self.rect.centery, self.vx * 0.4 + random.uniform(-3, 3), random.uniform(-4, 4), YELLOW, 5, 16, spark=True))

        # ======================================================================
        # COLISIONES CON PLATAFORMAS (Floor Bounce & Floor Teching)
        # ======================================================================
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if plat.passthrough:
                    if self.vy >= 0 and prev_bottom <= plat.rect.top + 16 and self.drop_through_timer == 0:
                        self.rect.bottom = plat.rect.top
                        self.vy = 0
                        self.on_ground = True
                        self.jumps_left = 2
                        self.up_special_used = False
                else:
                    if self.vy >= 0 and prev_bottom <= plat.rect.top + 22:
                        # Si impacta contra el suelo a alta velocidad en Hitstun:
                        if self.hitstun > 0 and self.vy > 7.0:
                            if self.tech_window > 0 or want_shield:
                                # ¡TECH EXITOSO EN SUELO!
                                self.rect.bottom = plat.rect.top
                                self.vy = 0
                                self.hitstun = 0
                                self.tech_window = 0
                                self.on_ground = True
                                self.jumps_left = 2
                                self.up_special_used = False

                                if move_x != 0:
                                    # Tech Roll (Rodar al incorporarse)
                                    self.vx = move_x * 9.5
                                    self.invincible = 22
                                    floating_texts.append(FloatingText(self.rect.centerx, self.rect.top - 20, "TECH ROLL!", GREEN_NEON, size="big"))
                                else:
                                    # Tech in place (Recuperación instantánea)
                                    self.vx = 0
                                    self.invincible = 20
                                    floating_texts.append(FloatingText(self.rect.centerx, self.rect.top - 20, "TECH!", GREEN_NEON, size="big"))
                                shockwaves.append(Shockwave(self.rect.centerx, self.rect.bottom, GREEN_NEON, 65, 8, 4))
                            else:
                                # ¡FLOOR BOUNCE (Rebote elástico contra el suelo)!
                                self.rect.bottom = plat.rect.top
                                self.vy = -self.vy * 0.66
                                self.vx *= 0.85
                                self.squash_stretch = 0.70
                                cam.add_shake(13)
                                floating_texts.append(FloatingText(self.rect.centerx, self.rect.bottom - 25, "BOUNCE!", YELLOW, size="med"))
                                shockwaves.append(Shockwave(self.rect.centerx, self.rect.bottom, WHITE, 70, 9, 5))
                                for _ in range(12):
                                    particles.append(Particle(self.rect.centerx + random.uniform(-15, 15), self.rect.bottom,
                                                              random.uniform(-4, 4), random.uniform(-6, -1), YELLOW, 5, 16, spark=True))
                        else:
                            self.rect.bottom = plat.rect.top
                            self.vy = 0
                            self.on_ground = True
                            self.jumps_left = 2
                            self.up_special_used = False

        if self.active_hitbox:
            self.active_hitbox.duration -= 1
            if self.active_hitbox.duration <= 0:
                self.active_hitbox = None

        # Blast Zones (Muerte al salir de la pantalla)
        if (self.rect.right < BLAST_LEFT or self.rect.left > BLAST_RIGHT or
                self.rect.bottom < BLAST_TOP or self.rect.top > BLAST_BOTTOM):
            ko_blasts.append(KOBlast(self.rect.centerx, self.rect.centery, self.color))
            shockwaves.append(Shockwave(
                max(50, min(WIDTH - 50, self.rect.centerx)),
                max(50, min(HEIGHT - 50, self.rect.centery)),
                self.color, max_radius=260, speed=16, width=10
            ))
            cam.add_shake(32)
            self.stocks -= 1
            if self.stocks > 0:
                self.respawn()

        self.update_skeleton()

    def update_skeleton(self):
        cx = self.rect.centerx
        cy = self.rect.centery + 4
        f = self.facing
        t = self.anim_time

        torso_lean = 0.0
        if self.on_ledge:
            torso_lean = 10
            la1, la2 = 165, 175
            ra1, ra2 = -20, 10
            ll1, ll2 = -10, -25
            rl1, rl2 = 15, -10
        elif self.attack_cooldown > 0 and self.attack_type:
            p = 1.0 - (self.attack_cooldown / self.attack_max_cd)
            swing = math.sin(min(1.0, p * 1.4) * math.pi)
            if self.attack_type == "jab":
                torso_lean = 18 * swing
                ra1, ra2 = 90 * swing, 95 * swing
                la1, la2 = -35, 45
                ll1, ll2, rl1, rl2 = -25, -35, 30, -10
            elif self.attack_type in ("ftilt", "sspecial"):
                torso_lean = -15 * swing
                rl1, rl2 = 100 * swing, 95 * swing
                ll1, ll2 = -20, -15
                ra1, ra2, la1, la2 = -45, -20, 55, 80
            elif self.attack_type in ("utilt", "uspecial", "usmash"):
                torso_lean = -12 * swing
                ra1, ra2 = 165 * swing, 175 * swing
                la1, la2 = -30, -10
                ll1, ll2, rl1, rl2 = -20, -25, 25, -15
            elif self.attack_type == "dair":
                torso_lean = 25 * swing
                rl1, rl2 = -15, -5
                ll1, ll2 = 35, -45
                ra1, ra2, la1, la2 = -120, -140, 120, 140
            elif self.attack_type == "fsmash":
                charge = -45 if p < 0.25 else 105 * swing
                torso_lean = 28 * swing
                ra1, ra2 = charge, charge + 10
                la1, la2 = -50, -20
                ll1, ll2, rl1, rl2 = -38, -45, 42, -5
            elif self.attack_type in ("dsmash", "dspecial"):
                torso_lean = 35 * swing
                rl1, rl2 = 85 * swing, 80 * swing
                ll1, ll2 = -85 * swing, -80 * swing
                ra1, ra2, la1, la2 = 75, 85, -75, -85
            else:
                torso_lean = 15
                ra1, ra2 = 70, 90
                la1, la2 = -30, 20
                ll1, ll2, rl1, rl2 = -20, -20, 20, 20
        elif not self.on_ground:
            torso_lean = 12 if self.vy < 0 else -8
            ra1, ra2 = 45, 85
            la1, la2 = -55, -20
            rl1, rl2 = 45, -35
            ll1, ll2 = -25, -50
        elif abs(self.vx) > 1.2:
            torso_lean = 22
            sw = math.sin(t * 1.7) * 58
            ll1, ll2 = sw, sw - 42 if sw < 0 else sw - 15
            rl1, rl2 = -sw, -sw - 42 if -sw < 0 else -sw - 15
            la1, la2 = -sw * 0.9, -sw * 0.9 + 55
            ra1, ra2 = sw * 0.9, sw * 0.9 + 55
        else:
            breath = math.sin(t * 0.6) * 4
            cy += breath * 0.5
            torso_lean = 8
            ll1, ll2 = -18, -24
            rl1, rl2 = 22, -8
            la1, la2 = -22, 48
            ra1, ra2 = 38, 82

        def limb(ox, oy, len1, len2, a1, a2):
            r1 = math.radians(a1)
            r2 = math.radians(a2)
            mx = ox + math.sin(r1) * len1 * f
            my = oy + math.cos(r1) * len1
            ex = mx + math.sin(r2) * len2 * f
            ey = my + math.cos(r2) * len2
            return (mx, my), (ex, ey)

        lean_rad = math.radians(torso_lean)
        hip = (cx - math.sin(lean_rad) * 4 * f, cy + 4)
        shoulder = (hip[0] + math.sin(lean_rad) * 22 * f, hip[1] - math.cos(lean_rad) * 22)
        head = (shoulder[0] + math.sin(lean_rad) * 11 * f, shoulder[1] - 12)

        l_knee, l_foot = limb(hip[0], hip[1], 15, 15, ll1, ll2)
        r_knee, r_foot = limb(hip[0], hip[1], 15, 15, rl1, rl2)
        l_elbow, l_hand = limb(shoulder[0], shoulder[1], 13, 13, la1, la2)
        r_elbow, r_hand = limb(shoulder[0], shoulder[1], 13, 13, ra1, ra2)

        pts = {
            "hip": hip, "shoulder": shoulder, "head": head,
            "l_knee": l_knee, "l_foot": l_foot, "r_knee": r_knee, "r_foot": r_foot,
            "l_elbow": l_elbow, "l_hand": l_hand, "r_elbow": r_elbow, "r_hand": r_hand
        }

        if self.hitstun > 0:
            cos_a = math.cos(self.spin_angle)
            sin_a = math.sin(self.spin_angle)
            for k, (px, py) in pts.items():
                dx, dy = px - cx, py - cy
                pts[k] = (cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a)

        self.joints = pts

        # Dinámica de la Bufanda de Energía conectada al cuello
        self.scarf_nodes[0] = [pts["shoulder"][0], pts["shoulder"][1]]
        for i in range(1, len(self.scarf_nodes)):
            px, py = self.scarf_nodes[i - 1]
            nx, ny = self.scarf_nodes[i]
            nx += (-self.facing * 2.6 - self.vx * 0.35)
            ny += (0.8 - self.vy * 0.25 + math.sin(self.anim_time + i) * 1.2)
            dx, dy = nx - px, ny - py
            dist = max(0.1, math.hypot(dx, dy))
            seg_len = 6.8
            self.scarf_nodes[i] = [px + (dx / dist) * seg_len, py + (dy / dist) * seg_len]

    def draw(self, surf, cam):
        if self.stocks <= 0:
            return
        if self.invincible > 0 and (self.invincible // 3) % 2 == 0:
            return
        if self.invisible_timer > 0 and (self.invisible_timer // 2) % 2 == 0:
            return

        def pt(name):
            return cam.apply(*self.joints[name])

        back_color = (max(0, self.color[0] // 2), max(0, self.color[1] // 2), max(0, self.color[2] // 2))
        main_color = WHITE if (self.hitstun > 0 and self.hitstun % 2 == 0) else self.color
        scarf_color = self.data["scarf"]

        # 1. Bufanda de Energía Neón ondeando
        scarf_pts = [cam.apply(nx, ny) for nx, ny in self.scarf_nodes]
        if len(scarf_pts) >= 2:
            pygame.draw.lines(surf, scarf_color, False, scarf_pts, cam.scale(5))
            pygame.draw.lines(surf, WHITE, False, scarf_pts, cam.scale(2))

        w_thigh = cam.scale(7)
        w_calf = cam.scale(5)
        w_arm = cam.scale(6)

        # 2. Extremidades Traseras
        pygame.draw.line(surf, back_color, pt("hip"), pt("l_knee"), w_thigh)
        pygame.draw.line(surf, back_color, pt("l_knee"), pt("l_foot"), w_calf)
        pygame.draw.circle(surf, back_color, pt("l_foot"), cam.scale(4))

        pygame.draw.line(surf, back_color, pt("shoulder"), pt("l_elbow"), w_arm)
        pygame.draw.line(surf, back_color, pt("l_elbow"), pt("l_hand"), w_calf)
        pygame.draw.circle(surf, WHITE, pt("l_hand"), cam.scale(4))

        # 3. Torso Blindado
        sh = pt("shoulder")
        hp = pt("hip")
        torso_width = 15 if self.char_id == "GOLIATH" else 13
        pygame.draw.line(surf, main_color, sh, hp, cam.scale(torso_width))
        pygame.draw.line(surf, WHITE, sh, hp, cam.scale(5))

        # 4. Pierna Delantera y Bota
        pygame.draw.line(surf, main_color, hp, pt("r_knee"), w_thigh)
        pygame.draw.line(surf, WHITE, pt("r_knee"), pt("r_foot"), w_calf)
        foot_col = YELLOW if (self.attack_type in ("ftilt", "dair", "dsmash", "sspecial")) else main_color
        pygame.draw.circle(surf, foot_col, pt("r_foot"), cam.scale(5))

        # 5. Cabeza con Casco Cibernético
        hd = pt("head")
        head_r = cam.scale(10)
        pygame.draw.circle(surf, main_color, hd, head_r)
        pygame.draw.circle(surf, WHITE, hd, head_r, cam.scale(2))
        visor_x = hd[0] + self.facing * cam.scale(4)
        visor_col = YELLOW if self.attack_cooldown > 0 else self.accent
        pygame.draw.line(surf, visor_col, (visor_x - cam.scale(4), hd[1]), (visor_x + cam.scale(5), hd[1]), cam.scale(4))

        # 6. Brazo Delantero y Puño
        pygame.draw.line(surf, main_color, sh, pt("r_elbow"), w_arm)
        pygame.draw.line(surf, WHITE, pt("r_elbow"), pt("r_hand"), w_calf)
        fist_r = cam.scale(7 if self.attack_cooldown > 0 else 5)
        fist_col = YELLOW if self.attack_cooldown > 0 else WHITE
        pygame.draw.circle(surf, fist_col, pt("r_hand"), fist_r)

        # 7. Escudo de Burbuja Neón
        if self.shielding:
            cx, cy = cam.apply(self.rect.centerx, self.rect.centery)
            radius = cam.scale(max(14, 46 * (self.shield_hp / self.data["max_shield"])))
            sh_surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(sh_surf, (*self.color, 115), (radius + 4, radius + 4), radius)
            pygame.draw.circle(sh_surf, (255, 255, 255, 220), (radius + 4, radius + 4), radius, cam.scale(3))
            surf.blit(sh_surf, (cx - radius - 4, cy - radius - 4))


# ==============================================================================
# RESOLUCIÓN DE EMPUJES Y COMBATE
# ==============================================================================
def resolve_fighter_push(p1, p2):
    if p1.stocks <= 0 or p2.stocks <= 0 or p1.hitstun > 0 or p2.hitstun > 0:
        return
    if p1.rect.colliderect(p2.rect):
        diff = p1.rect.centerx - p2.rect.centerx
        push = 2.4 if diff >= 0 else -2.4
        p1.rect.x += int(push)
        p2.rect.x -= int(push)


def check_combat_hits(attacker, defender, particles, shockwaves, floating_texts, hit_sparks, cam):
    hb = attacker.active_hitbox
    if not hb or defender in hb.hit_targets or defender.invincible > 0 or defender.stocks <= 0:
        return 0

    if hb.get_rect().colliderect(defender.rect):
        hb.hit_targets.add(defender)
        hit_x = (attacker.rect.centerx + defender.rect.centerx) // 2
        hit_y = (attacker.rect.centery + defender.rect.centery) // 2

        # 1. ¿Contraataque Activo de Nexus?
        if defender.counter_active:
            defender.counter_active = False
            floating_texts.append(FloatingText(hit_x, hit_y - 20, "COUNTER!", CYAN_NEON, size="big"))
            hit_sparks.append(HitSpark(hit_x, hit_y, CYAN_NEON, scale=1.5))
            shockwaves.append(Shockwave(hit_x, hit_y, CYAN_NEON, 110, 10))
            cam.add_shake(20)
            # El atacante recibe el contraataque
            attacker.percentage += hb.damage * 1.5
            attacker.hitstun = 55
            attacker.vx = -attacker.facing * 18.0
            attacker.vy = -12.0
            return 12

        # 2. ¿Impacto contra el Escudo?
        if defender.shielding:
            defender.shield_hp -= hb.damage * 1.85
            defender.vx = attacker.facing * 6.5
            shockwaves.append(Shockwave(hit_x, hit_y, WHITE, max_radius=58, speed=8))
            if defender.shield_hp <= 0:
                defender.shielding = False
                defender.hitstun = 140
                defender.vy = -13.0
                floating_texts.append(FloatingText(defender.rect.centerx, defender.rect.top - 20, "SHIELD BREAK!", YELLOW, size="big"))
                cam.add_shake(22)
            return 4

        # 3. Super Armor de Goliath
        if defender.super_armor and hb.damage < 15.0:
            defender.percentage += hb.damage * 0.5
            floating_texts.append(FloatingText(hit_x, hit_y - 20, "ARMOR!", PURPLE_NEON, size="med"))
            hit_sparks.append(HitSpark(hit_x, hit_y, PURPLE_NEON, scale=1.1))
            return 3

        # 4. Impacto directo
        defender.on_ledge = False
        defender.percentage = min(999.0, defender.percentage + hb.damage)
        defender.ui_shake = 16
        floating_texts.append(FloatingText(hit_x, hit_y - 20, f"+{int(hb.damage)}%", YELLOW if hb.is_heavy else WHITE, size="med"))

        # Knockback modulado por el peso del personaje defensor
        weight_factor = 1.0 / defender.data["weight"]
        kb_power = (hb.base_kb + (hb.kb_scale * (defender.percentage / 9.0))) * weight_factor
        rad = math.radians(hb.angle_deg)
        defender.vx = math.cos(rad) * kb_power * attacker.facing
        defender.vy = -math.sin(rad) * kb_power
        defender.hitstun = int(min(72, 10 + kb_power * 1.4))
        defender.on_ground = False

        # Destellos y Chispas Cinematográficas
        hit_sparks.append(HitSpark(hit_x, hit_y, YELLOW if hb.is_heavy else attacker.color, scale=1.4 if hb.is_heavy else 0.9))
        spark_count = 28 if hb.is_heavy else 16
        for _ in range(spark_count):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(4, 15 if hb.is_heavy else 9)
            particles.append(Particle(
                hit_x, hit_y, math.cos(ang) * spd, math.sin(ang) * spd,
                YELLOW if hb.is_heavy else attacker.color,
                random.randint(4, 8), random.randint(14, 25), spark=True
            ))

        shockwaves.append(Shockwave(hit_x, hit_y, YELLOW if hb.is_heavy else attacker.color,
                                    max_radius=120 if hb.is_heavy else 72, speed=11, width=6))

        if kb_power >= 22.0:
            cam.trigger_kill_flash(hit_x, hit_y)
            return 14

        cam.add_shake(13 if hb.is_heavy else 6)
        return 7 if hb.is_heavy else 4

    return 0


def check_projectile_hits(projectiles, fighters, particles, shockwaves, floating_texts, hit_sparks, cam):
    for proj in projectiles[:]:
        for f in fighters:
            if f != proj.owner and f.stocks > 0 and f.invincible <= 0:
                if proj.get_rect().colliderect(f.rect):
                    proj.alive = False
                    hit_x, hit_y = proj.x, proj.y

                    if f.shielding:
                        f.shield_hp -= proj.damage * 1.5
                        f.vx = (1 if proj.vx > 0 else -1) * 4.5
                        shockwaves.append(Shockwave(hit_x, hit_y, WHITE, 45, 6))
                    else:
                        f.percentage = min(999.0, f.percentage + proj.damage)
                        f.ui_shake = 12
                        floating_texts.append(FloatingText(hit_x, hit_y - 15, f"+{int(proj.damage)}%", proj.color))
                        kb = proj.base_kb + (proj.kb_scale * (f.percentage / 10.0))
                        rad = math.radians(proj.angle)
                        f.vx = math.cos(rad) * kb * (1 if proj.vx > 0 else -1)
                        f.vy = -math.sin(rad) * kb
                        f.hitstun = int(min(50, 8 + kb * 1.3))
                        f.on_ground = False
                        hit_sparks.append(HitSpark(hit_x, hit_y, proj.color, scale=1.0))

                    cam.add_shake(6)
                    break


# ==============================================================================
# RENDERIZADO DEL ENTORNO CYBERPUNK (Synthwave Grid, Sol y Rayos)
# ==============================================================================
def draw_cyber_background(surf, cam, stars, grid_offset):
    # Gradiente de cielo crepuscular
    for y in range(0, HEIGHT, 4):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOT[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOT[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOT[2] * ratio)
        pygame.draw.rect(surf, (r, g, b), (0, y, WIDTH, 4))

    # Sol Synthwave Gigante con Gradiente Pulsante
    sun_x = int(WIDTH // 2 - (cam.focus_x - WIDTH // 2) * 0.12)
    sun_y = int(HEIGHT // 2 + 35)
    sun_surf = pygame.Surface((280, 280), pygame.SRCALPHA)
    pygame.draw.circle(sun_surf, (255, 45, 115, 65), (140, 140), 130)
    pygame.draw.circle(sun_surf, (255, 160, 40, 115), (140, 140), 92)
    pygame.draw.circle(sun_surf, (255, 230, 80, 160), (140, 140), 60)
    surf.blit(sun_surf, (sun_x - 140, sun_y - 140))

    # Estrellas de fondo con efecto Parallax
    for sx, sy, sr in stars:
        px = int((sx - cam.focus_x * 0.08) % WIDTH)
        py = int((sy - cam.focus_y * 0.08) % HEIGHT)
        pygame.draw.circle(surf, (150, 170, 230), (px, py), sr)

    # Cuadrícula 3D en Perspectiva (Synthwave Grid)
    horizon_y = HEIGHT // 2 + 110
    grid_surf = pygame.Surface((WIDTH, HEIGHT - horizon_y), pygame.SRCALPHA)
    num_lines = 14
    for i in range(num_lines):
        t = (i + (grid_offset % 1.0)) / num_lines
        y_pos = int((t ** 2.2) * (HEIGHT - horizon_y))
        alpha = int(140 * t)
        pygame.draw.line(grid_surf, (120, 80, 255, alpha), (0, y_pos), (WIDTH, y_pos), 1)

    for x in range(0, WIDTH + 120, 55):
        alpha = 85
        pygame.draw.line(grid_surf, (120, 80, 255, alpha), (WIDTH // 2, 0), (x - 60, HEIGHT - horizon_y), 1)
    surf.blit(grid_surf, (0, horizon_y))


def draw_kill_lightning(surf, cam):
    if not cam.kill_pos:
        return
    lx, ly = cam.apply(*cam.kill_pos)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((14, 0, 22, 175))
    surf.blit(overlay, (0, 0))

    for _ in range(4):
        pts = [(lx, ly)]
        cx, cy = lx, ly
        ang = random.uniform(0, math.pi * 2)
        for _ in range(8):
            cx += math.cos(ang) * random.uniform(55, 115) + random.uniform(-30, 30)
            cy += math.sin(ang) * random.uniform(55, 115) + random.uniform(-30, 30)
            pts.append((int(cx), int(cy)))
        pygame.draw.lines(surf, RED_NEON, False, pts, 10)
        pygame.draw.lines(surf, WHITE, False, pts, 3)


def get_percent_color(pct):
    if pct < 50:
        return WHITE
    elif pct < 90:
        return YELLOW
    elif pct < 140:
        return ORANGE
    return RED_NEON


# ==============================================================================
# HUD DINÁMICO EN COMBATE
# ==============================================================================
def draw_hud(surf, fighters):
    for idx, p in enumerate(fighters):
        base_x = 220 if idx == 0 else WIDTH - 520
        base_y = HEIGHT - 110
        sx = random.randint(-5, 5) if p.ui_shake > 0 else 0
        sy = random.randint(-5, 5) if p.ui_shake > 0 else 0

        panel = pygame.Surface((290, 92), pygame.SRCALPHA)
        pygame.draw.rect(panel, (16, 20, 40, 220), (0, 0, 290, 92), border_radius=12)
        pygame.draw.rect(panel, (*p.color, 230), (0, 0, 290, 92), 2, border_radius=12)
        surf.blit(panel, (base_x + sx, base_y + sy))

        tag = f"{p.tag} (CPU)" if p.is_cpu else f"{p.tag} (P{p.player_num})"
        surf.blit(FONT_MED.render(tag, True, p.color), (base_x + 16 + sx, base_y + 8 + sy))

        # Indicador de Vidas (Stocks)
        for s in range(p.stocks):
            pygame.draw.circle(surf, p.color, (base_x + 22 + s * 22 + sx, base_y + 44 + sy), 7)
            pygame.draw.circle(surf, WHITE, (base_x + 22 + s * 22 + sx, base_y + 44 + sy), 7, 2)

        # Barra de Escudo
        shield_ratio = max(0.0, p.shield_hp / p.data["max_shield"])
        bar_w = 90
        pygame.draw.rect(surf, (30, 35, 60), (base_x + 16 + sx, base_y + 64 + sy, bar_w, 8), border_radius=3)
        pygame.draw.rect(surf, p.color, (base_x + 16 + sx, base_y + 64 + sy, int(bar_w * shield_ratio), 8), border_radius=3)

        # Porcentaje de daño
        pct_surf = FONT_UI.render(f"{int(p.percentage)}%", True, get_percent_color(p.percentage))
        surf.blit(pct_surf, (base_x + 140 + sx, base_y + 20 + sy))

    # Barra superior con recordatorio de controles rápidos
    tip = "P1: WASD / ESPACIO | J(Ataque) K(Smash) U/I(Especial) L/SHIFT(Escudo/Tech) | ESC/P: Pausa"
    t_surf = FONT_SMALL.render(tip, True, (185, 205, 245))
    surf.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, 12))


# ==============================================================================
# COMPONENTES DE UI Y MENÚS INTERACTIVOS
# ==============================================================================
class UIButton:
    def __init__(self, rect, text, font=FONT_MED, bg_color=(25, 30, 60), border_color=CYAN_NEON, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.border_color = border_color
        self.text_color = text_color
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surf):
        bg = (min(255, self.bg_color[0] + 30), min(255, self.bg_color[1] + 30), min(255, self.bg_color[2] + 45)) if self.hovered else self.bg_color
        border = WHITE if self.hovered else self.border_color
        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, border, self.rect, 3 if self.hovered else 2, border_radius=10)

        txt = self.font.render(self.text, True, YELLOW if self.hovered else self.text_color)
        surf.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))


# ==============================================================================
# BUCLE PRINCIPAL Y GESTOR DE ESTADOS (MENÚ PRINCIPAL, SELECTOR, COMBATE, PAUSA)
# ==============================================================================
def main():
    game_state = "MENU_MAIN"  # "MENU_MAIN", "MENU_CHAR_SELECT", "MENU_CONTROLS", "GAME_PLAYING", "GAME_PAUSED", "GAME_OVER"
    match_mode = "VS_CPU"     # "VS_CPU", "VS_LOCAL", "PRACTICE"

    # Configuración de Selección de Personajes
    char_keys = list(CHARACTERS.keys())
    p1_char_idx = 0
    p2_char_idx = 1
    cpu_difficulties = ["FACIL", "EQUILIBRADO", "EXPERTO"]
    cpu_diff_idx = 1
    stock_options = [1, 3, 5]
    stock_idx = 1

    # Objetos del Juego
    cam = Camera()
    stage = get_default_stage()
    fighters = []
    particles, shockwaves, afterimages, ko_blasts, slash_arcs, floating_texts, hit_sparks, projectiles = [], [], [], [], [], [], [], []
    hitstop_frames = 0
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(90)]
    grid_offset = 0.0
    winner_fighter = None

    # Botones del Menú Principal
    btn_vs_cpu = UIButton((WIDTH // 2 - 180, 260, 360, 52), "1P VS CPU (EQUILIBRADA)")
    btn_vs_local = UIButton((WIDTH // 2 - 180, 325, 360, 52), "1V1 LOCAL (2 JUGADORES)")
    btn_practice = UIButton((WIDTH // 2 - 180, 390, 360, 52), "MODO ENTRENAMIENTO")
    btn_controls = UIButton((WIDTH // 2 - 180, 455, 360, 52), "GUÍA DE CONTROLES Y COMBATE")
    btn_quit = UIButton((WIDTH // 2 - 180, 520, 360, 52), "SALIR DEL JUEGO", border_color=RED_NEON)
    main_menu_buttons = [btn_vs_cpu, btn_vs_local, btn_practice, btn_controls, btn_quit]

    # Botones del Menú de Selección de Personaje
    btn_start_match = UIButton((WIDTH // 2 - 160, HEIGHT - 85, 320, 55), "¡A LUCHAR! [ESPACIO/ENTER]", bg_color=(20, 60, 40), border_color=GREEN_NEON)
    btn_css_back = UIButton((50, HEIGHT - 85, 160, 55), "VOLVER [ESC]", border_color=RED_NEON)
    btn_diff_toggle = UIButton((WIDTH - 250, HEIGHT - 85, 200, 55), "DIFICULTAD: EQUILIBRADO", font=FONT_SMALL)
    btn_stocks_toggle = UIButton((WIDTH // 2 - 340, HEIGHT - 85, 160, 55), "VIDAS: 3", font=FONT_SMALL)

    # Botones de Pausa
    btn_pause_resume = UIButton((WIDTH // 2 - 160, 250, 320, 50), "CONTINUAR COMBATE")
    btn_pause_restart = UIButton((WIDTH // 2 - 160, 315, 320, 50), "REINICIAR COMBATE")
    btn_pause_css = UIButton((WIDTH // 2 - 160, 380, 320, 50), "CAMBIAR PERSONAJES")
    btn_pause_main = UIButton((WIDTH // 2 - 160, 445, 320, 50), "MENÚ PRINCIPAL")
    pause_buttons = [btn_pause_resume, btn_pause_restart, btn_pause_css, btn_pause_main]

    def start_new_match():
        nonlocal fighters, particles, shockwaves, afterimages, ko_blasts, slash_arcs, floating_texts, hit_sparks, projectiles, hitstop_frames, winner_fighter
        p1_char = char_keys[p1_char_idx]
        p2_char = char_keys[p2_char_idx]
        is_cpu = (match_mode in ("VS_CPU", "PRACTICE"))
        diff = "FACIL" if match_mode == "PRACTICE" else cpu_difficulties[cpu_diff_idx]

        f1 = Fighter(1, p1_char, 410, 380, is_cpu=False)
        f2 = Fighter(2, p2_char, 760, 380, is_cpu=is_cpu, cpu_difficulty=diff)
        f1.stocks = stock_options[stock_idx]
        f2.stocks = stock_options[stock_idx]

        fighters = [f1, f2]
        particles, shockwaves, afterimages, ko_blasts, slash_arcs, floating_texts, hit_sparks, projectiles = [], [], [], [], [], [], [], []
        hitstop_frames = 0
        winner_fighter = None

    running = True
    while running:
        clock.tick(FPS)
        grid_offset += 0.05
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        # Comandos de Jugadores procesados por eventos
        p1_jump_press = p1_light_press = p1_heavy_press = p1_special_press = p1_dash_press = p1_shield_press = False
        p2_jump_press = p2_light_press = p2_heavy_press = p2_special_press = p2_dash_press = p2_shield_press = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                # Controles del Menú Principal
                if game_state == "MENU_MAIN":
                    if event.key == pygame.K_1:
                        match_mode = "VS_CPU"
                        game_state = "MENU_CHAR_SELECT"
                    elif event.key == pygame.K_2:
                        match_mode = "VS_LOCAL"
                        game_state = "MENU_CHAR_SELECT"
                    elif event.key == pygame.K_3:
                        match_mode = "PRACTICE"
                        game_state = "MENU_CHAR_SELECT"
                    elif event.key == pygame.K_4:
                        game_state = "MENU_CONTROLS"
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False

                elif game_state == "MENU_CONTROLS":
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "MENU_MAIN"

                elif game_state == "MENU_CHAR_SELECT":
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU_MAIN"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        start_new_match()
                        game_state = "GAME_PLAYING"
                    elif event.key == pygame.K_a:
                        p1_char_idx = (p1_char_idx - 1) % len(char_keys)
                    elif event.key == pygame.K_d:
                        p1_char_idx = (p1_char_idx + 1) % len(char_keys)
                    elif event.key == pygame.K_LEFT:
                        p2_char_idx = (p2_char_idx - 1) % len(char_keys)
                    elif event.key == pygame.K_RIGHT:
                        p2_char_idx = (p2_char_idx + 1) % len(char_keys)
                    elif event.key == pygame.K_TAB:
                        cpu_diff_idx = (cpu_diff_idx + 1) % len(cpu_difficulties)

                elif game_state == "GAME_PLAYING":
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        game_state = "GAME_PAUSED"
                    elif event.key == pygame.K_r:
                        start_new_match()

                    # Controles de Jugador 1
                    if event.key in (pygame.K_w, pygame.K_SPACE):
                        p1_jump_press = True
                    if event.key == pygame.K_j:
                        p1_light_press = True
                    if event.key == pygame.K_k:
                        p1_heavy_press = True
                    if event.key in (pygame.K_u, pygame.K_i):
                        p1_special_press = True
                    if event.key in (pygame.K_l, pygame.K_LSHIFT):
                        p1_dash_press = True
                        p1_shield_press = True

                    # Controles de Jugador 2 (Local)
                    if not fighters[1].is_cpu:
                        if event.key in (pygame.K_UP, pygame.K_KP0):
                            p2_jump_press = True
                        if event.key in (pygame.K_b, pygame.K_KP1):
                            p2_light_press = True
                        if event.key in (pygame.K_n, pygame.K_KP2):
                            p2_heavy_press = True
                        if event.key in (pygame.K_h, pygame.K_KP4):
                            p2_special_press = True
                        if event.key in (pygame.K_m, pygame.K_KP3):
                            p2_dash_press = True
                            p2_shield_press = True

                elif game_state == "GAME_PAUSED":
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        game_state = "GAME_PLAYING"

                elif game_state == "GAME_OVER":
                    if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                        start_new_match()
                        game_state = "GAME_PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "MENU_CHAR_SELECT"

        keys = pygame.key.get_pressed()

        # ======================================================================
        # PANTALLA: MENÚ PRINCIPAL
        # ======================================================================
        if game_state == "MENU_MAIN":
            draw_cyber_background(screen, cam, stars, grid_offset)

            # Título Neón Animado
            title_glow = FONT_BIG.render("CYBER SMASH ARENA", True, (0, 160, 255))
            title_front = FONT_BIG.render("CYBER SMASH ARENA", True, WHITE)
            tx = WIDTH // 2 - title_front.get_width() // 2
            ty = 95 + int(math.sin(pygame.time.get_ticks() * 0.003) * 6)
            screen.blit(title_glow, (tx - 3, ty - 3))
            screen.blit(title_front, (tx, ty))

            sub_txt = FONT_MED.render("Advanced Humanoid Combat & High-Speed Physics Engine", True, (255, 220, 60))
            screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, ty + 85))

            # Actualizar y Dibujar Botones
            for btn in main_menu_buttons:
                btn.update(mouse_pos)
                btn.draw(screen)

            if mouse_clicked:
                if btn_vs_cpu.hovered:
                    match_mode = "VS_CPU"
                    game_state = "MENU_CHAR_SELECT"
                elif btn_vs_local.hovered:
                    match_mode = "VS_LOCAL"
                    game_state = "MENU_CHAR_SELECT"
                elif btn_practice.hovered:
                    match_mode = "PRACTICE"
                    game_state = "MENU_CHAR_SELECT"
                elif btn_controls.hovered:
                    game_state = "MENU_CONTROLS"
                elif btn_quit.hovered:
                    running = False

            cred = FONT_TINY.render("Antigravity Engine 2026 | Selecciona con el Ratón o Teclas numéricas", True, GRAY)
            screen.blit(cred, (WIDTH // 2 - cred.get_width() // 2, HEIGHT - 30))

        # ======================================================================
        # PANTALLA: GUÍA DE CONTROLES Y COMBATE
        # ======================================================================
        elif game_state == "MENU_CONTROLS":
            draw_cyber_background(screen, cam, stars, grid_offset)

            panel = pygame.Surface((WIDTH - 120, HEIGHT - 100), pygame.SRCALPHA)
            pygame.draw.rect(panel, (15, 18, 38, 235), (0, 0, WIDTH - 120, HEIGHT - 100), border_radius=16)
            pygame.draw.rect(panel, CYAN_NEON, (0, 0, WIDTH - 120, HEIGHT - 100), 3, border_radius=16)
            screen.blit(panel, (60, 50))

            t = FONT_TITLE.render("GUÍA DE CONTROLES Y MECÁNICAS AVANZADAS", True, YELLOW)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 65))

            # Tabla de Controles
            col1_x = 100
            col2_x = 640
            y_start = 145

            screen.blit(FONT_MED.render("JUGADOR 1 (WASD)", True, CYAN_NEON), (col1_x, y_start))
            p1_info = [
                ("Moverse / Agacharse:", "Teclas A / D / S"),
                ("Salto / Doble Salto:", "W o BARRA ESPACIADORA"),
                ("Ataque Ligero / Jab / Tilts:", "Tecla J (+ Dirección)"),
                ("Ataque Fuerte / Smashes:", "Tecla K (+ Dirección)"),
                ("Habilidades Especiales:", "Teclas U o I (+ Dirección)"),
                ("Escudo / Esquive / Dash:", "Tecla L o SHIFT IZQUIERDO"),
            ]
            for i, (k, v) in enumerate(p1_info):
                screen.blit(FONT_SMALL.render(k, True, WHITE), (col1_x, y_start + 35 + i * 28))
                screen.blit(FONT_SMALL.render(v, True, YELLOW), (col1_x + 240, y_start + 35 + i * 28))

            screen.blit(FONT_MED.render("JUGADOR 2 (Flechas / NumPad)", True, RED_NEON), (col2_x, y_start))
            p2_info = [
                ("Moverse / Agacharse:", "Flechas Izquierda / Derecha / Abajo"),
                ("Salto / Doble Salto:", "Flecha Arriba o NumPad 0"),
                ("Ataque Ligero / Jab:", "Tecla B o NumPad 1"),
                ("Ataque Fuerte / Smashes:", "Tecla N o NumPad 2"),
                ("Habilidades Especiales:", "Tecla H o NumPad 4"),
                ("Escudo / Esquive / Dash:", "Tecla M o NumPad 3"),
            ]
            for i, (k, v) in enumerate(p2_info):
                screen.blit(FONT_SMALL.render(k, True, WHITE), (col2_x, y_start + 35 + i * 28))
                screen.blit(FONT_SMALL.render(v, True, GOLD), (col2_x + 240, y_start + 35 + i * 28))

            # Sección de Mecánicas Avanzadas
            mech_y = 365
            pygame.draw.line(screen, (70, 80, 130), (90, mech_y), (WIDTH - 90, mech_y), 2)
            screen.blit(FONT_MED.render("SISTEMA DE FÍSICA Y HABILIDADES DE COMBATE", True, GREEN_NEON), (100, mech_y + 12))

            mechs = [
                ("MECÁNICA DE TECHING (Recuperación en Suelo/Pared):",
                 "Pulsa Escudo (L/Shift) justo al chocar contra el suelo o las paredes mientras estés en aturdimiento (Hitstun) para cancelar el impacto y levantarte invencible."),
                ("FLOOR & WALL BOUNCE (Rebote de Impacto):",
                 "Si no haces Tech, rebotarás elásticamente contra el suelo o las paredes conservando inercia para combos espectaculares."),
                ("SHORT HOP (Salto Corto):",
                 "Toca rápidamente y suelta el botón de salto para ejecutar un salto bajo ideal para ataques aéreos veloces."),
                ("FAST-FALL (Caída Rápida):",
                 "Pulsa ABAJO (S o Flecha Abajo) en el aire para descender al instante con gran velocidad."),
                ("CONTRATAQUE & ESCUDO:",
                 "Mantén Escudo para bloquear ataques. ¡Cuidado! Si tu escudo recibe demasiado daño sufrirá un SHIELD BREAK.")
            ]
            for i, (title, desc) in enumerate(mechs):
                screen.blit(FONT_SMALL.render(title, True, YELLOW), (100, mech_y + 44 + i * 38))
                screen.blit(FONT_TINY.render(desc, True, (210, 225, 255)), (100, mech_y + 64 + i * 38))

            btn_back = UIButton((WIDTH // 2 - 120, HEIGHT - 95, 240, 48), "VOLVER AL MENÚ [ESC]", border_color=CYAN_NEON)
            btn_back.update(mouse_pos)
            btn_back.draw(screen)
            if mouse_clicked and btn_back.hovered:
                game_state = "MENU_MAIN"

        # ======================================================================
        # PANTALLA: MENÚ DE SELECCIÓN DE PERSONAJES (CSS)
        # ======================================================================
        elif game_state == "MENU_CHAR_SELECT":
            draw_cyber_background(screen, cam, stars, grid_offset)

            t = FONT_TITLE.render("SELECCIÓN DE LUCHADORES", True, WHITE)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 20))

            mode_tag = f"MODO: {match_mode.replace('_', ' ')}"
            screen.blit(FONT_SMALL.render(mode_tag, True, YELLOW), (WIDTH // 2 - 80, 72))

            # 4 Tarjetas de Personajes
            card_w = 265
            card_h = 470
            start_x = (WIDTH - (card_w * 4 + 30 * 3)) // 2
            card_y = 105

            for idx, ckey in enumerate(char_keys):
                cdata = CHARACTERS[ckey]
                cx = start_x + idx * (card_w + 30)
                card_rect = pygame.Rect(cx, card_y, card_w, card_h)

                is_p1_sel = (idx == p1_char_idx)
                is_p2_sel = (idx == p2_char_idx)
                is_hovered = card_rect.collidepoint(mouse_pos)

                if mouse_clicked and is_hovered:
                    if mouse_pos[0] < WIDTH // 2:
                        p1_char_idx = idx
                    else:
                        p2_char_idx = idx

                # Fondo y Borde de la Tarjeta
                bg_col = (20, 24, 48) if not is_hovered else (28, 34, 66)
                pygame.draw.rect(screen, bg_col, card_rect, border_radius=14)
                border_col = cdata["color"] if (is_p1_sel or is_p2_sel) else (DARK_GRAY if not is_hovered else WHITE)
                pygame.draw.rect(screen, border_col, card_rect, 4 if (is_p1_sel or is_p2_sel) else 2, border_radius=14)

                # Insignias P1 / P2
                if is_p1_sel:
                    p1_badge = FONT_SMALL.render("P1", True, BLACK)
                    pygame.draw.rect(screen, CYAN_NEON, (cx + 10, card_y + 10, 36, 24), border_radius=6)
                    screen.blit(p1_badge, (cx + 18, card_y + 13))
                if is_p2_sel:
                    p2_badge = FONT_SMALL.render("CPU" if match_mode != "VS_LOCAL" else "P2", True, BLACK)
                    pygame.draw.rect(screen, RED_NEON, (cx + card_w - 56, card_y + 10, 46, 24), border_radius=6)
                    screen.blit(p2_badge, (cx + card_w - 50, card_y + 13))

                # Nombre y Rol
                name_surf = FONT_MED.render(cdata["name"], True, cdata["color"])
                screen.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2, card_y + 40))
                role_surf = FONT_TINY.render(cdata["role"], True, WHITE)
                screen.blit(role_surf, (cx + card_w // 2 - role_surf.get_width() // 2, card_y + 70))

                # Silueta / Preview Animada del Personaje
                prev_cx = cx + card_w // 2
                prev_cy = card_y + 160
                t_anim = pygame.time.get_ticks() * 0.004 + idx
                breath = math.sin(t_anim) * 4

                # Cabeza y visor
                pygame.draw.circle(screen, cdata["color"], (prev_cx, int(prev_cy - 35 + breath)), 14)
                pygame.draw.circle(screen, WHITE, (prev_cx, int(prev_cy - 35 + breath)), 14, 2)
                pygame.draw.line(screen, cdata["accent"], (prev_cx - 6, int(prev_cy - 35 + breath)), (prev_cx + 6, int(prev_cy - 35 + breath)), 4)
                # Torso
                torso_w = 16 if ckey == "GOLIATH" else 13
                pygame.draw.line(screen, cdata["color"], (prev_cx, int(prev_cy - 20 + breath)), (prev_cx, int(prev_cy + 15 + breath)), torso_w)
                # Bufanda animada
                scarf_pts = [(prev_cx, int(prev_cy - 22 + breath))]
                for si in range(1, 6):
                    sx = prev_cx - si * 9 + math.sin(t_anim + si) * 4
                    sy = prev_cy - 22 + breath + si * 4 + math.cos(t_anim + si) * 3
                    scarf_pts.append((int(sx), int(sy)))
                pygame.draw.lines(screen, cdata["scarf"], False, scarf_pts, 4)
                # Extremidades
                pygame.draw.line(screen, cdata["color"], (prev_cx, int(prev_cy + 15 + breath)), (prev_cx - 15, int(prev_cy + 48)), 6)
                pygame.draw.line(screen, cdata["color"], (prev_cx, int(prev_cy + 15 + breath)), (prev_cx + 15, int(prev_cy + 48)), 6)

                # Barras de Estadísticas
                stat_y = card_y + 230
                stats = [("VELOCIDAD", cdata["stats"]["vel"], CYAN_NEON),
                         ("POTENCIA", cdata["stats"]["pot"], RED_NEON),
                         ("PESO", cdata["stats"]["pes"], PURPLE_NEON),
                         ("RECUPERACIÓN", cdata["stats"]["rec"], GREEN_NEON)]
                for s_name, s_val, s_col in stats:
                    screen.blit(FONT_TINY.render(s_name, True, GRAY), (cx + 16, stat_y))
                    pygame.draw.rect(screen, (35, 40, 65), (cx + 120, stat_y + 2, 120, 8), border_radius=4)
                    pygame.draw.rect(screen, s_col, (cx + 120, stat_y + 2, int(120 * (s_val / 100.0)), 8), border_radius=4)
                    stat_y += 18

                # Resumen de Especiales
                stat_y += 8
                screen.blit(FONT_TINY.render("HABILIDADES ESPECIALES:", True, YELLOW), (cx + 16, stat_y))
                stat_y += 18
                for sk, sv in cdata["specials"].items():
                    line = f"• {sv}"
                    screen.blit(FONT_TINY.render(line[:32], True, (200, 215, 245)), (cx + 16, stat_y))
                    stat_y += 16

            # Botones Inferiores de Selección
            btn_diff_toggle.text = f"CPU: {cpu_difficulties[cpu_diff_idx]}"
            btn_stocks_toggle.text = f"VIDAS: {stock_options[stock_idx]}"

            for b in [btn_start_match, btn_css_back, btn_stocks_toggle]:
                b.update(mouse_pos)
                b.draw(screen)

            if match_mode != "VS_LOCAL":
                btn_diff_toggle.update(mouse_pos)
                btn_diff_toggle.draw(screen)

            if mouse_clicked:
                if btn_start_match.hovered:
                    start_new_match()
                    game_state = "GAME_PLAYING"
                elif btn_css_back.hovered:
                    game_state = "MENU_MAIN"
                elif btn_diff_toggle.hovered and match_mode != "VS_LOCAL":
                    cpu_diff_idx = (cpu_diff_idx + 1) % len(cpu_difficulties)
                elif btn_stocks_toggle.hovered:
                    stock_idx = (stock_idx + 1) % len(stock_options)

        # ======================================================================
        # PANTALLA: COMBATE EN VIVO (GAMEPLAY)
        # ======================================================================
        elif game_state in ("GAME_PLAYING", "GAME_PAUSED", "GAME_OVER"):
            p1, p2 = fighters[0], fighters[1]

            if game_state == "GAME_PLAYING":
                if hitstop_frames > 0:
                    hitstop_frames -= 1
                    cam.update(fighters)
                elif p1.stocks > 0 and p2.stocks > 0:
                    # Entradas de P1
                    p1_mx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
                    p1_my = (1 if keys[pygame.K_s] else 0) - (1 if (keys[pygame.K_w] or keys[pygame.K_SPACE]) else 0)
                    p1_shield = keys[pygame.K_l] or keys[pygame.K_LSHIFT]
                    p1_jump_held = keys[pygame.K_w] or keys[pygame.K_SPACE]

                    if p1_shield_press:
                        p1.tech_window = 10

                    if p1_jump_press:
                        p1.jump(particles, shockwaves)
                    if p1_dash_press and p1_mx != 0:
                        if not p1.on_ground:
                            p1.airdodge(p1_mx, p1_my, particles)
                        else:
                            p1.dash(p1_mx, particles)
                    if p1_light_press:
                        p1.perform_attack(p1_mx, p1_my, "light", particles, shockwaves, slash_arcs, projectiles)
                    if p1_heavy_press:
                        p1.perform_attack(p1_mx, p1_my, "heavy", particles, shockwaves, slash_arcs, projectiles)
                    if p1_special_press:
                        p1.perform_attack(p1_mx, p1_my, "special", particles, shockwaves, slash_arcs, projectiles)

                    # Entradas de P2
                    if p2.is_cpu:
                        p2_mx, p2_my, p2_shield, _ = p2.update_ai(p1, stage.platforms, particles, shockwaves, slash_arcs, projectiles)
                        p2_jump_held = True
                    else:
                        p2_mx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
                        p2_my = (1 if keys[pygame.K_DOWN] else 0) - (1 if (keys[pygame.K_UP] or keys[pygame.K_KP0]) else 0)
                        p2_shield = keys[pygame.K_m] or keys[pygame.K_KP3]
                        p2_jump_held = keys[pygame.K_UP] or keys[pygame.K_KP0]

                        if p2_shield_press:
                            p2.tech_window = 10

                        if p2_jump_press:
                            p2.jump(particles, shockwaves)
                        if p2_dash_press and p2_mx != 0:
                            if not p2.on_ground:
                                p2.airdodge(p2_mx, p2_my, particles)
                            else:
                                p2.dash(p2_mx, particles)
                        if p2_light_press:
                            p2.perform_attack(p2_mx, p2_my, "light", particles, shockwaves, slash_arcs, projectiles)
                        if p2_heavy_press:
                            p2.perform_attack(p2_mx, p2_my, "heavy", particles, shockwaves, slash_arcs, projectiles)
                        if p2_special_press:
                            p2.perform_attack(p2_mx, p2_my, "special", particles, shockwaves, slash_arcs, projectiles)

                    p1.update(p1_mx, p1_my, p1_jump_held, p1_shield, stage.platforms, particles, afterimages, shockwaves, ko_blasts, cam, floating_texts)
                    p2.update(p2_mx, p2_my, p2_jump_held, p2_shield, stage.platforms, particles, afterimages, shockwaves, ko_blasts, cam, floating_texts)
                    resolve_fighter_push(p1, p2)

                    # Detección de Golpes Cuerpo a Cuerpo
                    hs1 = check_combat_hits(p1, p2, particles, shockwaves, floating_texts, hit_sparks, cam)
                    hs2 = check_combat_hits(p2, p1, particles, shockwaves, floating_texts, hit_sparks, cam)
                    hitstop_frames = max(hs1, hs2)

                    # Detección de Proyectiles
                    check_projectile_hits(projectiles, fighters, particles, shockwaves, floating_texts, hit_sparks, cam)

                    # Actualización de Proyectiles
                    for proj in projectiles[:]:
                        proj.update(particles)
                        if not proj.alive:
                            projectiles.remove(proj)

                    # Actualización de Efectos
                    for lst in (particles, afterimages, ko_blasts, slash_arcs, floating_texts, hit_sparks):
                        for item in lst[:]:
                            item.update()
                            if item.life <= 0:
                                lst.remove(item)

                    for sw in shockwaves[:]:
                        sw.update()
                        if not sw.alive:
                            shockwaves.remove(sw)

                    cam.update(fighters)

                    # Comprobar Ganador
                    if p1.stocks <= 0 or p2.stocks <= 0:
                        winner_fighter = p2 if p1.stocks <= 0 else p1
                        game_state = "GAME_OVER"

            # ------------------------------------------------------------------
            # RENDERIZADO DEL COMBATE
            # ------------------------------------------------------------------
            draw_cyber_background(screen, cam, stars, grid_offset)

            if cam.flash_frames > 0:
                draw_kill_lightning(screen, cam)

            for plat in stage.platforms:
                plat.draw(screen, cam)

            for ai in afterimages:
                ai.draw(screen, cam)

            p1.draw(screen, cam)
            p2.draw(screen, cam)

            for proj in projectiles:
                proj.draw(screen, cam)
            for sa in slash_arcs:
                sa.draw(screen, cam)
            for p in particles:
                p.draw(screen, cam)
            for sw in shockwaves:
                sw.draw(screen, cam)
            for hs in hit_sparks:
                hs.draw(screen, cam)
            for kb in ko_blasts:
                kb.draw(screen, cam)
            for ft in floating_texts:
                ft.draw(screen, cam)

            draw_hud(screen, fighters)

            # ------------------------------------------------------------------
            # MENÚ DE PAUSA
            # ------------------------------------------------------------------
            if game_state == "GAME_PAUSED":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 10, 24, 190))
                screen.blit(overlay, (0, 0))

                pause_txt = FONT_BIG.render("PAUSA", True, YELLOW)
                screen.blit(pause_txt, (WIDTH // 2 - pause_txt.get_width() // 2, 140))

                for btn in pause_buttons:
                    btn.update(mouse_pos)
                    btn.draw(screen)

                if mouse_clicked:
                    if btn_pause_resume.hovered:
                        game_state = "GAME_PLAYING"
                    elif btn_pause_restart.hovered:
                        start_new_match()
                        game_state = "GAME_PLAYING"
                    elif btn_pause_css.hovered:
                        game_state = "MENU_CHAR_SELECT"
                    elif btn_pause_main.hovered:
                        game_state = "MENU_MAIN"

            # ------------------------------------------------------------------
            # PANTALLA DE FIN DE JUEGO (GAME OVER / VICTORIA)
            # ------------------------------------------------------------------
            elif game_state == "GAME_OVER" and winner_fighter:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((6, 8, 20, 195))
                screen.blit(overlay, (0, 0))

                game_txt = FONT_BIG.render("GAME!", True, YELLOW)
                screen.blit(game_txt, (WIDTH // 2 - game_txt.get_width() // 2, HEIGHT // 2 - 120))

                win_tag = f"¡VICTORIA PARA {winner_fighter.name}!"
                win_txt = FONT_UI.render(win_tag, True, winner_fighter.color)
                screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, HEIGHT // 2 - 20))

                sub = FONT_MED.render("Pulsa R / ESPACIO para REVANCHA  |  ESC para Selección de Personaje", True, WHITE)
                screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()