import { json } from "stream/consumers"
import { Phase } from "./phase"
import { Player } from "./player"
import { QuestionCard } from "./question-card"
import { Round } from "./round"

export class GameSession {
    players: Array<Player>
    phase: Phase
    joinCode: string
    round: Round | null
    complete: boolean

    constructor(json_object: any){
        console.log(json_object.toString())
        this.players = json_object.players
        this.phase = json_object.phase
        this.joinCode = json_object.session_id
        this.round = null
        this.complete = false
    }
}
