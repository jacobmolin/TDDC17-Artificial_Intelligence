(define (problem shacketys-prob)

(:domain shacketys-world)

(:objects
    r1 r2 r3 r4 - room
    ls1 ls2 ls3 ls4 - lightSwitch
    b - box
    s - shackety
)

(:init
    (adjacent    r1 r2)
    (adjacent    r1 r4)
    (adjacent    r2 r3)
    (at          s r1)
    (attached    ls1 r1)
    (attached    ls2 r2)
    (attached    ls3 r3)
    (attached    ls4 r4)
    (lightsAreOn ls3)
    (placed      b r2)
    (wideOpening r1 r2)
    (wideOpening r1 r4)
)

(:goal
    (and
        (lightsAreOn ls1)
        (lightsAreOn ls2)
        (lightsAreOn ls3)
        (lightsAreOn ls4)
    )
)
)
