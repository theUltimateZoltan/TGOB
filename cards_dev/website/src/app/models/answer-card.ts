export class AnswerCard {
    id: string
    text: string

    constructor(id: string){
        this.id = id
        this.text = "some fixed text"
    }

    getText(): string{
        return this.text
    }
}
