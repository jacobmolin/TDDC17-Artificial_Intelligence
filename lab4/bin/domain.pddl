(define (domain shacketys-world)

    (:requirements
        :strips 
        :typing 
        :adl
        :equality
    )

    (:types
        room
        lightSwitch
        box
        shackety
    )

    (:predicates
        (adjacent    ?r1 ?r2 - room)                ; room1 is next to room2
        (at          ?s - shackety ?r - room)        ; shackety is in room
        (attached    ?ls - lightSwitch ?r - room)   ; there is a lightswitch in room
        (placed      ?b - box ?r - room)            ; the box is placed in a room.
        (wideOpening ?r1 ?r2 - room)      ; there is a wide door in the room
        (lightsAreOn ?ls - lightSwitch)             ; the lightSwitch in the room is on
    )

    (:action move
        :parameters (?s - shackety ?start ?end - room) 
        :precondition (and (or (adjacent ?start ?end) (adjacent ?end ?start)) (at ?s ?start))
        :effect (and (at ?s ?end) (not (at ?s ?start)))
    )

    (:action turnLightsOn
        :parameters (?s - shackety ?b - box ?ls - lightSwitch ?r - room) 
        :precondition (and (at ?s ?r) (placed ?b ?r) (attached ?ls ?r) (not (lightsAreOn ?ls)))
        :effect (lightsAreOn ?ls)
    )

    (:action moveWithBox
        :parameters (?s - shackety ?b - box ?start ?end - room) 
        :precondition (
            and
            (at ?s ?start)
            (placed ?b ?start)
            (or (adjacent ?start ?end) (adjacent ?end ?start))
            (or (wideOpening ?start ?end) (wideOpening ?end ?start))
        )
        :effect (and (at ?s ?end) (not (at ?s ?start)) (placed ?b ?end) (not (placed ?b ?start)))
    )
)