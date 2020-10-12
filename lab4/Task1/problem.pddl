(define (problem shacketys-prob)

(:domain shacketys-world)

;  Below is a graphic representation of the initial states in the domain
; lightswitch = ls
; wide door = two spaces
; narrow door = one space
;
;|--------------|---------------|---------------|
;|   (room 1)   |   (room 2)    |    (room 3)   |
;|    ls: off   |    ls: off    |     ls: off   |
;|   Shackety          box                      |
;|                              |               |
;|              |               |               |
;|----      ----|---------------|---------------|
;|              | 
;|              | 
;|              |
;|   (room 4)   | 
;|   ls: off    |
;|--------------|


(:objects
    r1 r2 r3 r4 - room              ; Four rooms in the world 
    ls1 ls2 ls3 ls4 - lightSwitch   ; One lightswitch per room
    b - box                         ; One box in the world
    s - shackety
)

(:init
    ; World layout as depicted above
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
    (wideDoor r1 r2)
    (wideDoor r1 r4)
)

; The goal is to have all the lights turned on
(:goal
    (and
        (lightsAreOn ls1)
        (lightsAreOn ls2)
        (lightsAreOn ls3)
        (lightsAreOn ls4)
    )
)
)
