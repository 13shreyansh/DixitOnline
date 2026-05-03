import enum
import random
import threading
from time import sleep

from flask_socketio import emit


TARGET_PROMPTS = [
    "a tiny astronaut running a ramen shop on the moon",
    "a haunted vending machine in a luxury hotel lobby",
    "a dragon trying to use an office printer",
    "a royal portrait of a cat made of thunderclouds",
    "a submarine full of houseplants crossing a desert",
    "a wizard stuck in airport security with glowing luggage",
    "a cozy cafe inside a giant glass snow globe",
    "a robot barber giving haircuts to chess pieces",
    "a pirate ship sailing through a bowl of cereal",
    "a lonely lighthouse wearing sneakers on a foggy beach",
    "a medieval knight hosting a late night cooking show",
    "a city skyline growing out of an old piano",
    "a detective duck investigating a neon noodle factory",
    "a library where every book is a tiny aquarium",
    "a tea party for ghosts on top of a moving train",
    "a sushi chef preparing dinner for planets in orbit",
    "a sleepy volcano tucked into bed with a nightlight",
    "a circus tent floating in a thunderstorm over Tokyo",
    "a garden gnome piloting a cardboard spaceship",
    "a golden retriever CEO presenting charts to penguins",
    "a secret disco inside an ancient Egyptian pyramid",
    "a moonlit laundromat where socks become butterflies",
]

CHALLENGES = [
    {
        "title": "No Color Words",
        "description": "Do not use color words like red, blue, green, gold, black, or white.",
        "banned_words": ["red", "blue", "green", "yellow", "gold", "golden", "black", "white", "purple", "pink", "orange"],
    },
    {
        "title": "No Main Subject",
        "description": "Avoid naming the most obvious main object. Describe the scene around it instead.",
        "banned_words": [],
    },
    {
        "title": "Movie Poster Mode",
        "description": "Make your prompt sound like a dramatic movie poster.",
        "banned_words": [],
    },
    {
        "title": "Five Words Max",
        "description": "Use five words or fewer.",
        "banned_words": [],
        "max_words": 5,
    },
    {
        "title": "No People",
        "description": "Do not mention humans, people, person, man, woman, boy, or girl.",
        "banned_words": ["human", "humans", "people", "person", "man", "woman", "boy", "girl"],
    },
    {
        "title": "One Sentence",
        "description": "Write exactly one sentence. No comma-separated shopping list.",
        "banned_words": [],
    },
    {
        "title": "Tiny Detail First",
        "description": "Begin with a small detail, then describe the rest of the image.",
        "banned_words": [],
    },
    {
        "title": "No Style Words",
        "description": "Do not use art-style words like cinematic, realistic, illustration, painting, or photo.",
        "banned_words": ["cinematic", "realistic", "illustration", "painting", "photo", "photograph", "render", "style"],
    },
    {
        "title": "Child Explains It",
        "description": "Write like a kid describing the picture to a friend.",
        "banned_words": [],
    },
    {
        "title": "Museum Label",
        "description": "Write like a serious museum label for a very unserious scene.",
        "banned_words": [],
    },
]


def create_image_generator():
    import os

    if os.environ.get("DIXIT_USE_STABLE_DIFFUSION") == "1":
        from stablediffusion_dixit.image_generation.local_generation.local_image_generator import LocalImageGenerator

        return LocalImageGenerator()

    if os.environ.get("OPENAI_API_KEY"):
        from stablediffusion_dixit.image_generation.openai_image_generator import OpenAIImageGenerator

        return OpenAIImageGenerator()

    from stablediffusion_dixit.image_generation.mock_image_generator import MockImageGenerator

    return MockImageGenerator()


class GamePhase(enum.Enum):
    WaitingToStart = 0
    TargetImageWait = 1
    PlayerPrompts = 2
    PlayerImageWait = 3
    VoteClosest = 4
    ShowResults = 5


class GameState:
    def __init__(self, app, socketio=None):
        self.app = app
        self.socketio = socketio
        self.image_generator = create_image_generator()
        self.phase = GamePhase.WaitingToStart
        self.players = []
        self.pending_players = []
        self.tvs = []
        self.round_number = 0
        self.round_timer = None
        self.reset_round_state()

    def emit(self, event, payload, **kwargs):
        if self.socketio is not None:
            self.socketio.emit(event, payload, **kwargs)
        else:
            emit(event, payload, **kwargs)

    def add_player(self, player):
        if self.get_player(player.sid) is not None:
            return
        if self.phase == GamePhase.WaitingToStart:
            self.players.append(player)
            self.emit("display_waiting_screen", {
                "state": "Wait for the TV to start Prompt Match.",
                "image": self.get_random_animation(),
            }, to=player.sid)
            self.emit_lobby()
        elif self.phase in (GamePhase.TargetImageWait, GamePhase.PlayerPrompts):
            self.players.append(player)
            if self.phase == GamePhase.PlayerPrompts and self.target_image is not None:
                self.emit("display_prompt", {
                    "mode": "match",
                    "promptInfo": "Write a prompt to recreate the target image on the TV.",
                    "target_image": self.target_image,
                    "challenge": self.challenges.get(player.sid),
                }, to=player.sid)
                self.emit_target()
            else:
                self.emit("display_waiting_screen", {
                    "state": "Generating the target image.",
                    "image": self.get_random_animation(),
                }, to=player.sid)
        else:
            self.pending_players.append(player)
            self.emit("display_waiting_screen", {
                "state": "A round is already running. You will join the next one.",
                "image": self.get_random_animation(),
            }, to=player.sid)

    def add_tv(self, sid):
        if sid not in self.tvs:
            self.tvs.append(sid)
        if self.phase == GamePhase.WaitingToStart:
            self.emit_lobby(to=sid)
        elif self.target_image is not None:
            self.emit_target(to=sid)
        else:
            self.emit("display_waiting_screen", {
                "state": "Generating the target image.",
                "image": self.get_random_animation(),
            }, to=sid)

    def remove_sid(self, sid):
        if sid in self.tvs:
            self.tvs.remove(sid)
            return

        player = self.get_player(sid)
        if player is None:
            self.pending_players = [pending for pending in self.pending_players if pending.sid != sid]
            return

        self.players.remove(player)
        if not self.players:
            self.reset_to_lobby()
            return

        if self.phase == GamePhase.WaitingToStart:
            self.emit_lobby()
        elif self.phase in (GamePhase.PlayerPrompts, GamePhase.PlayerImageWait, GamePhase.VoteClosest):
            self.prompts.pop(sid, None)
            self.submission_tickets.pop(sid, None)
            self.submission_images.pop(sid, None)
            self.votes.pop(sid, None)
            if self.phase == GamePhase.VoteClosest:
                self.card_order = [player_sid for player_sid in self.card_order if player_sid != sid]
                self.emit_vote_screen()
                self.check_votes_complete()
            else:
                self.check_submissions_complete()

    def start_game(self):
        if self.pending_players:
            existing_sids = {player.sid for player in self.players}
            self.players.extend(player for player in self.pending_players if player.sid not in existing_sids)
            self.pending_players = []

        if not self.players:
            self.emit_lobby()
            return

        self.round_number += 1
        self.reset_round_state()
        self.assign_challenges()
        self.phase = GamePhase.TargetImageWait
        self.target_prompt = random.choice(TARGET_PROMPTS)
        self.target_image_ticket = self.image_generator.request_generation(
            self.target_prompt,
            callback=self.receive_target_finished_generating,
        )
        self.emit_waiting_to_all("Generating the target image.")

    def receive_prompt(self, sid, prompt):
        if self.phase != GamePhase.PlayerPrompts or self.get_player(sid) is None:
            return
        if sid in self.submission_tickets:
            return

        clean_prompt = prompt.strip()
        if not clean_prompt:
            return

        self.prompts[sid] = clean_prompt
        self.submission_tickets[sid] = self.image_generator.request_generation(
            clean_prompt,
            callback=self.receive_submission_finished_generating,
        )
        self.emit("display_waiting_screen", {
            "state": "Generating your match. Keep an eye on the TV.",
            "image": self.get_random_animation(),
        }, to=sid)
        self.emit_target()
        self.check_submissions_complete()

    def receive_vote(self, sid, voted_for):
        if self.phase != GamePhase.VoteClosest or self.get_player(sid) is None:
            return
        if sid in self.votes:
            return
        if voted_for < 0 or voted_for >= len(self.card_order):
            return
        selected_sid = self.card_order[voted_for]
        self.votes[sid] = selected_sid
        self.emit("display_waiting_screen", {
            "state": "Vote locked. Waiting for everyone else.",
            "image": self.get_random_animation(),
        }, to=sid)
        self.check_votes_complete()

    def receive_proceed_active_player(self, sid):
        return

    def receive_target_finished_generating(self, image_num, image_path, anim_path):
        with self.app.app_context():
            if self.phase != GamePhase.TargetImageWait or image_num != self.target_image_ticket:
                return
            self.target_image = image_path
            self.phase = GamePhase.PlayerPrompts
            self.emit_target()
            for player in self.players:
                self.emit("display_prompt", {
                    "mode": "match",
                    "promptInfo": "Write a prompt to recreate the target image on the TV.",
                    "target_image": self.target_image,
                    "challenge": self.challenges.get(player.sid),
                }, to=player.sid)

    def receive_submission_finished_generating(self, image_num, image_path, anim_path):
        with self.app.app_context():
            if self.phase not in (GamePhase.PlayerPrompts, GamePhase.PlayerImageWait):
                return
            for sid, ticket in self.submission_tickets.items():
                if ticket == image_num:
                    self.submission_images[sid] = image_path
                    break
            self.check_submissions_complete()

    def check_submissions_complete(self):
        if self.phase not in (GamePhase.PlayerPrompts, GamePhase.PlayerImageWait):
            return
        if len(self.submission_tickets) == len(self.players):
            self.phase = GamePhase.PlayerImageWait
        if len(self.submission_images) == len(self.players) and self.players:
            self.phase = GamePhase.VoteClosest
            self.create_images_list()
            self.emit_vote_screen()

    def check_votes_complete(self):
        if self.phase == GamePhase.VoteClosest and len(self.votes) == len(self.players):
            self.phase = GamePhase.ShowResults
            self.score_votes()
            self.show_results()

    def score_votes(self):
        tallies = {player.sid: 0 for player in self.players}
        for voted_sid in self.votes.values():
            if voted_sid in tallies:
                tallies[voted_sid] += 1

        highest_votes = max(tallies.values()) if tallies else 0
        winners = {sid for sid, count in tallies.items() if count == highest_votes and highest_votes > 0}
        self.round_scores = {}

        for player in self.players:
            round_score = tallies[player.sid]
            if player.sid in winners:
                round_score += 3
            self.round_scores[player.sid] = round_score
            player.score += round_score

    def show_results(self):
        for player in self.players:
            self.emit("player_display_results", {
                "message": "Round complete",
                "player_round_score": self.round_scores.get(player.sid, 0),
                "player_total_score": player.score,
            }, to=player.sid)

        image_info = []
        for sid in self.card_order:
            player = self.get_player(sid)
            if player is None:
                continue
            votes = [
                self.get_player(voter_sid).nickname
                for voter_sid, voted_sid in self.votes.items()
                if voted_sid == sid and self.get_player(voter_sid) is not None
            ]
            image_info.append({
                "image": self.submission_images[sid],
                "votes": votes,
                "is_winner": self.round_scores.get(sid, 0) >= max(self.round_scores.values()),
                "prompt": self.prompts.get(sid, ""),
                "author": player.nickname,
                "challenge": self.challenges.get(sid),
                "score": player.score,
                "round_score": self.round_scores.get(sid, 0),
            })

        player_scores = [{
            "name": player.nickname,
            "round_score": self.round_scores.get(player.sid, 0),
            "total_score": player.score,
        } for player in self.players]
        player_scores.sort(key=lambda p: p["total_score"], reverse=True)

        for tv in self.tvs:
            self.emit("tv_display_results", {
                "target_image": self.target_image,
                "target_prompt": self.target_prompt,
                "images": image_info,
                "players": player_scores,
            }, to=tv)

        self.round_timer = threading.Thread(target=self.sleep_and_start_next_round, daemon=True)
        self.round_timer.start()

    def sleep_and_start_next_round(self):
        sleep(15)
        with self.app.app_context():
            if self.players and self.phase == GamePhase.ShowResults:
                self.start_game()

    def emit_lobby(self, to=None):
        payload = {
            "names": [player.nickname for player in self.players + self.pending_players],
        }
        recipients = [to] if to is not None else self.tvs
        for tv in recipients:
            self.emit("tv_show_player_list", payload, to=tv)

    def emit_target(self, to=None):
        payload = {
            "target_image": self.target_image,
            "round_number": self.round_number,
            "submitted_count": len(self.submission_tickets),
            "player_count": len(self.players),
        }
        recipients = [to] if to is not None else self.tvs
        for tv in recipients:
            self.emit("tv_show_target", payload, to=tv)

    def emit_vote_screen(self):
        images = [{
            "image": self.submission_images[sid],
            "index": index,
            "is_own": False,
        } for index, sid in enumerate(self.card_order) if self.get_player(sid) is not None]

        for tv in self.tvs:
            self.emit("tv_show_cards_vote", {
                "target_image": self.target_image,
                "images": images,
            }, to=tv)

        for player in self.players:
            options = []
            for index, sid in enumerate(self.card_order):
                options.append({"index": index})
            self.emit("display_vote", {
                "options": options,
                "number": len(self.card_order),
            }, to=player.sid)

    def emit_waiting_to_all(self, state):
        payload = {
            "state": state,
            "image": self.get_random_animation(),
        }
        for player in self.players:
            self.emit("display_waiting_screen", payload, to=player.sid)
        for tv in self.tvs:
            self.emit("display_waiting_screen", payload, to=tv)

    def create_images_list(self):
        self.card_order = list(self.submission_images.keys())
        random.shuffle(self.card_order)
        self.images = [self.submission_images[sid] for sid in self.card_order]

    def assign_challenges(self):
        shuffled = CHALLENGES[:]
        random.shuffle(shuffled)
        self.challenges = {}
        for index, player in enumerate(self.players):
            self.challenges[player.sid] = shuffled[index % len(shuffled)]

    def get_player(self, sid):
        for player in self.players:
            if player.sid == sid:
                return player
        return None

    def get_random_animation(self):
        return f"premade_animations/{random.randrange(5)}.gif"

    def reset_round_state(self):
        self.target_prompt = None
        self.target_image_ticket = None
        self.target_image = None
        self.submission_tickets = {}
        self.submission_images = {}
        self.card_order = []
        self.votes = {}
        self.round_scores = {}
        self.images = []
        self.prompts = {}
        self.challenges = {}

    def reset_to_lobby(self):
        self.phase = GamePhase.WaitingToStart
        self.round_number = 0
        self.reset_round_state()
        self.emit_lobby()
