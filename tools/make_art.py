#!/usr/bin/env python3
"""Draws the placeholder panoramas in art/ for Regnum.

Every hotspot in index.html gets a drawing at its own x/y, so the art always lines up
with the game. Run from the repository root after moving a hotspot:

    python3 tools/make_art.py

To use painted artwork instead, drop the image into art/ and point the scene's
`image:` at it, then re-place the hotspots with the gear (tune mode) in the game.
"""
import json, math, random, subprocess, os

W, H = 3200, 1000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = '#2a1a10'

# ------------------------------------------------------------------ primitives
def f(v): return f'{v:.1f}'
def pts(p): return ' '.join(f'{f(x)},{f(y)}' for x, y in p)
def rect(x, y, w, h, fill, stroke=None, sw=3, rx=0, op=1, extra=''):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op != 1 else ''
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}"{s}{o} {extra}/>'
def poly(p, fill, stroke=INK, sw=3, op=1):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ''
    o = f' opacity="{op}"' if op != 1 else ''
    return f'<polygon points="{pts(p)}" fill="{fill}"{s}{o}/>'
def path(d, fill='none', stroke=INK, sw=3, op=1, cap='round'):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}" stroke-linejoin="round"' if stroke else ''
    o = f' opacity="{op}"' if op != 1 else ''
    return f'<path d="{d}" fill="{fill}"{s}{o}/>'
def circ(x, y, r, fill, stroke=INK, sw=3, op=1):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op != 1 else ''
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}"{s}{o}/>'
def ell(x, y, rx, ry, fill, stroke=INK, sw=3, op=1, rot=0):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op != 1 else ''
    t = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot else ''
    return f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"{s}{o}{t}/>'
def line(x1, y1, x2, y2, stroke=INK, sw=3, op=1):
    o = f' opacity="{op}"' if op != 1 else ''
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{o}/>'
def text(x, y, s, size=20, fill=INK, anchor='middle', font='Georgia, serif', weight='normal', op=1, ls=2, rot=0):
    o = f' opacity="{op}"' if op != 1 else ''
    t = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot else ''
    return (f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-family="{font}" font-weight="{weight}" letter-spacing="{ls}"{o}{t}>{s}</text>')
def g(items, extra=''): return f'<g {extra}>' + ''.join(items) + '</g>'

def X(fx): return fx * W
def Y(fy): return fy * H

# ------------------------------------------------------------------ people
SKINS = ['#e0b48c', '#c98f63', '#b07850', '#8d5a3b', '#d9a679', '#a96f4a']
HAIR = ['#2b1d14', '#3d2a1a', '#5a4030', '#1a1410', '#8a8580', '#c9c4bc']

def person(cx, feet, h, *, skin='#d9a679', robe='#8a6a48', toga=None, stripe=None, hair='#2b1d14',
           beard=False, female=False, long=None, hold=None, arm='down', seated=False, chained=False,
           facing=1, mourning=False, belt=True, cap=None, bald=False):
    """A standing or seated figure. feet = y of the soles, h = full height in px."""
    out = []
    if long is None: long = bool(toga) or female
    hr = h * 0.068
    head_y = feet - h + hr * 1.05
    sh_y = feet - h * 0.80
    sw = h * 0.25
    hem_y = feet - (h * 0.05 if long else h * 0.30)
    hw = h * (0.32 if long else 0.27)
    if seated:
        seat_y = feet - h * 0.28
        knee_x = cx + facing * h * 0.20
        # stool
        out.append(rect(cx - h*0.16, seat_y, h*0.32, h*0.05, '#6b4a2b', INK, 2))
        out.append(line(cx - h*0.13, seat_y + h*0.05, cx - h*0.13, feet, INK, 5))
        out.append(line(cx + h*0.13, seat_y + h*0.05, cx + h*0.13, feet, INK, 5))
        # lower legs
        out.append(line(knee_x, seat_y, knee_x, feet - 4, skin, h*0.05))
        out.append(ell(knee_x + facing*6, feet - 3, h*0.04, h*0.015, '#3a2414', None))
        body = (f'M{f(cx - sw/2)},{f(sh_y)} L{f(cx + sw/2)},{f(sh_y)} Q{f(cx + sw*0.6)},{f(seat_y - h*0.15)} '
                f'{f(cx + sw*0.55)},{f(seat_y)} L{f(knee_x + facing*h*0.05)},{f(seat_y - h*0.02)} '
                f'L{f(knee_x + facing*h*0.05)},{f(seat_y + h*0.12 if long else seat_y + h*0.05)} '
                f'L{f(cx - sw*0.55)},{f(seat_y + h*0.06)} Q{f(cx - sw*0.62)},{f(seat_y - h*0.2)} {f(cx - sw/2)},{f(sh_y)} Z')
        out.append(path(body, robe))
    else:
        # legs
        if not long:
            for dx in (-h*0.055, h*0.055):
                out.append(line(cx + dx, hem_y - 4, cx + dx, feet - 5, skin, h*0.052))
        for dx in (-h*0.06, h*0.06):
            out.append(ell(cx + dx + facing*5, feet - 4, h*0.045, h*0.016, '#3a2414', None))
        body = (f'M{f(cx - sw/2)},{f(sh_y)} L{f(cx + sw/2)},{f(sh_y)} '
                f'Q{f(cx + sw*0.62)},{f((sh_y+hem_y)/2)} {f(cx + hw/2)},{f(hem_y)} '
                f'Q{f(cx)},{f(hem_y + h*0.015)} {f(cx - hw/2)},{f(hem_y)} '
                f'Q{f(cx - sw*0.62)},{f((sh_y+hem_y)/2)} {f(cx - sw/2)},{f(sh_y)} Z')
        out.append(path(body, robe))
        if belt and not long and not toga:
            by = sh_y + h*0.25
            out.append(path(f'M{f(cx - sw*0.55)},{f(by)} Q{f(cx)},{f(by + 6)} {f(cx + sw*0.55)},{f(by)}', 'none', '#3a2414', 5))
        if stripe and not toga:
            out.append(line(cx - sw*0.18, sh_y + 4, cx - sw*0.2, hem_y - 6, stripe, h*0.018))
            out.append(line(cx + sw*0.18, sh_y + 4, cx + sw*0.2, hem_y - 6, stripe, h*0.018))
    if toga:
        # the drape: over the left shoulder, across the body, down to the hem
        top = sh_y
        bot = (feet - h*0.28) if seated else hem_y
        d = (f'M{f(cx - sw*0.52)},{f(top)} L{f(cx - sw*0.05)},{f(top - 2)} '
             f'Q{f(cx + sw*0.45)},{f(top + h*0.22)} {f(cx + hw*0.46)},{f(top + h*0.40)} '
             f'Q{f(cx + hw*0.2)},{f(top + h*0.46)} {f(cx - hw*0.15)},{f(bot - h*0.06)} '
             f'L{f(cx - hw*0.48)},{f(bot)} Q{f(cx - sw*0.68)},{f((top+bot)/2)} {f(cx - sw*0.52)},{f(top)} Z')
        out.append(path(d, toga, INK, 2.5))
        out.append(path(f'M{f(cx - sw*0.1)},{f(top + h*0.05)} Q{f(cx + sw*0.25)},{f(top + h*0.22)} {f(cx + hw*0.35)},{f(top + h*0.36)}',
                        'none', '#00000030', 3))
        out.append(path(f'M{f(cx - sw*0.3)},{f(top + h*0.12)} Q{f(cx - sw*0.1)},{f(top + h*0.35)} {f(cx - hw*0.2)},{f(bot - h*0.1)}',
                        'none', '#00000025', 3))
        if stripe:
            out.append(path(f'M{f(cx - sw*0.05)},{f(top)} Q{f(cx + sw*0.45)},{f(top + h*0.22)} {f(cx + hw*0.46)},{f(top + h*0.40)}',
                            'none', stripe, h*0.02))
    if female:
        # palla over head and shoulders
        out.append(path(f'M{f(cx - sw*0.58)},{f(sh_y + h*0.18)} Q{f(cx - sw*0.62)},{f(head_y - hr*1.1)} {f(cx)},{f(head_y - hr*1.35)} '
                        f'Q{f(cx + sw*0.62)},{f(head_y - hr*1.1)} {f(cx + sw*0.58)},{f(sh_y + h*0.18)} Z', robe if not mourning else '#3a3530', INK, 2.5, 0.0))
    # arms
    ax = cx + facing * sw * 0.48
    bx = cx - facing * sw * 0.48
    aw = h * 0.055
    def arm_to(sx, ex, ey):
        out.append(path(f'M{f(sx)},{f(sh_y + 8)} Q{f((sx+ex)/2 + (ex-sx)*0.1)},{f((sh_y+ey)/2)} {f(ex)},{f(ey)}', 'none', robe, aw * 1.25))
        out.append(path(f'M{f(sx + (ex-sx)*0.55)},{f(sh_y + (ey-sh_y)*0.55)} L{f(ex)},{f(ey)}', 'none', skin, aw))
        out.append(circ(ex, ey, aw * 0.55, skin, None))
    if arm == 'raise':
        arm_to(ax, ax + facing*h*0.12, sh_y - h*0.12)
        arm_to(bx, bx - facing*h*0.02, sh_y + h*0.33)
        hand = (ax + facing*h*0.12, sh_y - h*0.12)
    elif arm == 'out':
        arm_to(ax, ax + facing*h*0.20, sh_y + h*0.12)
        arm_to(bx, bx - facing*h*0.02, sh_y + h*0.33)
        hand = (ax + facing*h*0.20, sh_y + h*0.12)
    elif arm == 'both':
        arm_to(ax, ax + facing*h*0.16, sh_y + h*0.22)
        arm_to(bx, bx + facing*h*0.10, sh_y + h*0.24)
        hand = (ax + facing*h*0.16, sh_y + h*0.22)
    elif arm == 'head':
        arm_to(ax, cx + facing*hr*0.9, head_y - hr*0.3)
        arm_to(bx, bx - facing*h*0.02, sh_y + h*0.33)
        hand = (cx + facing*hr*0.9, head_y - hr*0.3)
    else:
        arm_to(ax, ax + facing*h*0.04, sh_y + h*0.32)
        arm_to(bx, bx - facing*h*0.03, sh_y + h*0.32)
        hand = (ax + facing*h*0.04, sh_y + h*0.32)
    if seated and arm == 'down':
        hand = (cx + facing*h*0.14, feet - h*0.33)
    # neck + head
    out.append(rect(cx - hr*0.35, head_y + hr*0.6, hr*0.7, hr*0.9, skin, None))
    out.append(circ(cx, head_y, hr, skin, INK, 2.5))
    if female:
        out.append(path(f'M{f(cx - hr*1.02)},{f(head_y + hr*0.2)} Q{f(cx - hr*1.1)},{f(head_y - hr*1.15)} {f(cx)},{f(head_y - hr*1.08)} '
                        f'Q{f(cx + hr*1.1)},{f(head_y - hr*1.15)} {f(cx + hr*1.02)},{f(head_y + hr*0.2)} '
                        f'Q{f(cx + hr*0.6)},{f(head_y - hr*0.55)} {f(cx)},{f(head_y - hr*0.6)} Q{f(cx - hr*0.6)},{f(head_y - hr*0.55)} {f(cx - hr*1.02)},{f(head_y + hr*0.2)} Z', hair, INK, 2))
        out.append(circ(cx - facing*hr*0.9, head_y - hr*0.35, hr*0.42, hair, INK, 2))
        if mourning or robe:
            out.append(path(f'M{f(cx - hr*1.25)},{f(head_y + hr*1.4)} Q{f(cx - hr*1.45)},{f(head_y - hr*1.3)} {f(cx)},{f(head_y - hr*1.38)} '
                            f'Q{f(cx + hr*1.45)},{f(head_y - hr*1.3)} {f(cx + hr*1.25)},{f(head_y + hr*1.4)}', 'none', robe if not mourning else '#3a3530', hr*0.35, 0.95))
    elif not bald:
        out.append(path(f'M{f(cx - hr*0.98)},{f(head_y + hr*0.05)} Q{f(cx - hr)},{f(head_y - hr*1.1)} {f(cx)},{f(head_y - hr*1.06)} '
                        f'Q{f(cx + hr)},{f(head_y - hr*1.1)} {f(cx + hr*0.98)},{f(head_y + hr*0.05)} '
                        f'Q{f(cx + hr*0.5)},{f(head_y - hr*0.5)} {f(cx)},{f(head_y - hr*0.55)} Q{f(cx - hr*0.5)},{f(head_y - hr*0.5)} {f(cx - hr*0.98)},{f(head_y + hr*0.05)} Z', hair, INK, 2))
    else:
        out.append(path(f'M{f(cx - hr*0.98)},{f(head_y + hr*0.1)} Q{f(cx - hr*1.0)},{f(head_y - hr*0.4)} {f(cx - hr*0.7)},{f(head_y - hr*0.5)}', 'none', hair, hr*0.3))
    if beard:
        out.append(path(f'M{f(cx - hr*0.92)},{f(head_y + hr*0.1)} Q{f(cx - hr*0.7)},{f(head_y + hr*1.25)} {f(cx)},{f(head_y + hr*1.3)} '
                        f'Q{f(cx + hr*0.7)},{f(head_y + hr*1.25)} {f(cx + hr*0.92)},{f(head_y + hr*0.1)} Q{f(cx)},{f(head_y + hr*0.55)} {f(cx - hr*0.92)},{f(head_y + hr*0.1)} Z', hair, INK, 2))
    if cap == 'pileus':
        out.append(path(f'M{f(cx - hr*0.95)},{f(head_y - hr*0.25)} Q{f(cx)},{f(head_y - hr*2.0)} {f(cx + hr*0.95)},{f(head_y - hr*0.25)} Z', '#8a7a5a', INK, 2))
    # face
    ex = cx + facing * hr * 0.32
    out.append(circ(ex, head_y - hr*0.05, hr*0.09, INK, None))
    out.append(circ(ex - facing*hr*0.45, head_y - hr*0.05, hr*0.08, INK, None, op=0.8))
    out.append(path(f'M{f(cx + facing*hr*0.62)},{f(head_y)} L{f(cx + facing*hr*0.78)},{f(head_y + hr*0.28)} L{f(cx + facing*hr*0.6)},{f(head_y + hr*0.3)}', 'none', INK, 2))
    if not beard:
        out.append(path(f'M{f(cx + facing*hr*0.15)},{f(head_y + hr*0.55)} L{f(cx + facing*hr*0.5)},{f(head_y + hr*0.52)}', 'none', INK, 2))
    if chained:
        out.append(path(f'M{f(cx - h*0.06)},{f(feet - 10)} q10,10 20,0 q10,10 20,0 q10,10 20,0 q10,10 20,0', 'none', '#6a6a6a', 4))
    # held things
    hx, hy = hand
    if hold == 'scroll':
        out.append(rect(hx - h*0.02, hy - h*0.06, h*0.04, h*0.12, '#efe2c0', INK, 2, rx=4))
    elif hold == 'tablet':
        out.append(rect(hx - h*0.05, hy - h*0.07, h*0.09, h*0.11, '#a7804a', INK, 2))
        out.append(rect(hx - h*0.04, hy - h*0.06, h*0.07, h*0.09, '#3d2f1c', None))
    elif hold == 'staff':
        out.append(line(hx, hy - h*0.3, hx, feet, '#6b4a2b', 7))
    elif hold == 'crook':
        out.append(path(f'M{f(hx)},{f(feet)} L{f(hx)},{f(hy - h*0.32)} q0,-30 22,-30 q22,0 22,22', 'none', '#6b4a2b', 7))
    elif hold == 'hoe':
        out.append(line(hx, hy - h*0.1, hx + facing*h*0.25, feet - 6, '#6b4a2b', 7))
        out.append(poly([(hx + facing*h*0.25, feet - 6), (hx + facing*h*0.33, feet - 2), (hx + facing*h*0.29, feet - 22)], '#777'))
    elif hold == 'club':
        out.append(line(hx, hy, hx + facing*h*0.05, hy - h*0.22, '#7a5230', 14))
    elif hold == 'whip':
        out.append(path(f'M{f(hx)},{f(hy)} q{f(facing*30)},40 {f(facing*10)},90 q{f(-facing*20)},40 {f(facing*15)},70', 'none', '#3a2414', 3))
    elif hold == 'cup':
        out.append(path(f'M{f(hx - 12)},{f(hy - 18)} L{f(hx + 12)},{f(hy - 18)} L{f(hx + 6)},{f(hy)} L{f(hx - 6)},{f(hy)} Z', '#c0c0c8', INK, 2))
    elif hold == 'spindle':
        out.append(line(hx, hy, hx, hy + h*0.25, '#d9c8a0', 3))
        out.append(circ(hx, hy + h*0.25, h*0.02, '#7a5230', INK, 2))
        out.append(ell(hx - facing*20, hy - 30, 22, 30, '#e8e0d0', INK, 2))
    elif hold == 'groma':
        px = hx
        out.append(line(px, hy - h*0.45, px, feet, '#6b4a2b', 6))
        out.append(line(px - h*0.12, hy - h*0.45, px + h*0.12, hy - h*0.45, '#6b4a2b', 5))
        for dx in (-h*0.12, h*0.12):
            out.append(line(px + dx, hy - h*0.45, px + dx, hy - h*0.35, '#444', 2))
            out.append(circ(px + dx, hy - h*0.35, 5, '#555', None))
    elif hold == 'child':
        pass
    return ''.join(out)

def auto_person(hx, hy, k=0.47, **kw):
    """Figure whose chest lands on the hotspot; lower on screen = closer = larger."""
    feet = Y(hy) / (1 - 0.62 * k)
    h = feet * k
    return person(X(hx), feet, h, **kw)

def chest_person(hx, hy, h, **kw):
    """Figure of a given height whose chest lands on the hotspot."""
    return person(X(hx), Y(hy) + 0.62 * h, h, **kw)

def crowd(x0, x1, feet, h, n, seed=1, dark=0.0, tones=None):
    rnd = random.Random(seed)
    tones = tones or ['#8a6a48', '#a08060', '#6b5a48', '#9a7a58', '#c8b898', '#7a6a5a', '#efe6d0']
    out = []
    for i in range(n):
        cx = x0 + (x1 - x0) * (i + rnd.random() * 0.6) / n
        hh = h * (0.9 + rnd.random() * 0.2)
        t = rnd.choice(tones)
        out.append(person(cx, feet + rnd.random() * 10, hh, skin=rnd.choice(SKINS), robe=t,
                          toga='#efe8d8' if rnd.random() < 0.25 else None, hair=rnd.choice(HAIR),
                          beard=rnd.random() < 0.3, facing=rnd.choice([1, -1]), female=rnd.random() < 0.15,
                          arm=rnd.choice(['down', 'down', 'out', 'raise'])))
    if dark:
        out.append(rect(x0 - 60, feet - h * 1.1, x1 - x0 + 120, h * 1.15, '#000', None, op=0))
    return g(out, f'opacity="{1 - dark:.2f}"')

# ------------------------------------------------------------------ architecture
def column(x, top, bot, w, fill='#e8dcc0', order='doric', shade='#c9b998'):
    out = [rect(x - w/2, top + w*0.35, w, bot - top - w*0.5, fill, INK, 3)]
    for i in range(1, 4):
        out.append(line(x - w/2 + w*i/4, top + w*0.45, x - w/2 + w*i/4, bot - w*0.2, shade, 2))
    if order == 'ionic':
        out.append(rect(x - w*0.75, top + w*0.08, w*1.5, w*0.28, fill, INK, 3))
        out.append(circ(x - w*0.72, top + w*0.3, w*0.18, fill, INK, 2.5))
        out.append(circ(x + w*0.72, top + w*0.3, w*0.18, fill, INK, 2.5))
    else:
        out.append(rect(x - w*0.7, top, w*1.4, w*0.2, fill, INK, 3))
        out.append(path(f'M{f(x - w*0.6)},{f(top + w*0.2)} Q{f(x)},{f(top + w*0.45)} {f(x + w*0.6)},{f(top + w*0.2)}', fill, INK, 3))
    out.append(rect(x - w*0.68, bot - w*0.22, w*1.36, w*0.22, fill, INK, 3))
    return ''.join(out)

def temple(cx, base, width, height, ncols=6, fill='#e8dcc0', roof='#a0522d', order='doric', podium=0.22, door=True):
    out = []
    pod_h = height * podium
    top = base - height
    out.append(rect(cx - width/2, base - pod_h, width, pod_h, '#cdbf9f', INK, 3))
    # steps
    for i in range(5):
        sw = width * 0.45 - i * 6
        out.append(rect(cx - sw/2, base - pod_h + i * pod_h/5, sw, pod_h/5, '#ddd0b0', INK, 1.5))
    col_top = top + height * 0.28
    col_bot = base - pod_h
    if door:
        out.append(rect(cx - width*0.12, col_top + 20, width*0.24, col_bot - col_top - 20, '#3a2a1c', INK, 2))
    cw = width / (ncols * 2.4)
    for i in range(ncols):
        x = cx - width/2 + width * 0.06 + (width * 0.88) * i / (ncols - 1)
        out.append(column(x, col_top, col_bot, cw, fill, order))
    out.append(rect(cx - width*0.53, col_top - height*0.06, width*1.06, height*0.06, fill, INK, 3))
    out.append(poly([(cx - width*0.56, col_top - height*0.06), (cx, top), (cx + width*0.56, col_top - height*0.06)], fill))
    out.append(poly([(cx - width*0.46, col_top - height*0.075), (cx, top + height*0.04), (cx + width*0.46, col_top - height*0.075)], '#d8c9a8', INK, 2))
    out.append(path(f'M{f(cx - width*0.58)},{f(col_top - height*0.055)} L{f(cx)},{f(top - 6)} L{f(cx + width*0.58)},{f(col_top - height*0.055)}', 'none', roof, 10))
    return ''.join(out)

def tiles(x, y, w, h, fill='#a0522d'):
    out = [rect(x, y, w, h, fill, INK, 3)]
    for i in range(int(w // 26)):
        out.append(line(x + i * 26 + 13, y + 2, x + i * 26 + 13, y + h - 2, '#7a3a1d', 3))
    return ''.join(out)

def first_style_wall(x0, x1, y0, y1, base='#c9a36a', band='#9a2e20', block='#dcc08a'):
    """Masonry-style painted plaster: a dado, rows of painted 'stone blocks', a cornice."""
    out = [rect(x0, y0, x1 - x0, y1 - y0, base, None)]
    dado = y1 - (y1 - y0) * 0.22
    out.append(rect(x0, dado, x1 - x0, y1 - dado, band, None))
    rows = 4
    rh = (dado - y0 - 60) / rows
    for r in range(rows):
        yy = y0 + 40 + r * rh
        off = (r % 2) * 90
        xx = x0 - off
        while xx < x1:
            out.append(rect(xx + 4, yy + 4, 172, rh - 8, block, '#00000022', 2))
            xx += 180
    out.append(rect(x0, y0 + 18, x1 - x0, 16, '#efe2c0', None))
    out.append(rect(x0, dado - 10, x1 - x0, 10, '#efe2c0', None))
    return ''.join(out)

def window(x, y, w, h, lit=False, shutter='#6b4a2b'):
    out = [rect(x, y, w, h, '#f2c05a' if lit else '#2a1e16', INK, 3)]
    out.append(rect(x - w*0.45, y, w*0.42, h, shutter, INK, 2))
    out.append(rect(x + w*1.03, y, w*0.42, h, shutter, INK, 2))
    return ''.join(out)

def insula_facade(x0, x1, top, ground, floors=5, wall='#c78d5c', seed=2, lit=0.0, laundry=True):
    rnd = random.Random(seed)
    out = [rect(x0, top, x1 - x0, ground - top, wall, INK, 3)]
    fh = (ground - top) / floors
    for fl in range(floors):
        yy = top + fl * fh
        out.append(line(x0, yy, x1, yy, '#00000030', 3))
        if fl == floors - 1:
            continue
        n = int((x1 - x0) // 160)
        for i in range(n):
            wx = x0 + 60 + i * 160 + rnd.randint(-8, 8)
            if wx + 50 > x1 - 30: break
            out.append(window(wx, yy + fh * 0.25, 46, fh * 0.45, lit=rnd.random() < lit))
        if fl in (1, 2) and laundry:
            # timber balcony with washing
            bx = x0 + rnd.randint(40, 200)
            bw = min(x1 - bx - 40, rnd.randint(300, 600))
            if bw > 100:
                out.append(rect(bx, yy + fh * 0.78, bw, 12, '#6b4a2b', INK, 2))
                for j in range(int(bw // 40)):
                    out.append(line(bx + j * 40 + 10, yy + fh * 0.78, bx + j * 40 + 10, yy + fh * 0.62, '#6b4a2b', 3))
                out.append(path(f'M{f(bx)},{f(yy + fh*0.5)} Q{f(bx + bw/2)},{f(yy + fh*0.62)} {f(bx + bw)},{f(yy + fh*0.5)}', 'none', '#5a4a3a', 2))
                for j in range(4):
                    cx = bx + bw * (0.15 + j * 0.2)
                    out.append(rect(cx, yy + fh * 0.53 + 4, 34, 46, rnd.choice(['#e8e0cc', '#b8664a', '#7a8aa0', '#d8c070']), INK, 1.5))
    # tile roof edge
    out.append(rect(x0 - 10, top - 18, x1 - x0 + 20, 22, '#a0522d', INK, 3))
    return ''.join(out)

# ------------------------------------------------------------------ nature & props
def cypress(x, base, h, fill='#2f4a2a'):
    return path(f'M{f(x)},{f(base - h)} Q{f(x + h*0.14)},{f(base - h*0.5)} {f(x + h*0.08)},{f(base)} L{f(x - h*0.08)},{f(base)} Q{f(x - h*0.14)},{f(base - h*0.5)} {f(x)},{f(base - h)} Z', fill, INK, 2.5)

def pine(x, base, h, fill='#3e5a34'):
    return (line(x, base, x + h*0.05, base - h*0.8, '#5a3e28', h*0.05) +
            ell(x + h*0.05, base - h*0.85, h*0.38, h*0.13, fill, INK, 2.5))

def olive(x, base, h, fill='#7f8f5f'):
    out = [path(f'M{f(x)},{f(base)} Q{f(x - 10)},{f(base - h*0.3)} {f(x + 8)},{f(base - h*0.55)}', 'none', '#5a4a38', h*0.07)]
    for dx, dy, r in ((-0.22, -0.65, 0.2), (0.2, -0.7, 0.22), (0, -0.85, 0.22), (-0.05, -0.62, 0.18)):
        out.append(circ(x + h*dx, base + h*dy, h*r, fill, INK, 2))
    return ''.join(out)

def sheep(x, y, s=1.0):
    return (ell(x, y, 34*s, 22*s, '#ece6d6', INK, 2) + ell(x + 34*s, y - 6*s, 12*s, 9*s, '#3a3028', INK, 2) +
            line(x - 18*s, y + 18*s, x - 18*s, y + 34*s, INK, 4) + line(x + 16*s, y + 18*s, x + 16*s, y + 34*s, INK, 4))

def mule(x, y, s=1.0, facing=1):
    return (ell(x, y, 70*s, 34*s, '#6b5a4a', INK, 2.5) +
            path(f'M{f(x + facing*55*s)},{f(y - 15*s)} L{f(x + facing*95*s)},{f(y - 70*s)} L{f(x + facing*120*s)},{f(y - 55*s)} L{f(x + facing*80*s)},{f(y)} Z', '#6b5a4a', INK, 2.5) +
            line(x + facing*100*s, y - 72*s, x + facing*92*s, y - 100*s, INK, 5) +
            ''.join(line(x + dx*s, y + 25*s, x + dx*s, y + 80*s, INK, 7) for dx in (-50, -30, 35, 55)) +
            rect(x - 45*s, y - 60*s, 90*s, 34*s, '#9a7a50', INK, 2) +
            ell(x - 30*s, y - 70*s, 16*s, 26*s, '#b0643a', INK, 2) + ell(x + 20*s, y - 70*s, 16*s, 26*s, '#b0643a', INK, 2))

def amphora(x, base, h, fill='#b5653a'):
    return (path(f'M{f(x - h*0.06)},{f(base - h)} L{f(x + h*0.06)},{f(base - h)} L{f(x + h*0.06)},{f(base - h*0.82)} '
                 f'Q{f(x + h*0.3)},{f(base - h*0.6)} {f(x + h*0.04)},{f(base - h*0.05)} L{f(x)},{f(base)} L{f(x - h*0.04)},{f(base - h*0.05)} '
                 f'Q{f(x - h*0.3)},{f(base - h*0.6)} {f(x - h*0.06)},{f(base - h*0.82)} Z', fill, INK, 2.5) +
            path(f'M{f(x - h*0.06)},{f(base - h*0.9)} q{f(-h*0.12)},0 {f(-h*0.12)},{f(h*0.15)}', 'none', INK, 3) +
            path(f'M{f(x + h*0.06)},{f(base - h*0.9)} q{f(h*0.12)},0 {f(h*0.12)},{f(h*0.15)}', 'none', INK, 3))

def table(x0, x1, top, floor, fill='#7a5230'):
    return (rect(x0, top, x1 - x0, 18, fill, INK, 3) +
            rect(x0 + 20, top + 18, 16, floor - top - 18, fill, INK, 2.5) +
            rect(x1 - 36, top + 18, 16, floor - top - 18, fill, INK, 2.5))

def tablet_flat(x, y, s=1.0):
    return (poly([(x - 40*s, y - 8*s), (x + 30*s, y - 14*s), (x + 44*s, y + 6*s), (x - 26*s, y + 12*s)], '#a7804a', INK, 2) +
            poly([(x - 33*s, y - 6*s), (x + 27*s, y - 11*s), (x + 37*s, y + 4*s), (x - 22*s, y + 8*s)], '#3d2f1c', None))

def fire(x, y, s=1.0):
    return (ell(x, y, 160*s, 70*s, 'url(#glow)', None) +
            ''.join(line(x + dx*s, y + 14*s, x - dx*s, y - 6*s, '#4a2e1a', 9) for dx in (-40, 30)) +
            path(f'M{f(x - 30*s)},{f(y + 4*s)} Q{f(x - 26*s)},{f(y - 50*s)} {f(x)},{f(y - 80*s)} Q{f(x + 22*s)},{f(y - 40*s)} {f(x + 30*s)},{f(y + 4*s)} Z', '#f0a030', '#c05a10', 2) +
            path(f'M{f(x - 14*s)},{f(y + 4*s)} Q{f(x - 10*s)},{f(y - 26*s)} {f(x + 2*s)},{f(y - 44*s)} Q{f(x + 12*s)},{f(y - 20*s)} {f(x + 14*s)},{f(y + 4*s)} Z', '#ffe080', None))

def torch(x, y):
    return (rect(x - 6, y, 12, 70, '#4a2e1a', INK, 2) + ell(x, y + 5, 60, 60, 'url(#glow)', None) +
            path(f'M{f(x - 12)},{f(y + 2)} Q{f(x - 8)},{f(y - 30)} {f(x)},{f(y - 44)} Q{f(x + 9)},{f(y - 24)} {f(x + 12)},{f(y + 2)} Z', '#f0a030', '#c05a10', 2))

def nav_arrow(x, y, left=True):
    return ''  # navigation hotspots carry their own labels in the game

# ------------------------------------------------------------------ defs
def defs(sky_top, sky_bot, glow='#ffb040'):
    return f'''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky_top}"/><stop offset="1" stop-color="{sky_bot}"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{glow}" stop-opacity="0.55"/><stop offset="0.5" stop-color="{glow}" stop-opacity="0.18"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>
<radialGradient id="dark"><stop offset="0.35" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.35"/></radialGradient>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="7"/><feColorMatrix type="matrix" values="0 0 0 0 0.16  0 0 0 0 0.1  0 0 0 0 0.05  0 0 0 0.10 0"/></filter>
</defs>'''

def finish(body, sky_top, sky_bot, glow='#ffb040', night=0.0):
    overlay = rect(0, 0, W, H, '#0a1430', None, op=night) if night else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            + defs(sky_top, sky_bot, glow) + body + overlay
            + rect(0, 0, W, H, '#000', None, extra='filter="url(#grain)"') + '</svg>')

# ================================================================== SCENES
def scene_nasica_atrium(P):
    b = []
    b.append(rect(0, 0, W, H, '#c9a36a', None))
    b.append(first_style_wall(0, W, 120, 860))
    # ceiling beams and the opening in the roof
    b.append(rect(0, 0, W, 130, '#5a3a22', INK, 3))
    for i in range(0, W, 140):
        b.append(rect(i, 0, 40, 130, '#4a2e1a', INK, 2))
    cx = X(P['compluvium'][0])
    b.append(rect(cx - 230, 0, 460, 130, 'url(#sky)', INK, 4))
    for sx, sy in ((cx - 90, 50), (cx + 60, 80), (cx + 140, 38)):
        b.append(path(f'M{sx - 18},{sy} q9,-10 18,0 q9,-10 18,0', 'none', INK, 3))
    # sunlight falling into the atrium
    b.append(poly([(cx - 230, 130), (cx + 230, 130), (cx + 330, 860), (cx - 330, 860)], '#fff6d0', None, op=0.13))
    # tablinum opening behind the patron
    tx = X(P['nasica'][0])
    b.append(rect(tx - 260, 200, 520, 660, '#3a2416', INK, 4))
    b.append(path(f'M{tx - 260},{200} Q{tx - 150},{420} {tx - 200},{860} L{tx - 260},{860} Z', '#7a2418', INK, 3))
    b.append(path(f'M{tx + 260},{200} Q{tx + 150},{420} {tx + 200},{860} L{tx + 260},{860} Z', '#7a2418', INK, 3))
    b.append(rect(tx - 120, 300, 240, 140, '#5a3a22', INK, 2))  # shelves of scrolls
    for i in range(8):
        b.append(circ(tx - 95 + i * 27, 340, 11, '#efe2c0', INK, 1.5))
        b.append(circ(tx - 95 + i * 27, 400, 11, '#efe2c0', INK, 1.5))
    # doorway on the right, bright street beyond
    dx = X(P['daos'][0])
    b.append(rect(dx - 60, 180, 200, 680, '#f0e0b0', INK, 4))
    b.append(rect(dx - 60, 180, 200, 40, '#5a3a22', INK, 3))
    # floor
    b.append(rect(0, 860, W, 140, '#9a5a3a', INK, 3))
    rnd = random.Random(4)
    for i in range(500):
        b.append(circ(rnd.uniform(0, W), rnd.uniform(866, 1000), 2.2, '#efe2c0', None, op=0.7))
    for x in range(0, W, 220):
        b.append(line(x, 860, x - 120, 1000, '#00000020', 2))
    # impluvium
    ix, iy = X(P['impluvium'][0]), Y(P['impluvium'][1])
    b.append(poly([(ix - 260, iy - 40), (ix + 260, iy - 40), (ix + 330, iy + 70), (ix - 330, iy + 70)], '#e8dcc0', INK, 4))
    b.append(poly([(ix - 220, iy - 26), (ix + 220, iy - 26), (ix + 280, iy + 54), (ix - 280, iy + 54)], '#7aa0b8', INK, 2))
    b.append(poly([(ix - 120, iy - 20), (ix + 120, iy - 20), (ix + 150, iy + 30), (ix - 150, iy + 30)], '#b8d4e4', None, op=0.6))
    for px, py in ((ix - 60, iy + 10), (ix + 80, iy), (ix + 20, iy + 30)):
        b.append(ell(px, py, 12, 6, '#e07090', INK, 1.5))
    # four columns of the atrium
    for x in (cx - 330, cx + 330):
        b.append(column(x, 140, 870, 70, '#efe2c0', 'doric'))
    # lararium
    lx, ly = X(P['lararium'][0]), Y(P['lararium'][1])
    b.append(rect(lx - 95, ly - 120, 190, 230, '#efe2c0', INK, 3))
    b.append(poly([(lx - 115, ly - 120), (lx, ly - 190), (lx + 115, ly - 120)], '#efe2c0'))
    b.append(rect(lx - 75, ly - 100, 150, 180, '#b8472f', INK, 2))
    for sx in (lx - 38, lx + 38):
        b.append(person(sx, ly + 30, 120, skin='#e0b48c', robe='#e8d070', hair='#2b1d14', arm='raise', facing=1 if sx > lx else -1))
    b.append(path(f'M{lx - 60},{ly + 62} q30,-20 60,0 q30,20 60,0', 'none', '#3f6a2a', 6))
    b.append(rect(lx - 115, ly + 110, 230, 22, '#d8c9a8', INK, 3))
    b.append(rect(lx - 30, ly + 92, 60, 18, '#8a6a48', INK, 2))
    # ancestor masks in cupboards
    mx, my = X(P['imagines'][0]), Y(P['imagines'][1])
    for i in range(4):
        x = mx - 230 + i * 155
        b.append(rect(x - 62, my - 110, 124, 200, '#6b4a2b', INK, 3))
        b.append(rect(x - 52, my - 100, 104, 150, '#2a1a10', INK, 2))
        b.append(ell(x, my - 30, 32, 42, '#e8dcc8', INK, 2))
        b.append(circ(x - 11, my - 38, 4, INK, None) + circ(x + 11, my - 38, 4, INK, None))
        b.append(path(f'M{x - 10},{my - 8} q10,6 20,0', 'none', INK, 2))
        b.append(text(x, my + 72, ['COS', 'CENS', 'COS II', 'IMP'][i], 18, '#efe2c0'))
    b.append(text(mx, my - 125, 'CORNELII SCIPIONES', 22, '#5a3a22', ls=5))
    # the patron and his table
    b.append(auto_person(P['nasica'][0], P['nasica'][1], skin='#e0b48c', robe='#efe8d8', toga='#f3eee2', stripe='#7a1a2a',
                         hair='#8a8580', arm='out', facing=1, k=0.50))
    b.append(table(X(0.205), X(0.415), Y(0.735), 920))
    b.append(tablet_flat(X(P['census_tablet'][0]), Y(P['census_tablet'][1]), 1.2))
    b.append(text(X(P['census_tablet'][0]), Y(P['census_tablet'][1]) + 4, 'CENSVS', 12, '#e8d8b0', ls=1))
    comx, comy = X(P['commission'][0]), Y(P['commission'][1])
    b.append(tablet_flat(comx, comy, 1.3) + line(comx - 30, comy, comx + 34, comy - 6, '#a02020', 4))
    b.append(circ(comx + 4, comy - 3, 9, '#a02020', INK, 2))
    b.append(amphora(X(0.39), Y(0.735), 70, '#c0c0c8'))
    # Pompeius
    b.append(auto_person(P['pompeius'][0], P['pompeius'][1], skin='#d9a679', robe='#efe8d8', toga='#f3eee2', stripe='#7a1a2a',
                         hair='#3d2a1a', bald=True, arm='out', hold='cup', facing=-1, k=0.50))
    # steward
    b.append(auto_person(P['steward'][0], P['steward'][1], skin='#c98f63', robe='#7a8aa0', hair='#c9c4bc', beard=True, hold='tablet', arm='out', facing=-1, k=0.50))
    # figs
    fx, fy = X(P['figs'][0]), Y(P['figs'][1])
    b.append(rect(fx - 70, fy + 10, 140, 14, '#7a5230', INK, 3) + rect(fx - 10, fy + 24, 20, 920 - fy - 24, '#7a5230', INK, 2))
    b.append(ell(fx, fy + 8, 70, 14, '#c8c8d0', INK, 2))
    for i, (ddx, ddy) in enumerate(((-30, -6), (0, -12), (28, -6), (-14, -20), (14, -22))):
        b.append(circ(fx + ddx, fy + ddy, 15, '#5a3060', INK, 2))
    # satchel
    sx, sy = X(P['satchel'][0]), Y(P['satchel'][1])
    b.append(path(f'M{sx - 60},{sy - 30} L{sx + 60},{sy - 30} L{sx + 70},{sy + 40} L{sx - 70},{sy + 40} Z', '#8a6a3a', INK, 3))
    b.append(path(f'M{sx - 40},{sy - 30} Q{sx},{sy - 110} {sx + 40},{sy - 30}', 'none', '#5a3a22', 6))
    b.append(path(f'M{sx + 40},{sy - 26} Q{sx + 90},{sy - 60} {sx + 100},{sy - 20} Z', '#8a7a5a', INK, 2))
    # Daos on his stool
    b.append(person(X(P['daos'][0]), 900, 400, skin='#b07850', robe='#8a7a60', hair='#c9c4bc', beard=True, seated=True, facing=-1))
    b.append(path(f'M{X(P["daos"][0]) - 40},{880} q-40,30 -100,10', 'none', '#6a6a6a', 4))
    return finish(''.join(b), '#7ab0e0', '#cfe6f5')

def scene_forum_day(P):
    b = [rect(0, 0, W, H, 'url(#sky)', None)]
    for cx, cy, s in ((400, 90, 1.0), (1500, 60, 1.4), (2600, 110, 1.1)):
        b.append(ell(cx, cy, 120*s, 30*s, '#ffffff', None, op=0.7) + ell(cx + 70*s, cy - 15*s, 80*s, 28*s, '#ffffff', None, op=0.7))
    # Palatine with houses
    px = X(P['to_palatine'][0])
    b.append(path(f'M{px - 700},{560} Q{px - 400},{150} {px},{160} Q{px + 450},{150} {px + 750},{560} Z', '#9aa070', INK, 3))
    rnd = random.Random(5)
    for i in range(14):
        hx = px - 420 + i * 62 + rnd.randint(-10, 10)
        hy = 200 + abs(i - 7) * 18 + rnd.randint(0, 20)
        b.append(rect(hx, hy, 58, 50, rnd.choice(['#efe2c0', '#e8d0a8', '#dcc8a0']), INK, 2))
        b.append(poly([(hx - 6, hy), (hx + 29, hy - 22), (hx + 64, hy)], '#a0522d', INK, 2))
    for i in range(6):
        b.append(cypress(px - 380 + i * 150, 260 + (i % 2) * 30, 90))
    # Curia
    cx = X(P['curia'][0])
    b.append(rect(cx - 210, 140, 420, 500, '#a8603e', INK, 4))
    b.append(poly([(cx - 230, 140), (cx, 60), (cx + 230, 140)], '#b8704e'))
    b.append(rect(cx - 80, 330, 160, 310, '#7a5a30', INK, 3))
    b.append(rect(cx - 76, 334, 74, 302, '#b08a40', INK, 2) + rect(cx + 2, 334, 74, 302, '#b08a40', INK, 2))
    for yy in range(380, 620, 60):
        b.append(circ(cx - 39, yy, 6, '#6a4a20', None) + circ(cx + 39, yy, 6, '#6a4a20', None))
    for wx in (cx - 170, cx + 110):
        b.append(rect(wx, 200, 60, 90, '#2a1e16', INK, 2))
    b.append(text(cx, 175, 'CVRIA', 34, '#efe2c0', ls=8))
    # portico with graffiti
    gx, gy = X(P['graffiti'][0]), Y(P['graffiti'][1])
    b.append(rect(gx - 210, 330, 420, 400, '#e8dcc0', INK, 3))
    b.append(rect(gx - 230, 300, 460, 40, '#d8c9a8', INK, 3))
    for i in range(5):
        b.append(column(gx - 200 + i * 100, 340, 730, 34, '#efe6d0'))
    b.append(text(gx, gy - 40, 'TI GRACCHE REDDE', 26, '#2a2a2a', font='Comic Sans MS, cursive', ls=1, rot=-3))
    b.append(text(gx, gy, 'AGRVM PVBLICVM', 26, '#2a2a2a', font='Comic Sans MS, cursive', ls=1, rot=-2))
    b.append(text(gx + 10, gy + 40, 'PAVPERIBVS', 26, '#2a2a2a', font='Comic Sans MS, cursive', ls=1, rot=-4))
    b.append(text(gx - 40, gy + 100, 'WE FOVGHT FOR IT', 18, '#5a2a1a', font='Comic Sans MS, cursive', ls=1, rot=5))
    # Temple of Castor and Temple of Saturn
    b.append(temple(X(P['temple_castor'][0]), 640, 380, 560, 6, '#efe6d0', '#a0522d', 'doric', 0.3))
    b.append(temple(X(P['temple_saturn'][0]), 640, 420, 560, 6, '#e8dcc0', '#a0522d', 'ionic', 0.32))
    # gate arch far right
    ax = X(0.975)
    b.append(rect(ax - 110, 260, 220, 400, '#cdbf9f', INK, 4))
    b.append(path(f'M{ax - 70},{660} L{ax - 70},{420} Q{ax},{330} {ax + 70},{420} L{ax + 70},{660} Z', '#9ab0c0', INK, 3))
    # pavement
    b.append(rect(0, 640, W, 360, '#d8ccb0', INK, 3))
    for i in range(0, W, 170):
        b.append(line(i, 640, i - 200, 1000, '#00000018', 3))
    for yy in (700, 780, 880):
        b.append(line(0, yy, W, yy, '#00000018', 3))
    # background crowd
    b.append(crowd(X(0.40), X(0.60), 700, 190, 9, seed=3))
    b.append(crowd(X(0.70), X(0.86), 690, 180, 7, seed=4))
    # Rostra
    rx = X(P['tiberius'][0])
    b.append(rect(rx - 220, 550, 440, 150, '#cdbf9f', INK, 4))
    b.append(rect(rx - 235, 535, 470, 20, '#e8dcc0', INK, 3))
    for i in range(6):
        bx = rx - 190 + i * 76
        b.append(poly([(bx, 590), (bx + 50, 610), (bx, 630)], '#6a7a50', INK, 2.5))
    b.append(text(rx, 680, 'ROSTRA', 20, '#5a4a30', ls=6))
    b.append(chest_person(P['tiberius'][0], P['tiberius'][1], 250, skin='#e0b48c', robe='#efe8d8', toga='#f6f2e8', stripe='#7a1a2a', hair='#3d2a1a', arm='raise', facing=1))
    # tribunes' bench with the empty place
    tx, ty = X(P['octavius_bench'][0]), Y(P['octavius_bench'][1])
    b.append(rect(tx - 160, ty - 10, 320, 26, '#7a5230', INK, 3))
    for lx in (tx - 140, tx - 20, tx + 120):
        b.append(rect(lx, ty + 16, 18, 70, '#7a5230', INK, 2))
    b.append(person(tx - 120, ty + 80, 300, skin='#d9a679', robe='#efe8d8', toga='#f3eee2', stripe='#7a1a2a', hair='#2b1d14', seated=True, facing=1))
    b.append(rect(tx + 30, ty - 30, 90, 20, '#f3eee2', INK, 2, op=0.0))
    # Octavius
    b.append(auto_person(P['octavius'][0], P['octavius'][1], skin='#d9a679', robe='#efe8d8', toga='#f3eee2', stripe='#7a1a2a', hair='#5a4030', facing=-1))
    # Lacus Curtius
    lx, ly = X(P['lacus_curtius'][0]), Y(P['lacus_curtius'][1])
    b.append(ell(lx, ly, 150, 40, '#a89878', INK, 3))
    for i in range(9):
        a = math.pi * i / 8
        b.append(line(lx - 150 * math.cos(a), ly - 10, lx - 150 * math.cos(a), ly - 50 - 0 * math.sin(a), '#5a4a38', 5))
    b.append(path(f'M{lx - 150},{ly - 40} Q{lx},{ly - 70} {lx + 150},{ly - 40}', 'none', '#5a4a38', 5))
    for i in range(6):
        b.append(circ(lx - 60 + i * 24, ly + (i % 2) * 8, 6, '#c8a040', INK, 1.5))
    # country men
    rx2, ry2 = X(P['rustics'][0]), Y(P['rustics'][1])
    b.append(auto_person(P['rustics'][0] - 0.03, P['rustics'][1] + 0.01, skin='#a96f4a', robe='#7a5a3a', hair='#2b1d14', beard=True, facing=1))
    b.append(auto_person(P['rustics'][0], P['rustics'][1], skin='#b07850', robe='#8a6a48', hair='#3d2a1a', beard=True, arm='out', facing=1, hold='staff'))
    b.append(auto_person(P['rustics'][0] + 0.03, P['rustics'][1] + 0.015, skin='#c98f63', robe='#6b5a48', hair='#8a8580', facing=-1))
    # Philo and his table
    phx, phy = X(P['philo'][0]), Y(P['philo'][1])
    b.append(auto_person(P['philo'][0], P['philo'][1], skin='#c98f63', robe='#4a6a8a', hair='#1a1410', beard=True, arm='both', facing=-1))
    b.append(table(phx - 200, phx + 40, phy + 90, Y(0.93)))
    for i in range(5):
        b.append(rect(phx - 180 + i * 24, phy + 60 - i * 3, 18, 30 + i * 3, '#c8a040', INK, 1.5))
    b.append(line(phx - 50, phy + 20, phx - 50, phy + 90, INK, 3) + line(phx - 90, phy + 30, phx - 10, phy + 30, INK, 3))
    b.append(path(f'M{phx - 100},{phy + 50} q10,14 20,0 Z', '#c8a040', INK, 2) + path(f'M{phx - 20},{phy + 50} q10,14 20,0 Z', '#c8a040', INK, 2))
    # man on a barrel
    crx, cry = X(P['crier'][0]), Y(P['crier'][1])
    b.append(ell(crx, Y(0.88), 70, 20, '#7a5230', INK, 3) + rect(crx - 70, Y(0.72), 140, Y(0.88) - Y(0.72), '#8a6038', INK, 3) +
             ell(crx, Y(0.72), 70, 20, '#9a7048', INK, 3) + line(crx - 70, Y(0.78), crx + 70, Y(0.78), INK, 3))
    b.append(person(crx, Y(0.72), 300, skin='#e0b48c', robe='#b05a3a', hair='#5a4030', arm='raise', facing=-1))
    # chickpea boy
    cpx, cpy = X(P['chickpeas'][0]), Y(P['chickpeas'][1])
    b.append(rect(cpx - 50, cpy, 100, 80, '#5a4a3a', INK, 3) + ell(cpx, cpy, 56, 14, '#2a1a10', INK, 2))
    b.append(ell(cpx, cpy - 10, 40, 10, '#f09030', None, op=0.7))
    for i in range(10):
        b.append(circ(cpx - 30 + (i * 7) % 60, cpy - 6 - (i % 3) * 3, 5, '#d8b060', INK, 1))
    b.append(person(cpx + 90, 990, 260, skin='#c98f63', robe='#a08060', hair='#2b1d14', arm='out', facing=-1))
    return finish(''.join(b), '#6fa8dc', '#e6f0f5')

def scene_subura_insula(P):
    b = [rect(0, 0, W, H, 'url(#sky)', None)]
    b.append(insula_facade(-20, W + 20, 60, 760, 5, '#c78d5c', seed=3))
    # crack with props
    kx, ky = X(P['crack'][0]), Y(P['crack'][1])
    b.append(path(f'M{kx},{ky - 140} L{kx + 18},{ky - 80} L{kx - 6},{ky - 30} L{kx + 22},{ky + 30} L{kx},{ky + 90} L{kx + 20},{ky + 150}', 'none', '#2a1a10', 7))
    b.append(line(kx - 120, ky + 220, kx - 10, ky - 20, '#7a5230', 14) + line(kx + 140, ky + 220, kx + 30, ky - 20, '#7a5230', 14))
    # ground floor shops
    for i, x in enumerate(range(80, W, 420)):
        b.append(rect(x, 560, 300, 200, '#3a2416', INK, 3))
        b.append(rect(x - 10, 548, 320, 16, '#7a5230', INK, 2))
    # street ground
    b.append(rect(0, 760, W, 240, '#a08a68', INK, 3))
    rnd = random.Random(9)
    for i in range(140):
        b.append(ell(rnd.uniform(0, W), rnd.uniform(770, 1000), rnd.uniform(6, 16), rnd.uniform(3, 6), '#8a7458', None, op=0.6))
    # crossroads shrine
    cx, cy = X(P['compitum'][0]), Y(P['compitum'][1])
    b.append(rect(cx - 80, cy - 100, 160, 180, '#efe2c0', INK, 3) + poly([(cx - 95, cy - 100), (cx, cy - 160), (cx + 95, cy - 100)], '#efe2c0'))
    b.append(rect(cx - 60, cy - 80, 120, 130, '#b8472f', INK, 2))
    for i in range(6):
        b.append(line(cx - 50 + i * 20, cy - 80, cx - 50 + i * 20, cy - 40 - (i % 3) * 10, '#5a4a3a', 1.5))
        b.append(circ(cx - 50 + i * 20, cy - 34 - (i % 3) * 10, 7, '#e8e0cc', INK, 1.5))
    b.append(rect(cx - 90, cy + 80, 180, 140, '#d8c9a8', INK, 3))
    # Naevia spinning, boy beside her
    nx, ny = X(P['naevia'][0]), Y(P['naevia'][1])
    b.append(rect(nx - 140, 520, 280, 240, '#2a1a10', INK, 3))
    b.append(person(nx, 900, 430, skin='#d9a679', robe='#8a7a6a', hair='#3d2a1a', female=True, seated=True, hold='spindle', arm='out', facing=1))
    b.append(person(nx + 140, 930, 230, skin='#d9a679', robe='#a08060', hair='#3d2a1a', seated=True, facing=-1))
    # grain jar
    gx, gy = X(P['grain_jar'][0]), Y(P['grain_jar'][1])
    b.append(path(f'M{gx - 45},{gy - 100} L{gx + 45},{gy - 100} Q{gx + 85},{gy} {gx + 40},{gy + 100} L{gx - 40},{gy + 100} Q{gx - 85},{gy} {gx - 45},{gy - 100} Z', '#b5653a', INK, 3))
    b.append(ell(gx, gy - 100, 48, 12, '#2a1a10', INK, 2))
    # children with knucklebones
    kx, ky = X(P['knucklebones'][0]), Y(P['knucklebones'][1])
    for i, dx in enumerate((-90, 0, 90)):
        b.append(person(kx + dx, ky + 70, 170, skin=SKINS[i + 1], robe=['#c8a060', '#8aa0b0', '#b07050'][i], hair=HAIR[i], seated=True, facing=1 if dx < 0 else -1))
    for i in range(4):
        b.append(rect(kx - 20 + i * 14, ky + 50, 10, 8, '#efe6d0', INK, 1))
    # Arrius at his table, the tablets, a queue
    ax, ay = X(P['arrius'][0]), Y(P['arrius'][1])
    b.append(crowd(X(0.60), X(0.69), 800, 330, 4, seed=12, tones=['#7a5a3a', '#8a6a48', '#6b5a48', '#9a7a58']))
    b.append(auto_person(P['arrius'][0], P['arrius'][1], skin='#b07850', robe='#8a5a40', hair='#8a8580', beard=True, arm='out', facing=1, hold='tablet'))
    tx, ty = X(P['tribe_lists'][0]), Y(P['tribe_lists'][1])
    b.append(table(ax + 30, tx + 120, ty + 20, 960))
    for i in range(5):
        b.append(tablet_flat(tx - 40 + (i % 3) * 30, ty + 8 - i * 9, 1.0))
    # rent collector
    b.append(auto_person(P['gnaeus'][0], P['gnaeus'][1], skin='#e0b48c', robe='#6a5a3a', hair='#2b1d14', bald=True, arm='out', hold='tablet', facing=-1))
    b.append(line(X(P['gnaeus'][0]) + 70, Y(P['gnaeus'][1]) - 60, X(P['gnaeus'][0]) + 90, 990, '#5a3a22', 8))
    # vote seller leaning on a post
    vx, vy = X(P['vote_seller'][0]), Y(P['vote_seller'][1])
    b.append(rect(vx + 60, 520, 40, 470, '#7a5230', INK, 3))
    b.append(chest_person(P['vote_seller'][0], P['vote_seller'][1], 420, skin='#c98f63', robe='#5a6a4a', hair='#1a1410', arm='out', facing=-1))
    # fullery vats
    fx, fy = X(P['fullery'][0]), Y(P['fullery'][1])
    for dx in (-90, 60):
        b.append(ell(fx + dx, fy + 60, 70, 18, '#7a6a5a', INK, 3) + rect(fx + dx - 70, fy + 60, 140, 70, '#8a7a6a', INK, 3))
    b.append(person(fx - 90, fy + 80, 280, skin='#b07850', robe='#a09070', hair='#2b1d14', arm='both', facing=1))
    # fountain
    wx, wy = X(P['fountain'][0]), Y(P['fountain'][1])
    b.append(rect(wx - 90, wy - 220, 180, 120, '#cdbf9f', INK, 3) + circ(wx, wy - 160, 28, '#a0a0a0', INK, 2))
    b.append(line(wx, wy - 130, wx, wy + 10, '#8ab8d8', 6))
    b.append(rect(wx - 120, wy + 10, 240, 90, '#cdbf9f', INK, 3) + rect(wx - 110, wy + 14, 220, 20, '#8ab8d8', None))
    b.append(rect(wx - 30, wy + 100, 60, 290, '#bcae8e', INK, 3))
    return finish(''.join(b), '#a8c8e0', '#e6ddc8')

def scene_tiburtina_estate(P):
    b = [rect(0, 0, W, H, 'url(#sky)', None)]
    b.append(circ(2300, 120, 60, '#fff2c0', None, op=0.9))
    # distant mountains
    b.append(path('M0,420 L300,260 L560,360 L900,220 L1300,340 L1700,240 L2100,330 L2500,200 L2900,310 L3200,250 L3200,520 L0,520 Z', '#8ea0b8', INK, 2, 0.9))
    b.append(path('M0,470 Q500,360 1000,430 T2000,410 T3200,380 L3200,560 L0,560 Z', '#a8b890', INK, 2))
    # villa hill
    vx = X(P['villa'][0])
    b.append(path(f'M{vx - 900},{560} Q{vx - 300},{230} {vx},{250} Q{vx + 400},{240} {vx + 900},{560} Z', '#9aac70', INK, 3))
    b.append(rect(vx - 230, 180, 460, 110, '#f3eee2', INK, 3) + tiles(vx - 250, 160, 500, 26))
    for i in range(9):
        b.append(column(vx - 200 + i * 50, 200, 290, 16, '#ffffff'))
    b.append(rect(vx + 230, 220, 180, 70, '#efe6d0', INK, 3) + tiles(vx + 220, 204, 200, 20))
    for i in range(4):
        b.append(cypress(vx - 330 + i * 30, 300, 110) + cypress(vx + 440 + i * 34, 300, 100))
    # fields
    b.append(rect(0, 540, W, 460, '#c8b060', None))
    b.append(path('M0,540 Q800,500 1600,540 T3200,530 L3200,1000 L0,1000 Z', '#d0b868', INK, 3))
    for i in range(14):
        y = 560 + i * 32
        b.append(path(f'M{X(0.43)},{y} Q{X(0.62)},{y - 8} {X(0.78)},{y}', 'none', '#b09848', 3))
    # vineyard
    for r in range(7):
        y = Y(0.40) + r * 46
        for i in range(16):
            x = X(0.205) + i * 38 + (r % 2) * 18
            if x > X(0.405): break
            b.append(line(x, y + 30, x, y - 10, '#6b4a2b', 3) + circ(x, y - 12, 16, '#5a7a3a', INK, 1.5))
    # ruined farmhouse
    rx, ry = X(P['ruined_farm'][0]), Y(P['ruined_farm'][1])
    b.append(rect(rx - 120, ry - 50, 240, 140, '#b89a78', INK, 3))
    b.append(poly([(rx - 140, ry - 50), (rx - 40, ry - 120), (rx - 10, ry - 70), (rx + 40, ry - 110), (rx + 60, ry - 50)], '#a0522d', INK, 3))
    b.append(rect(rx - 30, ry + 10, 50, 80, '#2a1a10', INK, 2) + rect(rx + 60, ry - 20, 36, 34, '#2a1a10', INK, 2))
    b.append(path(f'M{rx + 70},{ry - 50} L{rx + 120},{ry - 50} L{rx + 120},{ry + 20}', 'none', '#7a5a40', 6))
    for i in range(8):
        b.append(path(f'M{rx - 110 + i * 30},{ry + 90} l6,-24 l6,24', 'none', '#5a7a3a', 3))
    # old Tullus, fence, olive tree, bean rows
    tx = X(P['old_tullus'][0])
    b.append(olive(tx - 120, Y(0.66), 300))
    for i in range(7):
        b.append(line(tx + 60 + i * 30, Y(0.86), tx + 60 + i * 30, Y(0.78), '#6b4a2b', 6))
    b.append(line(tx + 50, Y(0.80), tx + 260, Y(0.80), '#6b4a2b', 5) + line(tx + 50, Y(0.84), tx + 260, Y(0.84), '#6b4a2b', 5))
    for i in range(4):
        b.append(path(f'M{tx - 180},{Y(0.90) + i * 22} L{tx + 40},{Y(0.90) + i * 22}', 'none', '#4a7a3a', 8))
    b.append(auto_person(P['old_tullus'][0], P['old_tullus'][1], skin='#a96f4a', robe='#8a7a5a', hair='#c9c4bc', beard=True, hold='hoe', arm='out', facing=1))
    # tomb in the vines
    tbx, tby = X(P['old_tomb'][0]), Y(P['old_tomb'][1])
    b.append(rect(tbx - 70, tby - 60, 140, 140, '#cdbf9f', INK, 3) + poly([(tbx - 85, tby - 60), (tbx, tby - 110), (tbx + 85, tby - 60)], '#cdbf9f'))
    b.append(text(tbx, tby - 10, 'OPSII', 18, '#5a4a30') + text(tbx, tby + 20, 'PATER MATER', 12, '#5a4a30', ls=1) + text(tbx, tby + 38, 'FILII', 12, '#5a4a30', ls=1))
    # boundary stone
    bx, by = X(P['boundary_stone'][0]), Y(P['boundary_stone'][1])
    b.append(ell(bx + 120, by + 70, 50, 14, '#a89048', '#8a7038', 3))
    b.append(path(f'M{bx - 45},{by + 80} L{bx - 40},{by - 50} Q{bx},{by - 80} {bx + 40},{by - 50} L{bx + 45},{by + 80} Z', '#cdbf9f', INK, 3))
    b.append(text(bx, by - 15, 'AGER', 18, '#4a3a28') + text(bx, by + 10, 'PVBL', 18, '#4a3a28'))
    b.append(path(f'M{bx + 70},{by + 60} q30,-10 50,4', 'none', '#6a5030', 3))
    # ergastulum
    ex, ey = X(P['ergastulum'][0]), Y(P['ergastulum'][1])
    b.append(rect(ex - 220, ey - 30, 440, 90, '#9a8a70', INK, 3) + tiles(ex - 235, ey - 50, 470, 24, '#8a4a2a'))
    for i in range(7):
        b.append(rect(ex - 190 + i * 60, ey - 15, 26, 10, '#1a1410', None))
    # overseer
    b.append(auto_person(P['damon'][0], P['damon'][1], skin='#c98f63', robe='#4a6a8a', hair='#2b1d14', beard=True, hold='whip', arm='out', facing=1))
    # chain gang
    gx, gy = X(P['chain_gang'][0]), Y(P['chain_gang'][1])
    for i in range(6):
        b.append(person(gx - 200 + i * 80, gy + 130 + (i % 2) * 10, 250, skin=['#a96f4a', '#8d5a3b', '#c98f63', '#b07850', '#a96f4a', '#8d5a3b'][i],
                        robe='#7a6a50', hair=HAIR[i % 3], beard=i % 2 == 0, hold='hoe', arm='out', chained=True, facing=1))
    b.append(path(f'M{gx - 210},{gy + 125} ' + ' '.join(f'Q{gx - 170 + i*80},{gy + 140} {gx - 130 + i*80},{gy + 125}' for i in range(6)), 'none', '#6a6a6a', 4))
    # shepherd and flock
    sx, sy = X(P['syrus'][0]), Y(P['syrus'][1])
    for i, (dx, dy) in enumerate(((-260, 260), (-170, 290), (-90, 250), (120, 280), (200, 260), (-210, 330))):
        b.append(sheep(sx + dx, sy + dy, 1.1))
    b.append(auto_person(P['syrus'][0], P['syrus'][1], skin='#c98f63', robe='#b0a080', hair='#1a1410', hold='crook', arm='out', facing=-1))
    # road and Herius with mules
    b.append(path(f'M{X(0.86)},1000 Q{X(0.93)},700 {X(0.99)},560 L{W},560 L{W},1000 Z', '#bca88a', INK, 3))
    for i in range(10):
        b.append(ell(X(0.92) + i * 26, 980 - i * 40, 22, 10, '#a89478', INK, 1.5))
    hx, hy = X(P['herius'][0]), Y(P['herius'][1])
    b.append(mule(hx - 150, hy + 140, 1.0, facing=-1))
    b.append(auto_person(P['herius'][0], P['herius'][1], skin='#b07850', robe='#7a5a3a', hair='#3d2a1a', beard=True, arm='out', hold='staff', facing=-1))
    # milestone
    mx, my = X(P['estate_back'][0]), Y(P['estate_back'][1])
    b.append(rect(mx - 30, my - 70, 60, 110, '#cdbf9f', INK, 3) + text(mx, my - 30, 'XVI', 18, '#4a3a28'))
    # hare
    hx2, hy2 = X(P['hare'][0]), Y(P['hare'][1])
    b.append(ell(hx2, hy2, 34, 18, '#8a7058', INK, 2) + ell(hx2 + 30, hy2 - 16, 14, 11, '#8a7058', INK, 2) +
             ell(hx2 + 30, hy2 - 42, 5, 18, '#8a7058', INK, 2, rot=-15) + ell(hx2 + 38, hy2 - 40, 5, 18, '#8a7058', INK, 2, rot=10))
    return finish(''.join(b), '#8ab8e0', '#f2e6c0')

def scene_gracchus_house(P):
    b = [rect(0, 0, W, H, '#b8946a', None)]
    b.append(first_style_wall(0, W, 90, 860, base='#c9a36a', band='#3f5a3a', block='#d8c49a'))
    b.append(rect(0, 0, W, 100, '#5a3a22', INK, 3))
    # open to the peristyle garden in the middle
    gx0, gx1 = X(0.49), X(0.77)
    b.append(rect(gx0, 160, gx1 - gx0, 560, 'url(#sky)', INK, 4))
    b.append(rect(gx0, 520, gx1 - gx0, 200, '#6a8a4a', None))
    for i in range(5):
        b.append(cypress(gx0 + 80 + i * 150, 600, 220, '#2f5a2a'))
    b.append(ell((gx0 + gx1) / 2, 650, 160, 30, '#8ab8d8', INK, 2))
    for i in range(5):
        b.append(column(gx0 + i * (gx1 - gx0) / 4, 160, 730, 48, '#efe6d0'))
    # street door, light pouring in
    dx = X(P['dusk_door'][0])
    b.append(rect(dx - 70, 200, 200, 660, '#f0c070', INK, 4))
    b.append(crowd(dx - 50, dx + 110, 820, 220, 3, seed=21))
    b.append(rect(dx - 70, 180, 200, 30, '#5a3a22', INK, 3))
    # floor
    b.append(rect(0, 860, W, 140, '#8a6a4a', INK, 3))
    for x in range(0, W, 90):
        b.append(line(x, 860, x, 1000, '#00000020', 2))
    # Cornelia
    b.append(auto_person(P['cornelia'][0], P['cornelia'][1] + 0.08, skin='#e0b48c', robe='#6a4a6a', hair='#c9c4bc', female=True, seated=True, hold='scroll', arm='out', facing=1, k=0.50))
    b.append(rect(X(P['cornelia'][0]) - 110, Y(0.42), 30, Y(0.92) - Y(0.42), '#5a3a22', INK, 3))
    # jewel box on side table
    jx, jy = X(P['jewel_box'][0]), Y(P['jewel_box'][1])
    b.append(rect(jx - 60, jy + 20, 120, 14, '#7a5230', INK, 3) + rect(jx - 8, jy + 34, 16, 950 - jy - 34, '#7a5230', INK, 2))
    b.append(rect(jx - 34, jy - 8, 68, 28, '#efe6d0', INK, 2) + poly([(jx - 34, jy - 8), (jx - 24, jy - 40), (jx + 44, jy - 40), (jx + 34, jy - 8)], '#efe6d0', INK, 2))
    b.append(rect(jx - 28, jy - 4, 56, 10, '#a02020', None))
    # scribes and the long table with the survey map
    sx = X(P['scribes'][0])
    for i, dx in enumerate((-110, 10, 130)):
        b.append(person(sx + dx, 900, 380, skin=SKINS[i + 2], robe=['#8a7a60', '#a08a6a', '#6a7a8a'][i], hair=HAIR[i], seated=True, facing=1, arm='out'))
    for i in range(4):
        b.append(ell(X(0.21) + i * 40, 940, 34, 20, '#a08050', INK, 2) + circ(X(0.21) + i * 40, 930, 10, '#efe2c0', INK, 1))
    b.append(table(X(0.225), X(0.425), Y(0.70), 930))
    for i in range(5):
        b.append(tablet_flat(sx - 120 + i * 50, Y(0.69), 0.8))
    fx, fy = X(P['forma'][0]), Y(P['forma'][1])
    b.append(poly([(fx - 120, fy - 50), (fx + 100, fy - 50), (fx + 130, fy - 30), (fx - 90, fy - 30)], '#efe2c0', INK, 2))
    b.append(rect(fx - 110, fy - 30, 220, 90, '#efe2c0', INK, 2))
    for i in range(1, 6):
        b.append(line(fx - 110 + i * 37, fy - 30, fx - 110 + i * 37, fy + 60, '#7a6a50', 1.5))
    for i in range(1, 3):
        b.append(line(fx - 110, fy - 30 + i * 30, fx + 110, fy - 30 + i * 30, '#7a6a50', 1.5))
    b.append(rect(fx + 40, fy, 60, 50, 'none', '#c02020', 3))
    # Gaius with the groma
    b.append(auto_person(P['gaius'][0], P['gaius'][1], skin='#e0b48c', robe='#efe8d8', hair='#3d2a1a', arm='out', hold='groma', facing=-1))
    # Blossius
    b.append(auto_person(P['blossius'][0], P['blossius'][1], skin='#d9a679', robe='#5a6a8a', hair='#8a8580', beard=True, hold='scroll', arm='out', facing=1))
    # reading stand with the Stoic scroll
    rx, ry = X(P['stoic_scroll'][0]), Y(P['stoic_scroll'][1])
    b.append(line(rx, ry + 10, rx, 930, '#5a3a22', 8) + line(rx - 40, 930, rx + 40, 930, '#5a3a22', 8))
    b.append(poly([(rx - 70, ry - 20), (rx + 70, ry - 30), (rx + 76, ry + 10), (rx - 64, ry + 20)], '#efe2c0', INK, 2))
    b.append(text(rx, ry, 'ΜΟΝΟΣ Ο ΣΟΦΟΣ', 13, '#3a2a1a', ls=1, rot=-4))
    # Diophanes
    b.append(auto_person(P['diophanes'][0], P['diophanes'][1], skin='#c98f63', robe='#7a8a5a', hair='#1a1410', beard=True, hold='tablet', arm='out', facing=-1))
    # mural crown in its niche
    cx, cy = X(P['mural_crown'][0]), Y(P['mural_crown'][1])
    b.append(path(f'M{cx - 110},{cy + 90} L{cx - 110},{cy - 40} Q{cx},{cy - 140} {cx + 110},{cy - 40} L{cx + 110},{cy + 90} Z', '#3a2416', INK, 3))
    b.append(rect(cx - 120, cy + 90, 240, 18, '#efe2c0', INK, 3))
    b.append(ell(cx, cy + 50, 60, 16, '#d4a830', INK, 2) + rect(cx - 60, cy + 10, 120, 40, '#e8c040', INK, 2))
    for i in range(5):
        b.append(rect(cx - 56 + i * 25, cy - 8, 16, 20, '#e8c040', INK, 2))
    # chest from Pergamum
    px, py = X(P['pergamum_chest'][0]), Y(P['pergamum_chest'][1])
    b.append(rect(px - 110, py - 30, 220, 120, '#8a5a30', INK, 3) + rect(px - 116, py - 50, 232, 30, '#9a6a3a', INK, 3))
    for dx in (-90, 70):
        b.append(rect(px + dx, py - 50, 20, 140, '#b08a40', INK, 2))
    for i in range(8):
        a = i * math.pi / 4
        b.append(line(px, py + 30, px + 26 * math.cos(a), py + 30 + 26 * math.sin(a), '#e8c040', 4))
    b.append(circ(px - 40, py - 62, 12, '#efe2c0', INK, 1.5) + circ(px + 20, py - 64, 12, '#efe2c0', INK, 1.5))
    # Claudia and the boy
    b.append(auto_person(P['claudia'][0], P['claudia'][1], skin='#e0b48c', robe='#8a5a5a', hair='#3d2a1a', female=True, arm='out', facing=-1))
    b.append(person(X(P['claudia'][0]) - 80, 960, 200, skin='#e0b48c', robe='#efe8d8', hair='#3d2a1a', arm='raise', facing=1))
    return finish(''.join(b), '#8ab8e0', '#e8f0e0')

def scene_vigil_night(P):
    b = [rect(0, 0, W, H, 'url(#sky)', None)]
    rnd = random.Random(11)
    for i in range(160):
        b.append(circ(rnd.uniform(0, W), rnd.uniform(0, 420), rnd.uniform(1, 3), '#ffffff', None, op=rnd.uniform(0.3, 0.9)))
    mx, my = X(P['moon_stars'][0]), Y(P['moon_stars'][1])
    b.append(circ(mx, my, 46, '#f4ecd0', None) + circ(mx + 18, my - 6, 42, '#1c2848', None))
    # Capitol on the right
    cx = X(P['night_capitol'][0])
    b.append(path(f'M{cx - 520},{560} Q{cx - 260},{250} {cx},{280} Q{cx + 200},{270} {W + 20},{330} L{W + 20},{560} Z', '#26304a', INK, 3))
    b.append(temple(cx, 300, 300, 200, 6, '#9aa0b8', '#5a4a5a', 'doric', 0.2, door=False))
    b.append(temple(cx - 330, 370, 120, 90, 4, '#8a90a8', '#4a3a4a', 'ionic', 0.2))
    b.append(rect(cx - 352, 330, 44, 32, '#ffd070', None, op=0.9))
    # houses along the street
    b.append(insula_facade(-20, X(0.36), 220, 780, 4, '#5a4a48', seed=5, lit=0.25, laundry=False))
    b.append(insula_facade(X(0.56), X(0.84), 240, 780, 4, '#544848', seed=6, lit=0.2, laundry=False))
    # the house of the Gracchi with its lit door
    hx = X(P['tiberius_door'][0])
    b.append(rect(X(0.36), 300, X(0.56) - X(0.36), 480, '#6a5a50', INK, 3) + tiles(X(0.355), 280, X(0.565) - X(0.355), 26, '#4a2a1a'))
    b.append(ell(hx, 640, 300, 260, 'url(#glow)', None))
    b.append(rect(hx - 110, 420, 220, 360, '#f0b050', INK, 4))
    b.append(rect(hx - 130, 400, 260, 26, '#3a2a20', INK, 3))
    b.append(torch(hx - 180, 470) + torch(hx + 180, 470))
    # street
    b.append(rect(0, 780, W, 220, '#3a3430', INK, 3))
    for i in range(0, W, 120):
        b.append(ell(i + (i % 240) * 0.2, 840 + (i % 360) / 4, 50, 14, '#4a443e', None))
    # sleepers and fires
    fx, fy = X(P['campfire_men'][0]), Y(P['campfire_men'][1])
    b.append(fire(fx, fy + 70, 1.1))
    for dx, dy in ((-220, 120), (180, 140), (-120, 190)):
        b.append(ell(fx + dx, fy + dy, 110, 30, '#5a4a3a', INK, 3) + circ(fx + dx - 100, fy + dy - 10, 22, '#a96f4a', INK, 2))
    b.append(person(fx + 120, 950, 330, skin='#a96f4a', robe='#6a5a48', hair='#2b1d14', beard=True, seated=True, facing=-1))
    b.append(fire(X(0.79), Y(0.86), 0.9))
    # crowd in the street
    b.append(crowd(X(0.33), X(0.40), 820, 280, 3, seed=31, tones=['#5a4a3a', '#6a5a48', '#4a4038']))
    b.append(crowd(X(0.66), X(0.72), 820, 280, 3, seed=32, tones=['#5a4a3a', '#6a5a48', '#4a4038']))
    # Arrius
    b.append(auto_person(P['arrius_vigil'][0], P['arrius_vigil'][1], skin='#b07850', robe='#8a5a40', hair='#8a8580', beard=True, arm='out', hold='tablet', facing=1))
    # Tiberius in mourning with his son
    b.append(chest_person(P['tiberius_door'][0], P['tiberius_door'][1], 470, skin='#e0b48c', robe='#4a4440', toga='#5a5450', hair='#3d2a1a', arm='out', facing=1))
    b.append(chest_person(P['the_son'][0], P['the_son'][1], 230, skin='#e0b48c', robe='#efe8d8', toga='#f3eee2', stripe='#7a1a2a', hair='#3d2a1a', arm='raise', facing=-1))
    # the helmet
    hmx, hmy = X(P['helmet'][0]), Y(P['helmet'][1])
    b.append(path(f'M{hmx - 50},{hmy + 30} Q{hmx - 55},{hmy - 50} {hmx},{hmy - 55} Q{hmx + 55},{hmy - 50} {hmx + 50},{hmy + 30} Z', '#8a7a50', INK, 3))
    b.append(line(hmx, hmy - 55, hmx, hmy - 90, '#a02020', 10))
    b.append(path(f'M{hmx + 40},{hmy + 30} q30,-10 50,10 q-20,10 -40,0', 'none', '#4a6a3a', 5))
    # Villius, Calvus, Naevia
    b.append(auto_person(P['villius'][0], P['villius'][1], skin='#c98f63', robe='#6a5a48', hair='#2b1d14', beard=True, arm='head', facing=-1))
    b.append(auto_person(P['calvus'][0], P['calvus'][1], skin='#e0b48c', robe='#b8a888', hair='#5a4030', arm='raise', hold='cup', facing=-1))
    nx, ny = X(P['naevia_vigil'][0]), Y(P['naevia_vigil'][1])
    b.append(rect(nx - 160, 760, 320, 30, '#5a5048', INK, 3))
    b.append(person(nx, 900, 400, skin='#d9a679', robe='#5a5048', hair='#3d2a1a', female=True, seated=True, facing=-1))
    b.append(ell(nx + 90, 885, 90, 28, '#8a7a5a', INK, 2) + circ(nx + 10, 870, 24, '#d9a679', INK, 2))
    return finish(''.join(b), '#0c1630', '#2a3a60', glow='#ff9a30', night=0.22)

def scene_fides_night(P):
    b = [rect(0, 0, W, H, '#2a2018', None)]
    # dawn opening on the right
    dx = X(0.80)
    b.append(rect(dx, 0, W - dx, 820, 'url(#sky)', None))
    b.append(circ(X(P['dawn'][0]) + 60, Y(P['dawn'][1]) + 90, 70, '#ffd890', None, op=0.6))
    b.append(path(f'M{dx},{560} Q{dx + 200},{460} {dx + 400},{500} T{W},{470} L{W},{820} L{dx},{820} Z', '#4a4858', INK, 3))
    b.append(temple(X(0.93), 620, 280, 220, 6, '#b8b0b8', '#6a4a4a', 'doric', 0.2, door=False))
    b.append(crowd(dx + 40, W - 40, 760, 110, 12, seed=41, tones=['#6a6070', '#7a7080', '#5a5060', '#9a90a0']))
    # inner wall and ceiling
    b.append(rect(0, 0, dx, 820, '#4a3a2c', INK, 3))
    b.append(first_style_wall(0, dx, 120, 820, base='#5a4532', band='#3a2418', block='#6a5240'))
    b.append(rect(0, 0, W, 110, '#2a1a10', INK, 3))
    # lamps' glow
    for lx in (X(0.18), X(0.52), X(0.70)):
        b.append(ell(lx, 520, 360, 300, 'url(#glow)', None))
    # Fides
    fx, fy = X(P['fides_statue'][0]), Y(P['fides_statue'][1])
    b.append(rect(fx - 120, 640, 240, 180, '#8a7a6a', INK, 3) + text(fx, 740, 'FIDES', 30, '#2a1a10', ls=10))
    b.append(person(fx, 640, 520, skin='#c8c0b0', robe='#bcb4a4', toga=None, hair='#aaa298', female=True, arm='out', facing=1))
    # floor
    b.append(rect(0, 820, W, 180, '#5a4a3a', INK, 3))
    for x in range(0, W, 160):
        b.append(line(x, 820, x - 60, 1000, '#00000030', 2))
    # columns of the pronaos
    for x in (X(0.08), X(0.30), X(0.62), X(0.80)):
        b.append(column(x, 110, 830, 80, '#9a8a74', 'ionic', '#7a6a58'))
    # Scaevola, seated by a lamp
    sx = X(P['scaevola'][0])
    b.append(rect(sx - 220, 800, 440, 30, '#6b4a2b', INK, 3))
    b.append(person(sx, 930, 430, skin='#e0b48c', robe='#efe8d8', toga='#f3eee2', stripe='#7a1a2a', hair='#c9c4bc', bald=True, seated=True, facing=1, arm='out'))
    b.append(rect(sx + 150, 740, 18, 60, '#c8a040', INK, 2) + ell(sx + 159, 730, 30, 12, '#c8a040', INK, 2) + ell(sx + 175, 712, 12, 22, '#ffd070', None))
    # bench with Pompeius' speech
    px, py = X(P['pompeius_tablet'][0]), Y(P['pompeius_tablet'][1])
    b.append(rect(px - 120, py + 14, 240, 20, '#6b4a2b', INK, 3) + rect(px - 100, py + 34, 16, 960 - py - 34, '#6b4a2b', INK, 2) + rect(px + 84, py + 34, 16, 960 - py - 34, '#6b4a2b', INK, 2))
    b.append(tablet_flat(px, py, 1.2))
    # clubs
    cx, cy = X(P['clubs'][0]), Y(P['clubs'][1])
    rnd = random.Random(3)
    for i in range(16):
        a = rnd.uniform(-0.5, 0.5)
        x0 = cx - 150 + i * 18
        b.append(line(x0, cy + 70, x0 + 180 * math.sin(a), cy + 70 - 170 * math.cos(a), rnd.choice(['#7a5230', '#6b4a2b', '#8a6038']), 18))
    for i in range(5):
        b.append(line(cx - 150 + i * 60, cy + 90, cx - 40 + i * 60, cy + 50, '#5a3a22', 20))
    # table with the informer's note and the ledger
    b.append(table(X(0.40), X(0.66), Y(0.73), 960, '#5a3a22'))
    ix, iy = X(P['informer_note'][0]), Y(P['informer_note'][1])
    b.append(tablet_flat(ix, iy + 10, 1.0) + circ(ix + 30, iy + 4, 8, '#a02020', INK, 1.5))
    lx, ly = X(P['nasica_ledger'][0]), Y(P['nasica_ledger'][1])
    b.append(poly([(lx - 70, ly - 50), (lx + 60, ly - 56), (lx + 74, ly - 34), (lx - 56, ly - 28)], '#7a2a1a', INK, 2))
    b.append(rect(lx + 80, Y(0.62), 16, Y(0.73) - Y(0.62), '#c8a040', INK, 2) + ell(lx + 88, Y(0.615), 26, 10, '#c8a040', INK, 2) + ell(lx + 100, Y(0.595), 10, 18, '#ffd070', None))
    b.append(poly([(lx - 230, Y(0.73)), (lx - 120, Y(0.725)), (lx - 110, Y(0.705)), (lx - 220, Y(0.71))], '#efe8d8', INK, 2))
    # Satureius with a bench leg
    b.append(auto_person(P['satureius'][0], P['satureius'][1], skin='#d9a679', robe='#efe8d8', toga='#f3eee2', hair='#2b1d14', arm='out', hold='club', facing=-1))
    # slaves carrying in staves, silhouettes
    b.append(person(X(0.76), 900, 360, skin='#8d5a3b', robe='#5a3a3a', hair='#1a1410', arm='both', hold='club', facing=-1))
    # geese
    gx, gy = X(P['sacred_geese'][0]), Y(P['sacred_geese'][1])
    for i in range(0, 7):
        b.append(line(gx - 160 + i * 52, gy - 60, gx - 160 + i * 52, gy + 60, '#6b4a2b', 5))
    b.append(line(gx - 170, gy - 50, gx + 170, gy - 50, '#6b4a2b', 5))
    for dx in (-80, 30):
        b.append(ell(gx + dx, gy + 20, 44, 26, '#efece4', INK, 2) + path(f'M{gx + dx + 34},{gy + 10} q14,-30 4,-56', 'none', '#efece4', 12) +
                 circ(gx + dx + 40, gy - 48, 11, '#efece4', INK, 2) + poly([(gx + dx + 50, gy - 50), (gx + dx + 70, gy - 44), (gx + dx + 50, gy - 40)], '#e09030', INK, 1.5))
    return finish(''.join(b), '#3a3a6a', '#f0b080', glow='#ffb050', night=0.12)

SCENES = {
    'nasica_atrium': scene_nasica_atrium, 'forum_day': scene_forum_day, 'subura_insula': scene_subura_insula,
    'tiburtina_estate': scene_tiburtina_estate, 'gracchus_house': scene_gracchus_house,
    'vigil_night': scene_vigil_night, 'fides_night': scene_fides_night,
}

def main():
    data = json.loads(subprocess.check_output(['node', os.path.join(ROOT, 'tools', 'dump_scenes.js'), os.path.join(ROOT, 'index.html')]))
    os.makedirs(os.path.join(ROOT, 'art'), exist_ok=True)
    for s in data:
        fn = SCENES.get(s['id'])
        if not fn or not s['image'].endswith('.svg'):
            continue
        P = {h['id']: (h['x'], h['y']) for h in s['hotspots']}
        svg = fn(P)
        out = os.path.join(ROOT, s['image'])
        with open(out, 'w') as fh:
            fh.write(svg)
        print(f'{out}: {len(svg)//1024} KB')

if __name__ == '__main__':
    main()
