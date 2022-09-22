import { Phase } from "./phase"
import { Player } from "./player"
import { QuestionCard } from "./question-card"
import { Round } from "./round"

export class GameSession {
    players: Array<Player>
    phase: Phase
    joinCode: string
    round: Round
    complete: boolean

    constructor(session_id: string){
        // access api gw

        this.players = []
        this.phase = Phase.enrollment
        this.joinCode = this.generateJoinCode()
        this.round = this.generateRound()
        this.complete = false
    }

    private generateJoinCode(): string {
        return "samplejoincode"
    }

    private generateRound(): Round{
        var questionCard: QuestionCard = new QuestionCard("sample")
        var arbiter: Player | undefined = this.players.at(0)

        if (arbiter != undefined){
            return new Round(questionCard, arbiter)
        }else{
            throw new Error("This is somehow a game with no Players.")
        }
    }

    
}
