export class ConnectionRequest {
    body: string
    is_coordinator: boolean

    constructor(body: string, is_coordinator: boolean) {
        this.body = body
        this.is_coordinator = is_coordinator
    }

}
