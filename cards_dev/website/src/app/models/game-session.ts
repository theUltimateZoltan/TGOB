import { Player } from "./player"
import { Round } from "./round"

type Phase = 'enrollment' | 'in_progress' | 'complete'

export class GameSession {
    connection_request: string
    players: Array<Player>
    phase: Phase
    joinCode: string
    round: Round | null
    complete: boolean
    is_coordinator: boolean

    constructor(json_object: any){
        this.players = json_object.players
        this.phase = json_object.phase
        this.joinCode = json_object.session_id
        this.round = null
        this.complete = false
        this.connection_request = json_object.connection_request
        this.is_coordinator = json_object.is_coordinator
        console.log(`Successfuly initialized game session: ${JSON.stringify(this)}`)
    }
}
