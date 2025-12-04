# pyright: reportMissingImports=false
from browser import document, html, ajax, bind, window
import json

STATE = {
    "game_id": None,
    "max_attempts": 6,
    "attempts": 0,
    "finished": False,
    "letter_tiles": False,  
}

def hide_modal():
    document["resultModal"].classList.add("hidden")

def reset_input(focus=True):
    try:
        document["guessInput"].value = ""
    except Exception:
        pass
    try:
        document["suggestions"].clear()
    except Exception:
        pass
    if focus:
        try:
            document["guessInput"].focus()
        except Exception:
            pass

def normalize_name(s: str) -> str:
    return " ".join([w for w in s.strip().split() if w])

def render_attempts():
    paws = document["attempts"]
    paws.clear()
    for i in range(STATE["max_attempts"]):
        used = " used" if i < STATE["attempts"] else ""
        paws <= html.SPAN("🐾", Class="paw" + used)

def arrow(dir):  
    return {"up": "↑", "down": "↓", "same": "≈"}.get(dir, "?")

def cls_of(dir):  
    return {"up": "up", "down": "down", "same": "same"}.get(dir, "")

def thermoreg(animal_class: str):
    warm = ("Mammal", "Bird")
    return ("warm", "warm-blooded") if animal_class in warm else ("cold", "cold-blooded")

def set_tip(el, text):
    if not el:
        return
    try:
        el.setAttribute("data-tip", str(text))
    except Exception:
        el.attrs["data-tip"] = str(text)
    el.attrs["title"] = str(text)

def get_letter_toggle() -> bool:
    try:
        return bool(document["letterToggle"].checked)
    except Exception:
        return False

def api(method, url, data=None, on_ok=None, on_err=None):
    req = ajax.Ajax()

    def _done(ev):
        try:
            status = req.status
            txt = req.text or ""
            payload = json.loads(txt) if txt else {}
            if 200 <= status < 300:
                if on_ok:
                    on_ok(payload)
            else:
                if on_err:
                    on_err(status, payload)
        except Exception as e:
            if on_err:
                on_err(0, {"error": str(e)})

    req.bind("complete", _done)
    req.open(method, url, True)
    if data is None:
        req.send()
    else:
        req.set_header("content-type", "application/json")
        if isinstance(data, (str, bytes)):
            req.send(data)
        else:
            req.send(json.dumps(data))

def fetch_suggestions(q: str):
    def ok(data):
        render_suggestions(data.get("items", []))
    api("GET", f"/api/animals?q={q}&details=true", on_ok=ok)

def render_suggestions(items):
    host = document["suggestions"]
    host.clear()
    if not items:
        return
    for it in items[:8]:
        name = it.get("name_en", "")
        emoji = it.get("emoji") or "🐾"
        cls = it.get("class", "")
        diet = it.get("diet", "")
        habitats = (it.get("habitat") or [])[:2]
        t_class, t_label = thermoreg(cls)

        card = html.DIV(Class="sugg")
        row1 = html.DIV(Class="row1")
        row1 <= html.SPAN(emoji, Class="emoji")
        row1 <= html.SPAN(name)
        row2 = html.DIV(Class="row2")
        row2 <= html.SPAN(cls or "—", Class="tag")
        if diet:
            row2 <= html.SPAN(diet, Class="tag")
        if habitats:
            row2 <= html.SPAN(" / ".join(habitats), Class="tag")
        row2 <= html.SPAN(t_label, Class=f"tag {t_class}")
        card <= row1
        card <= row2

        def on_click(ev, n=name):
            document["guessInput"].value = n
            document["guessInput"].focus()

        card.bind("click", on_click)
        host <= card

def fetch_guess_info_exact(name, cb):
    def ok(data):
        items = data.get("items", [])
        info = None
        for it in items:
            if (it.get("name_en", "").lower() == name.lower()):
                info = it
                break
        if not info and items:
            info = items[0] 
        cb(info or {})
    api("GET", f"/api/animals?q={name}&details=true", on_ok=ok)

def start_new():
    payload = {"mode": "free"} 
    lt = get_letter_toggle()
    if lt:
        payload["letter_feedback"] = True

    def ok(data):
        STATE["game_id"] = data.get("game_id")
        STATE["max_attempts"] = data.get("max_attempts", 6)
        STATE["attempts"] = 0
        STATE["finished"] = False
        STATE["letter_tiles"] = lt

        document["history"].clear()
        try:
            document["attempts"].clear()
        except Exception:
            pass
        try:
            document["suggestions"].clear()
        except Exception:
            pass

        board = document["board"]
        if STATE["letter_tiles"]:
            board.classList.remove("hidden")
            board.clear()
            for _ in range(STATE["max_attempts"]):
                row = html.DIV(Class="row")
                for _ in range(8):  
                    row <= html.DIV("", Class="tile")
                board <= row
        else:
            board.classList.add("hidden")

        reset_input(focus=True)
        render_attempts()

    api("POST", "/api/new", data=payload, on_ok=ok)
    hide_modal()

def guess():
    if STATE["finished"]:
        return
    name = normalize_name(document["guessInput"].value)
    if not name:
        return

    def ok(data):
        STATE["attempts"] = data.get("attempt", STATE["attempts"] + 1)
        render_attempts()

        card = html.DIV(Class="card")
        title = html.H3(f"Guess: {name}")
        card <= title

        tf = data.get("trait_feedback", {}) or {}
        traits = html.DIV(Class="traits")

        cls_val = tf.get("class")
        diet_val = tf.get("diet")
        cls_badge = html.SPAN(
            "class: ✔" if cls_val == "match" else "class: ✖",
            Class="badge " + ("ok" if cls_val == "match" else "no") + " tip",
        )
        diet_badge = html.SPAN(
            "diet: ✔" if diet_val == "match" else "diet: ✖",
            Class="badge " + ("ok" if diet_val == "match" else "no") + " tip",
        )
        set_tip(cls_badge, "")
        set_tip(diet_badge, "")
        traits <= cls_badge
        traits <= diet_badge

        h = tf.get("habitat", {}) or {}
        c = tf.get("continents", {}) or {}
        hab_badge = html.SPAN(
            f"habitat match: {h.get('matches', h.get('overlap', 0))}",
            Class="badge tip",
        )
        cont_badge = html.SPAN(
            f"continents overlap: {c.get('overlap', 0)}",
            Class="badge tip",
        )
        set_tip(hab_badge, "")
        set_tip(cont_badge, cont_badge.text)
        traits <= hab_badge
        traits <= cont_badge

        def _dir(v):
            if isinstance(v, str):
                return v
            if isinstance(v, dict):
                return v.get("dir", "")
            return ""

        szd = _dir(tf.get("size"))
        if szd:
            size_badge = html.SPAN(
                f"size: {arrow(szd)}", Class="badge " + cls_of(szd) + " tip"
            )
            set_tip(size_badge, size_badge.text)
            traits <= size_badge

        lsd = _dir(tf.get("lifespan"))
        if lsd:
            life_badge = html.SPAN(
                f"life: {arrow(lsd)}", Class="badge " + cls_of(lsd) + " tip"
            )
            set_tip(life_badge, life_badge.text)
            traits <= life_badge

        card <= traits
        document["history"] <= card

        def fill_tips(info):
            if info:
                if info.get("class"):
                    set_tip(
                        cls_badge,
                        (info["class"])
                        + (" (target different)" if cls_val == "mismatch" else "")
                    )
                if info.get("diet"):
                    set_tip(
                        diet_badge,
                        (info["diet"])
                        + (" (target different)" if diet_val == "mismatch" else "")
                    )
                if info.get("habitat"):
                    set_tip(
                        hab_badge,
                        " / ".join(info["habitat"]),
                    )
        fetch_guess_info_exact(name, fill_tips)

        if STATE["letter_tiles"]:
            feedback = data.get("letter_feedback", [])
            rows = document.select(".row")
            if rows and 0 < STATE["attempts"] <= len(rows):
                row = rows[STATE["attempts"] - 1]
                for i, st in enumerate(feedback[:8]):
                    tile = row.children[i]
                    tile.text = st.get("ch", "").upper()
                    tile.classList.add(st.get("state", "absent"))
                    window.set_timeout(lambda t=tile: t.classList.add("flip"), 20 * i)

        state = data.get("status", "in_progress")
        if state in ("won", "lost"):
            STATE["finished"] = True
            if state == "won":
                title.text = f"🎉 Correct: {data.get('answer','')}"
            else:
                title.text = f"💥 Out of tries — Answer: {data.get('answer','')}"
            show_modal(state, data.get("answer", ""))

        reset_input(focus=True)

    def err(code, payload):
        window.alert(payload.get("error", "Something went wrong"))

    api(
        "POST",
        "/api/guess",
        data={"game_id": STATE["game_id"], "guess": name},
        on_ok=ok,
        on_err=err,
    )

def show_modal(state, answer):
    panel = document["modalPanel"]
    panel.classList.remove("win", "lose")
    if state == "won":
        document["modalIcon"].text = "🎉"
        document["modalTitle"].text = "You got it!"
        document["modalSubtitle"].text = (
            f"Answer: {answer} • Attempts: {STATE['attempts']}/{STATE['max_attempts']}"
        )
        panel.classList.add("win")
    else:
        document["modalIcon"].text = "💥"
        document["modalTitle"].text = "Out of tries"
        document["modalSubtitle"].text = f"Answer: {answer}"
        panel.classList.add("lose")
    document["resultModal"].classList.remove("hidden")

@bind(document["newBtn"], "click")
def _(ev):
    start_new()

@bind(document["guessBtn"], "click")
def _(ev):
    guess()

@bind(document["guessInput"], "keydown")
def _(ev):
    if getattr(ev, "key", "") == "Enter":
        ev.preventDefault()
        guess()

@bind(document["guessInput"], "input")
def _(ev):
    q = normalize_name(document["guessInput"].value)
    if q:
        fetch_suggestions(q)
    else:
        try:
            document["suggestions"].clear()
        except Exception:
            pass

@bind(document["modalClose"], "click")
def _(ev):
    hide_modal()

@bind(document["modalBackdrop"], "click")
def _(ev):
    hide_modal()

@bind(document["modalNew"], "click")
def _(ev):
    hide_modal()
    start_new()

@bind(document, "keydown")
def _(ev):
    if getattr(ev, "key", "") == "Escape":
        hide_modal()

start_new()
fetch_suggestions("") 
