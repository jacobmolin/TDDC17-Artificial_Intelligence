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
        (adjacent    ?r1 ?r2 - room)                  ; room1 is next to room2
        (at          ?s - shackety ?r - room)           ; shackety is in room
        (attached    ?ls - lightSwitch ?r - room)       ; there is a lightswitch in the room
        (placed      ?b - box ?r - room)       ; the box is placed in the room.
        (wideDoor ?r1 ?r2 - room)                    ; there is a wide door connecting the rooms
        (lightsAreOn ?ls - lightSwitch)           ; the lightSwitch in the room is on
    )

    (:action move
        :parameters (?s - shackety ?start ?end - room)
        ; Only move if the rooms are adjacent and Shackety is in the start room
        :precondition (and (or (adjacent ?start ?end) (adjacent ?end ?start)) (at ?s ?start))
        ; Move Shakety from start to end room
        :effect (and (at ?s ?end) (not (at ?s ?start)))
    )

    (:action turnLightsOn
        :parameters (?s - shackety ?b - box ?ls - lightSwitch ?r - room) 
        ; Only turn the light on if Shackety is in the room, 
        ; the box is placed in the room, there is a light switch in the room
        ; and the light is not already on
        :precondition (and (at ?s ?r) (placed ?b ?r) (attached ?ls ?r) (not (lightsAreOn ?ls)))
        ; Turn lights on in the room
        :effect (lightsAreOn ?ls)
    )

    (:action moveWithBox
        :parameters (?s - shackety ?b - box ?start ?end - room)
        ; Only push the box if the rooms are adjacent, the box is in the start room,
        ; Shackety is in the start room and there is wide door connecting the rooms
        :precondition (
            and
            (at ?s ?start)
            (placed ?b ?start)
            (or (adjacent ?start ?end) (adjacent ?end ?start))
            (or (wideDoor ?start ?end) (wideDoor ?end ?start))
        )
        ; Move Shackety and the box from start to end room
        :effect (and (at ?s ?end) (not (at ?s ?start)) (placed ?b ?end) (not (placed ?b ?start)))
    )
)