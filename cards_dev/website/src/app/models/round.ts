import { AnswerCard } from "./answer-card";
import { Player } from "./player";
import { QuestionCard } from "./question-card";

export class Round {
    questionCard: QuestionCard
    arbiter: Player
    winner: Player | null
    winningCard: AnswerCard | null

    constructor(questionCard: QuestionCard, arbiter: Player){
        this.questionCard = questionCard
        this.arbiter = arbiter
        this.winner = null
        this.winningCard = null
    }
}
