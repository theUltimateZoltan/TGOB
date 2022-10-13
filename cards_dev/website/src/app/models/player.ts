import jwt_decode from 'jwt-decode';

export class Player {
    id_jwt: string
    name: string
    email: string

    constructor(identity_token: string) {
        this.id_jwt = identity_token
        const user_details: any = jwt_decode(this.id_jwt)
        this.name = user_details.name
        this.email = user_details.email
    }

}