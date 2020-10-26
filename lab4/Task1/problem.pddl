(define (problem shacketys-prob)

    (:domain shacketys-world)

    ;  Below is a graphic representation of the initial states in the domain
    ; lightswitch = ls
    ; wide door = two spaces
    ; narrow door = one space
    ;
    ;|--------------|---------------|---------------|
    ;|   (room 1)   |   (room 2)    |    (room 3)   |
    ;|    ls: off   |    ls: off    |     ls: on    |
    ;|   Shackety          box                      |
    ;|                              |               |
    ;|   o1 o2      |     o5        |               |
    ;|----      ----|---------------|---------------|
    ;|              | 
    ;|   o3 o4      | 
    ;|              |
    ;|   (room 4)   | 
    ;|   ls: off    |
    ;|--------------|


    (:objects
        r1 r2 r3 r4 - room              ; Four rooms in the world 
        ls1 ls2 ls3 ls4 - lightSwitch   ; One lightswitch per room
        b - box                         ; One box in the world
        o1 o2 o3 o4 o5 - smallObject    ; Five small objects
        s - shackety
        gL gR - grip                    ; One left and one right grip
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
        (objectPlaced o1 r1)
        (objectPlaced o2 r1)
        (objectPlaced o3 r4)
        (objectPlaced o4 r4)
        (objectPlaced o5 r2)
    )

    ; The goal is to have all small objects in room 3
    (:goal
        (and
            (objectPlaced o1 r3)
            (objectPlaced o2 r3)
            (objectPlaced o3 r3)
            (objectPlaced o4 r3)
            (objectPlaced o5 r3)
        )
    )
)