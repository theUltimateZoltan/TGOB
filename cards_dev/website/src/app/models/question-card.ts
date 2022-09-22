import { AnswerCard } from "./answer-card"

export class QuestionCard {
    id: string
    text: string
    static placeholder: string= "{ph}"

    constructor(id: string){
        this.id = id
        this.text = "sample text {ph} " + this.id
    }

    interpolate(answer: AnswerCard): string{
        return this.text.replace(QuestionCard.placeholder, answer.getText())
    }
}
