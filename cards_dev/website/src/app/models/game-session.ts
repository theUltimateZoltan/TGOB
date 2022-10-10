import { Phase } from "./phase"
import { Player } from "./player"
import { Round } from "./round"

export class GameSession {
    connection_request: string
    players: Array<Player>
    phase: Phase
    joinCode: string
    round: Round | null
    complete: boolean

    constructor(json_object: any){
        this.players = json_object.players
        this.phase = json_object.phase
        this.joinCode = json_object.session_id
        this.round = null
        this.complete = false
        this.connection_request = json_object.connection_request
        console.log(`Successfuly initialized game session: ${JSON.stringify(this)}`)
    }
}
