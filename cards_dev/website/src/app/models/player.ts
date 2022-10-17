
export class Player {
    name: string
    email: string
    connection_id: string | undefined

    constructor(email: string, name: string) {
        this.email = email
        this.name = name
    }

    set_connection_id(connection: string) {
        this.connection_id = connection
    }
}