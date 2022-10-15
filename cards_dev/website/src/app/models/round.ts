import { Player } from "./player";

export class Round {
    question_card: string
    arbiter: Player
    winner: Player | null
    winning_card: string | undefined
    answer_cards_suggested: Array<string>

    constructor(json_object: any){
        console.log(`parsing round from json object: ${JSON.stringify(json_object)}`)
        this.question_card = json_object.question_card
        this.arbiter = json_object.arbiter
        this.winner = json_object.winner
        this.answer_cards_suggested = json_object.answer_cards_suggested
        const winning_card_index: number | null = json_object.winning_answer_index
        if (winning_card_index) {
            this.winning_card = this.answer_cards_suggested[winning_card_index]
        }
    }
}
